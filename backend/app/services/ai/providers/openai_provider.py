"""
OpenAI Provider Implementation
Supports GPT-4, GPT-3.5-turbo, and text-embedding-ada-002
"""
import asyncio
import logging
from typing import List, Optional, Dict, Any
import json
import time

from ..llm_service import AbstractLLMProvider, LLMResponse, LLMUsage, LLMMessage, LLMProvider

logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. Install with: pip install openai")


class OpenAIProvider(AbstractLLMProvider):
    """OpenAI LLM Provider"""
    
    # Pricing per 1K tokens (as of 2024)
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "text-embedding-ada-002": {"input": 0.0001, "output": 0}
    }
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo", **kwargs):
        super().__init__(api_key, model, **kwargs)
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed")
        
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.embedding_model = kwargs.get("embedding_model", "text-embedding-ada-002")
        self.max_retries = kwargs.get("max_retries", 3)
        self.timeout = kwargs.get("timeout", 30)
        
        logger.info(f"Initialized OpenAI provider with model: {model}")
    
    async def generate(
        self,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate response using OpenAI API"""
        start_time = time.time()
        
        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            openai_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Prepare request parameters
        request_params = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 1500,
            "timeout": self.timeout
        }
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key in ["top_p", "frequency_penalty", "presence_penalty", "stop"]:
                request_params[key] = value
        
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                response = await self.client.chat.completions.create(**request_params)
                
                # Extract response data
                content = response.choices[0].message.content
                usage_data = response.usage
                
                # Calculate usage and cost
                usage = LLMUsage(
                    prompt_tokens=usage_data.prompt_tokens,
                    completion_tokens=usage_data.completion_tokens,
                    total_tokens=usage_data.total_tokens,
                    estimated_cost=self.calculate_cost_from_usage(usage_data),
                    provider=LLMProvider.OPENAI,
                    model=self.model
                )
                
                # Determine confidence (simple heuristic based on response length and token usage)
                confidence = min(0.9, len(content) / 1000) if content else 0.1
                
                return LLMResponse(
                    content=content,
                    usage=usage,
                    confidence=confidence,
                    provider=LLMProvider.OPENAI,
                    model=self.model,
                    response_time=time.time() - start_time,
                    metadata={
                        "finish_reason": response.choices[0].finish_reason,
                        "model_used": response.model
                    }
                )
                
            except openai.RateLimitError as e:
                logger.warning(f"OpenAI rate limit hit, retrying in {2 ** retries} seconds")
                await asyncio.sleep(2 ** retries)
                retries += 1
                last_error = e
                
            except openai.APIError as e:
                logger.error(f"OpenAI API error: {str(e)}")
                retries += 1
                last_error = e
                if retries < self.max_retries:
                    await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Unexpected error with OpenAI: {str(e)}")
                raise e
        
        raise Exception(f"OpenAI provider failed after {self.max_retries} retries: {str(last_error)}")
    
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI API"""
        try:
            response = await self.client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"OpenAI embedding error: {str(e)}")
            raise e
    
    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        return [
            "gpt-4",
            "gpt-4-turbo", 
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]
    
    def calculate_cost_from_usage(self, usage) -> float:
        """Calculate cost from OpenAI usage object"""
        model_pricing = self.PRICING.get(self.model, {"input": 0.01, "output": 0.03})
        
        input_cost = (usage.prompt_tokens / 1000) * model_pricing["input"]
        output_cost = (usage.completion_tokens / 1000) * model_pricing["output"]
        
        return input_cost + output_cost
    
    def calculate_cost(self, usage: LLMUsage) -> float:
        """Calculate cost for usage"""
        model_pricing = self.PRICING.get(usage.model, {"input": 0.01, "output": 0.03})
        
        input_cost = (usage.prompt_tokens / 1000) * model_pricing["input"]
        output_cost = (usage.completion_tokens / 1000) * model_pricing["output"]
        
        return input_cost + output_cost


class MockOpenAIProvider(AbstractLLMProvider):
    """Mock OpenAI provider for testing when API key not available"""
    
    def __init__(self, api_key: str = "mock", model: str = "gpt-4-turbo", **kwargs):
        super().__init__(api_key, model, **kwargs)
        logger.info("Initialized Mock OpenAI provider (no API calls will be made)")
    
    async def generate(
        self,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate mock response"""
        await asyncio.sleep(0.5)  # Simulate API delay
        
        # Generate a reasonable mock response based on the last message
        last_message = messages[-1].content if messages else "Hello"
        
        if "analyze" in last_message.lower():
            mock_content = {
                "document_type": "specification",
                "summary": "This document contains technical specifications and requirements.",
                "key_points": ["Technical requirements", "Performance criteria", "Compliance standards"],
                "quality_score": 8,
                "metadata": {"pages": 5, "sections": 3},
                "suggestions": ["Add more detail to section 2", "Include compliance checklist"]
            }
            content = json.dumps(mock_content, indent=2)
        elif "suggest" in last_message.lower() or "improve" in last_message.lower():
            mock_content = {
                "overall_score": 7,
                "strengths": ["Clear objectives", "Well-structured requirements"],
                "weaknesses": ["Missing evaluation criteria", "Unclear timeline"],
                "suggestions": ["Add detailed evaluation matrix", "Specify project timeline"],
                "missing_sections": ["Budget information", "Technical specifications"],
                "evaluation_criteria": ["Technical capability", "Cost effectiveness", "Timeline feasibility"]
            }
            content = json.dumps(mock_content, indent=2)
        else:
            content = f"This is a mock response to: {last_message[:100]}..."
        
        usage = LLMUsage(
            prompt_tokens=len(last_message) // 4,  # Rough estimate
            completion_tokens=len(content) // 4,
            total_tokens=(len(last_message) + len(content)) // 4,
            estimated_cost=0.001,  # Mock cost
            provider=LLMProvider.OPENAI,
            model=self.model
        )
        
        return LLMResponse(
            content=content,
            usage=usage,
            confidence=0.85,
            provider=LLMProvider.OPENAI,
            model=self.model,
            response_time=0.5,
            metadata={"mock": True}
        )
    
    async def embed(self, text: str) -> List[float]:
        """Generate mock embeddings"""
        await asyncio.sleep(0.1)
        # Return a mock 1536-dimension vector (OpenAI ada-002 size)
        import random
        return [random.random() for _ in range(1536)]
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return ["gpt-4-turbo", "gpt-3.5-turbo"]
    
    def calculate_cost(self, usage: LLMUsage) -> float:
        """Calculate mock cost"""
        return 0.001