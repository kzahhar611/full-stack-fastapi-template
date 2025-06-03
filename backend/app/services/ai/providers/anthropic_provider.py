"""
Anthropic Claude Provider Implementation
Supports Claude-3 models (Opus, Sonnet, Haiku)
"""
import asyncio
import logging
from typing import List, Optional, Dict, Any
import json
import time

from ..llm_service import AbstractLLMProvider, LLMResponse, LLMUsage, LLMMessage, LLMProvider

logger = logging.getLogger(__name__)

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not available. Install with: pip install anthropic")


class AnthropicProvider(AbstractLLMProvider):
    """Anthropic Claude LLM Provider"""
    
    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
        "claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    }
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", **kwargs):
        super().__init__(api_key, model, **kwargs)
        
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic library not installed")
        
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.max_retries = kwargs.get("max_retries", 3)
        self.timeout = kwargs.get("timeout", 30)
        
        logger.info(f"Initialized Anthropic provider with model: {model}")
    
    async def generate(
        self,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Anthropic API"""
        start_time = time.time()
        
        # Convert messages to Anthropic format
        system_message = None
        claude_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                claude_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Prepare request parameters
        request_params = {
            "model": self.model,
            "messages": claude_messages,
            "max_tokens": max_tokens or 1500,
            "temperature": temperature,
            "timeout": self.timeout
        }
        
        if system_message:
            request_params["system"] = system_message
        
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                response = await self.client.messages.create(**request_params)
                
                # Extract response data
                content = response.content[0].text if response.content else ""
                
                # Calculate usage (Anthropic provides usage info)
                usage = LLMUsage(
                    prompt_tokens=response.usage.input_tokens,
                    completion_tokens=response.usage.output_tokens,
                    total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                    estimated_cost=self.calculate_cost_from_usage(response.usage),
                    provider=LLMProvider.ANTHROPIC,
                    model=self.model
                )
                
                # Claude responses tend to be high quality
                confidence = min(0.95, len(content) / 1000) if content else 0.1
                
                return LLMResponse(
                    content=content,
                    usage=usage,
                    confidence=confidence,
                    provider=LLMProvider.ANTHROPIC,
                    model=self.model,
                    response_time=time.time() - start_time,
                    metadata={
                        "stop_reason": response.stop_reason,
                        "model_used": response.model
                    }
                )
                
            except anthropic.RateLimitError as e:
                logger.warning(f"Anthropic rate limit hit, retrying in {2 ** retries} seconds")
                await asyncio.sleep(2 ** retries)
                retries += 1
                last_error = e
                
            except anthropic.APIError as e:
                logger.error(f"Anthropic API error: {str(e)}")
                retries += 1
                last_error = e
                if retries < self.max_retries:
                    await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Unexpected error with Anthropic: {str(e)}")
                raise e
        
        raise Exception(f"Anthropic provider failed after {self.max_retries} retries: {str(last_error)}")
    
    async def embed(self, text: str) -> List[float]:
        """
        Anthropic doesn't provide embeddings API
        This is a placeholder that raises NotImplementedError
        """
        raise NotImplementedError("Anthropic does not provide embeddings API")
    
    def get_available_models(self) -> List[str]:
        """Get list of available Anthropic models"""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229", 
            "claude-3-haiku-20240307"
        ]
    
    def calculate_cost_from_usage(self, usage) -> float:
        """Calculate cost from Anthropic usage object"""
        model_pricing = self.PRICING.get(self.model, {"input": 3.0, "output": 15.0})
        
        input_cost = (usage.input_tokens / 1000000) * model_pricing["input"]
        output_cost = (usage.output_tokens / 1000000) * model_pricing["output"]
        
        return input_cost + output_cost
    
    def calculate_cost(self, usage: LLMUsage) -> float:
        """Calculate cost for usage"""
        model_pricing = self.PRICING.get(usage.model, {"input": 3.0, "output": 15.0})
        
        input_cost = (usage.prompt_tokens / 1000000) * model_pricing["input"]
        output_cost = (usage.completion_tokens / 1000000) * model_pricing["output"]
        
        return input_cost + output_cost


class MockAnthropicProvider(AbstractLLMProvider):
    """Mock Anthropic provider for testing when API key not available"""
    
    def __init__(self, api_key: str = "mock", model: str = "claude-3-sonnet-20240229", **kwargs):
        super().__init__(api_key, model, **kwargs)
        logger.info("Initialized Mock Anthropic provider (no API calls will be made)")
    
    async def generate(
        self,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate mock response"""
        await asyncio.sleep(0.6)  # Simulate API delay
        
        # Generate a reasonable mock response
        last_message = messages[-1].content if messages else "Hello"
        
        if "analyze" in last_message.lower():
            mock_content = {
                "document_type": "requirement",
                "summary": "This document outlines comprehensive requirements for the project.",
                "key_points": ["Functional requirements", "Non-functional requirements", "Constraints"],
                "quality_score": 9,
                "metadata": {"complexity": "high", "completeness": "good"},
                "suggestions": ["Add acceptance criteria", "Define performance metrics"]
            }
            content = json.dumps(mock_content, indent=2)
        elif "suggest" in last_message.lower() or "improve" in last_message.lower():
            mock_content = {
                "overall_score": 8,
                "strengths": ["Comprehensive scope", "Clear deliverables"],
                "weaknesses": ["Timeline too aggressive", "Budget constraints unclear"],
                "suggestions": ["Extend timeline by 2 weeks", "Define budget ranges"],
                "missing_sections": ["Risk assessment", "Change management process"],
                "evaluation_criteria": ["Experience", "Methodology", "Cost", "Timeline"]
            }
            content = json.dumps(mock_content, indent=2)
        else:
            content = f"I understand you're asking about: {last_message[:100]}...\n\nBased on my analysis, I would recommend focusing on the key requirements and ensuring clear communication throughout the process."
        
        usage = LLMUsage(
            prompt_tokens=len(last_message) // 3,  # Claude is more efficient
            completion_tokens=len(content) // 3,
            total_tokens=(len(last_message) + len(content)) // 3,
            estimated_cost=0.002,  # Mock cost
            provider=LLMProvider.ANTHROPIC,
            model=self.model
        )
        
        return LLMResponse(
            content=content,
            usage=usage,
            confidence=0.92,
            provider=LLMProvider.ANTHROPIC,
            model=self.model,
            response_time=0.6,
            metadata={"mock": True}
        )
    
    async def embed(self, text: str) -> List[float]:
        """Mock embedding - Anthropic doesn't provide embeddings"""
        raise NotImplementedError("Anthropic does not provide embeddings API")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return ["claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
    
    def calculate_cost(self, usage: LLMUsage) -> float:
        """Calculate mock cost"""
        return 0.002