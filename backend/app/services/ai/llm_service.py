"""
Abstract LLM Service Interface for Multi-Provider Support
Inspired by Langflow's provider abstraction patterns
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import logging
import asyncio
import time

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM Providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    LOCAL = "local"


class LLMUsage(BaseModel):
    """Token usage tracking"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    provider: LLMProvider
    model: str
    timestamp: datetime = Field(default_factory=datetime.now)


class LLMResponse(BaseModel):
    """Standardized LLM response"""
    content: str
    usage: LLMUsage
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    provider: LLMProvider
    model: str
    response_time: float = 0.0


class LLMMessage(BaseModel):
    """Message format for LLM conversations"""
    role: str  # "system", "user", "assistant"
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AbstractLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs
        self.rate_limit_delay = 0.1  # Default rate limiting
    
    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass
    
    @abstractmethod
    def calculate_cost(self, usage: LLMUsage) -> float:
        """Calculate cost for usage"""
        pass


class LLMService:
    """
    Multi-provider LLM service with failover support
    Manages multiple LLM providers and provides unified interface
    """
    
    def __init__(self):
        self.providers: Dict[LLMProvider, AbstractLLMProvider] = {}
        self.primary_provider: Optional[LLMProvider] = None
        self.fallback_providers: List[LLMProvider] = []
        self.usage_logs: List[LLMUsage] = []
        self.rate_limits: Dict[LLMProvider, float] = {}
        self.last_request_time: Dict[LLMProvider, float] = {}
    
    def register_provider(
        self,
        provider_type: LLMProvider,
        provider: AbstractLLMProvider,
        is_primary: bool = False
    ):
        """Register an LLM provider"""
        self.providers[provider_type] = provider
        
        if is_primary or self.primary_provider is None:
            self.primary_provider = provider_type
        
        if provider_type not in self.fallback_providers and not is_primary:
            self.fallback_providers.append(provider_type)
        
        logger.info(f"Registered LLM provider: {provider_type}")
    
    def set_primary_provider(self, provider_type: LLMProvider):
        """Set the primary LLM provider"""
        if provider_type in self.providers:
            self.primary_provider = provider_type
            logger.info(f"Set primary LLM provider: {provider_type}")
        else:
            raise ValueError(f"Provider {provider_type} not registered")
    
    def add_fallback_provider(self, provider_type: LLMProvider):
        """Add a fallback provider"""
        if provider_type in self.providers and provider_type not in self.fallback_providers:
            self.fallback_providers.append(provider_type)
            logger.info(f"Added fallback provider: {provider_type}")
    
    async def _rate_limit_check(self, provider_type: LLMProvider):
        """Check and enforce rate limits"""
        if provider_type in self.rate_limits:
            last_time = self.last_request_time.get(provider_type, 0)
            time_since_last = time.time() - last_time
            min_interval = self.rate_limits[provider_type]
            
            if time_since_last < min_interval:
                sleep_time = min_interval - time_since_last
                await asyncio.sleep(sleep_time)
        
        self.last_request_time[provider_type] = time.time()
    
    async def generate(
        self,
        messages: Union[str, List[LLMMessage]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        provider: Optional[LLMProvider] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate response using specified or primary provider with fallback
        """
        # Convert string to message format
        if isinstance(messages, str):
            messages = [LLMMessage(role="user", content=messages)]
        
        # Determine providers to try
        providers_to_try = []
        if provider and provider in self.providers:
            providers_to_try = [provider]
        else:
            if self.primary_provider:
                providers_to_try.append(self.primary_provider)
            providers_to_try.extend(self.fallback_providers)
        
        if not providers_to_try:
            raise ValueError("No LLM providers available")
        
        last_error = None
        
        for provider_type in providers_to_try:
            try:
                await self._rate_limit_check(provider_type)
                
                start_time = time.time()
                provider_instance = self.providers[provider_type]
                
                response = await provider_instance.generate(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                
                response.response_time = time.time() - start_time
                
                # Log usage
                self.usage_logs.append(response.usage)
                
                logger.info(f"Successfully generated response using {provider_type}")
                return response
                
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider_type} failed: {str(e)}")
                continue
        
        # All providers failed
        raise Exception(f"All LLM providers failed. Last error: {str(last_error)}")
    
    async def embed(
        self,
        text: str,
        provider: Optional[LLMProvider] = None
    ) -> List[float]:
        """Generate embeddings using specified or primary provider"""
        provider_type = provider or self.primary_provider
        
        if not provider_type or provider_type not in self.providers:
            raise ValueError("No suitable provider for embeddings")
        
        await self._rate_limit_check(provider_type)
        
        try:
            embeddings = await self.providers[provider_type].embed(text)
            logger.info(f"Generated embeddings using {provider_type}")
            return embeddings
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise
    
    async def analyze_document(
        self,
        content: str,
        document_type: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze document content using AI"""
        system_prompt = """You are an expert document analyzer. Analyze the provided document and return a JSON response with:
        - document_type: The type of document (requirement, specification, proposal, contract, evaluation, attachment)
        - summary: A brief summary of the document content
        - key_points: List of main points or requirements
        - quality_score: Quality score from 1-10
        - metadata: Any relevant metadata extracted
        - suggestions: Suggestions for improvement"""
        
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=f"Analyze this document:\n\n{content}")
        ]
        
        response = await self.generate(
            messages=messages,
            temperature=0.3,
            max_tokens=1000,
            **kwargs
        )
        
        try:
            import json
            analysis = json.loads(response.content)
            return analysis
        except json.JSONDecodeError:
            # Fallback to structured response
            return {
                "document_type": "unknown",
                "summary": response.content[:200] + "...",
                "key_points": [],
                "quality_score": 5,
                "metadata": {},
                "suggestions": []
            }
    
    async def suggest_rfp_improvements(
        self,
        rfp_content: str,
        rfp_type: str = "general",
        **kwargs
    ) -> Dict[str, Any]:
        """Suggest improvements for RFP content"""
        system_prompt = f"""You are an expert RFP consultant. Analyze the provided RFP content and suggest improvements.
        Focus on:
        - Clarity and completeness of requirements
        - Structure and organization
        - Missing information or sections
        - Compliance and legal considerations
        - Evaluation criteria suggestions
        
        Return a JSON response with:
        - overall_score: Score from 1-10
        - strengths: List of strong points
        - weaknesses: List of areas needing improvement
        - suggestions: Specific improvement suggestions
        - missing_sections: Important sections that might be missing
        - evaluation_criteria: Suggested evaluation criteria"""
        
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=f"RFP Type: {rfp_type}\n\nRFP Content:\n{rfp_content}")
        ]
        
        response = await self.generate(
            messages=messages,
            temperature=0.4,
            max_tokens=1500,
            **kwargs
        )
        
        try:
            import json
            suggestions = json.loads(response.content)
            return suggestions
        except json.JSONDecodeError:
            return {
                "overall_score": 7,
                "strengths": ["Content provided"],
                "weaknesses": ["Analysis failed"],
                "suggestions": [response.content[:500]],
                "missing_sections": [],
                "evaluation_criteria": []
            }
    
    def get_usage_stats(self, provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
        """Get usage statistics"""
        filtered_logs = self.usage_logs
        if provider:
            filtered_logs = [log for log in self.usage_logs if log.provider == provider]
        
        if not filtered_logs:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}
        
        total_requests = len(filtered_logs)
        total_tokens = sum(log.total_tokens for log in filtered_logs)
        total_cost = sum(log.estimated_cost for log in filtered_logs)
        
        return {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "average_tokens_per_request": total_tokens / total_requests if total_requests > 0 else 0,
            "providers_used": list(set(log.provider for log in filtered_logs))
        }
    
    def get_available_providers(self) -> List[LLMProvider]:
        """Get list of registered providers"""
        return list(self.providers.keys())
    
    def is_provider_available(self, provider: LLMProvider) -> bool:
        """Check if provider is available"""
        return provider in self.providers


# Global LLM service instance
llm_service = LLMService()