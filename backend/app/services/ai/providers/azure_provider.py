"""
Azure OpenAI Provider Implementation
Supports Azure-hosted OpenAI models
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
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    AZURE_OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available for Azure. Install with: pip install openai")


class AzureOpenAIProvider(AbstractLLMProvider):
    """Azure OpenAI LLM Provider"""
    
    # Azure pricing varies by region and deployment
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-35-turbo": {"input": 0.0015, "output": 0.002},
        "text-embedding-ada-002": {"input": 0.0001, "output": 0}
    }
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "gpt-4",
        azure_endpoint: str = None,
        api_version: str = "2024-02-15-preview",
        deployment_name: str = None,
        **kwargs
    ):
        super().__init__(api_key, model, **kwargs)
        
        if not AZURE_OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed")
        
        if not azure_endpoint:
            raise ValueError("Azure endpoint is required")
        
        self.client = openai.AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version
        )
        
        self.deployment_name = deployment_name or model
        self.embedding_deployment = kwargs.get("embedding_deployment", "text-embedding-ada-002")
        self.max_retries = kwargs.get("max_retries", 3)
        self.timeout = kwargs.get("timeout", 30)
        
        logger.info(f"Initialized Azure OpenAI provider with deployment: {self.deployment_name}")
    
    async def generate(
        self,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Azure OpenAI API"""
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
            "model": self.deployment_name,  # Use deployment name for Azure
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
                    provider=LLMProvider.AZURE_OPENAI,
                    model=self.model
                )
                
                # Confidence based on response quality
                confidence = min(0.9, len(content) / 1000) if content else 0.1
                
                return LLMResponse(
                    content=content,
                    usage=usage,
                    confidence=confidence,
                    provider=LLMProvider.AZURE_OPENAI,
                    model=self.model,
                    response_time=time.time() - start_time,
                    metadata={
                        "finish_reason": response.choices[0].finish_reason,
                        "model_used": response.model,
                        "deployment": self.deployment_name
                    }
                )
                
            except openai.RateLimitError as e:
                logger.warning(f"Azure OpenAI rate limit hit, retrying in {2 ** retries} seconds")
                await asyncio.sleep(2 ** retries)
                retries += 1
                last_error = e
                
            except openai.APIError as e:
                logger.error(f"Azure OpenAI API error: {str(e)}")
                retries += 1
                last_error = e
                if retries < self.max_retries:
                    await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Unexpected error with Azure OpenAI: {str(e)}")
                raise e
        
        raise Exception(f"Azure OpenAI provider failed after {self.max_retries} retries: {str(last_error)}")
    
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using Azure OpenAI API"""
        try:
            response = await self.client.embeddings.create(
                input=text,
                model=self.embedding_deployment
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Azure OpenAI embedding error: {str(e)}")
            raise e
    
    def get_available_models(self) -> List[str]:
        """Get list of available Azure OpenAI models"""
        return [
            "gpt-4",
            "gpt-35-turbo",
            "gpt-4-turbo"
        ]
    
    def calculate_cost_from_usage(self, usage) -> float:
        """Calculate cost from Azure OpenAI usage object"""
        # Use base model name for pricing lookup
        base_model = self.model.replace("-", "").replace("35", "-35")
        model_pricing = self.PRICING.get(base_model, {"input": 0.01, "output": 0.03})
        
        input_cost = (usage.prompt_tokens / 1000) * model_pricing["input"]
        output_cost = (usage.completion_tokens / 1000) * model_pricing["output"]
        
        return input_cost + output_cost
    
    def calculate_cost(self, usage: LLMUsage) -> float:
        """Calculate cost for usage"""
        base_model = usage.model.replace("-", "").replace("35", "-35")
        model_pricing = self.PRICING.get(base_model, {"input": 0.01, "output": 0.03})
        
        input_cost = (usage.prompt_tokens / 1000) * model_pricing["input"]
        output_cost = (usage.completion_tokens / 1000) * model_pricing["output"]
        
        return input_cost + output_cost


class MockAzureOpenAIProvider(AbstractLLMProvider):
    """Mock Azure OpenAI provider for testing when API key not available"""
    
    def __init__(
        self, 
        api_key: str = "mock", 
        model: str = "gpt-4",
        azure_endpoint: str = "https://mock.openai.azure.com/",
        **kwargs
    ):
        super().__init__(api_key, model, **kwargs)
        self.azure_endpoint = azure_endpoint
        logger.info("Initialized Mock Azure OpenAI provider (no API calls will be made)")
    
    async def generate(
        self,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate mock response"""
        await asyncio.sleep(0.7)  # Simulate Azure API delay
        
        # Generate a reasonable mock response
        last_message = messages[-1].content if messages else "Hello"
        
        if "analyze" in last_message.lower():
            mock_content = {
                "document_type": "contract",
                "summary": "This document contains contractual terms and conditions.",
                "key_points": ["Payment terms", "Delivery requirements", "Legal obligations"],
                "quality_score": 8,
                "metadata": {"legal_complexity": "medium", "risk_level": "low"},
                "suggestions": ["Review liability clauses", "Clarify payment schedule"]
            }
            content = json.dumps(mock_content, indent=2)
        elif "suggest" in last_message.lower() or "improve" in last_message.lower():
            mock_content = {
                "overall_score": 7,
                "strengths": ["Clear scope", "Detailed requirements"],
                "weaknesses": ["Missing risk assessment", "Unclear success metrics"],
                "suggestions": ["Add risk mitigation plan", "Define KPIs"],
                "missing_sections": ["Project timeline", "Quality assurance"],
                "evaluation_criteria": ["Technical approach", "Team expertise", "Past performance"]
            }
            content = json.dumps(mock_content, indent=2)
        else:
            content = f"Azure OpenAI response to: {last_message[:100]}...\n\nThis is a comprehensive analysis based on enterprise-grade AI processing."
        
        usage = LLMUsage(
            prompt_tokens=len(last_message) // 4,
            completion_tokens=len(content) // 4,
            total_tokens=(len(last_message) + len(content)) // 4,
            estimated_cost=0.0015,  # Mock cost
            provider=LLMProvider.AZURE_OPENAI,
            model=self.model
        )
        
        return LLMResponse(
            content=content,
            usage=usage,
            confidence=0.88,
            provider=LLMProvider.AZURE_OPENAI,
            model=self.model,
            response_time=0.7,
            metadata={"mock": True, "azure_endpoint": self.azure_endpoint}
        )
    
    async def embed(self, text: str) -> List[float]:
        """Generate mock embeddings"""
        await asyncio.sleep(0.2)
        # Return a mock 1536-dimension vector
        import random
        return [random.random() for _ in range(1536)]
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return ["gpt-4", "gpt-35-turbo"]
    
    def calculate_cost(self, usage: LLMUsage) -> float:
        """Calculate mock cost"""
        return 0.0015