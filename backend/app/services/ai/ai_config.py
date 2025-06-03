"""
AI Configuration and Initialization
Manages AI service setup with proper provider configuration
"""
import os
import logging
from typing import Optional, Dict, Any
import keyring

from .llm_service import llm_service, LLMProvider
from .providers.openai_provider import OpenAIProvider, MockOpenAIProvider
from .providers.anthropic_provider import AnthropicProvider, MockAnthropicProvider
from .providers.azure_provider import AzureOpenAIProvider, MockAzureOpenAIProvider

logger = logging.getLogger(__name__)


class AIConfig:
    """AI Configuration Manager"""
    
    def __init__(self):
        self.initialized = False
        self.mock_mode = False
        self.available_providers = []
    
    def initialize_ai_services(self, force_mock: bool = False) -> Dict[str, Any]:
        """
        Initialize AI services with available providers
        """
        if self.initialized and not force_mock:
            return self.get_status()
        
        logger.info("Initializing AI services...")
        
        # Reset service
        llm_service.providers = {}
        llm_service.primary_provider = None
        llm_service.fallback_providers = []
        
        providers_initialized = []
        errors = []
        
        # Try to initialize each provider
        if not force_mock:
            # OpenAI
            openai_provider = self._init_openai_provider()
            if openai_provider:
                llm_service.register_provider(LLMProvider.OPENAI, openai_provider, is_primary=True)
                providers_initialized.append("OpenAI")
            
            # Anthropic
            anthropic_provider = self._init_anthropic_provider()
            if anthropic_provider:
                llm_service.register_provider(LLMProvider.ANTHROPIC, anthropic_provider)
                providers_initialized.append("Anthropic")
                if not llm_service.primary_provider:
                    llm_service.set_primary_provider(LLMProvider.ANTHROPIC)
            
            # Azure OpenAI
            azure_provider = self._init_azure_provider()
            if azure_provider:
                llm_service.register_provider(LLMProvider.AZURE_OPENAI, azure_provider)
                providers_initialized.append("Azure OpenAI")
                if not llm_service.primary_provider:
                    llm_service.set_primary_provider(LLMProvider.AZURE_OPENAI)
        
        # If no real providers or force_mock, use mock providers
        if not providers_initialized or force_mock:
            logger.info("Initializing mock providers for development/testing")
            self._init_mock_providers()
            providers_initialized = ["Mock OpenAI", "Mock Anthropic", "Mock Azure"]
            self.mock_mode = True
        
        self.available_providers = providers_initialized
        self.initialized = True
        
        logger.info(f"AI services initialized with providers: {', '.join(providers_initialized)}")
        
        return {
            "initialized": True,
            "mock_mode": self.mock_mode,
            "providers": providers_initialized,
            "primary_provider": str(llm_service.primary_provider) if llm_service.primary_provider else None,
            "errors": errors
        }
    
    def _init_openai_provider(self) -> Optional[OpenAIProvider]:
        """Initialize OpenAI provider"""
        try:
            api_key = self._get_api_key("OPENAI_API_KEY")
            if not api_key:
                logger.info("OpenAI API key not found")
                return None
            
            provider = OpenAIProvider(
                api_key=api_key,
                model="gpt-4-turbo",
                embedding_model="text-embedding-ada-002"
            )
            
            logger.info("OpenAI provider initialized successfully")
            return provider
            
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI provider: {str(e)}")
            return None
    
    def _init_anthropic_provider(self) -> Optional[AnthropicProvider]:
        """Initialize Anthropic provider"""
        try:
            api_key = self._get_api_key("ANTHROPIC_API_KEY")
            if not api_key:
                logger.info("Anthropic API key not found")
                return None
            
            provider = AnthropicProvider(
                api_key=api_key,
                model="claude-3-sonnet-20240229"
            )
            
            logger.info("Anthropic provider initialized successfully")
            return provider
            
        except Exception as e:
            logger.warning(f"Failed to initialize Anthropic provider: {str(e)}")
            return None
    
    def _init_azure_provider(self) -> Optional[AzureOpenAIProvider]:
        """Initialize Azure OpenAI provider"""
        try:
            api_key = self._get_api_key("AZURE_OPENAI_API_KEY")
            endpoint = self._get_config("AZURE_OPENAI_ENDPOINT")
            
            if not api_key or not endpoint:
                logger.info("Azure OpenAI credentials not found")
                return None
            
            provider = AzureOpenAIProvider(
                api_key=api_key,
                azure_endpoint=endpoint,
                model="gpt-4",
                deployment_name=self._get_config("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
            )
            
            logger.info("Azure OpenAI provider initialized successfully")
            return provider
            
        except Exception as e:
            logger.warning(f"Failed to initialize Azure OpenAI provider: {str(e)}")
            return None
    
    def _init_mock_providers(self):
        """Initialize mock providers for development/testing"""
        try:
            # Mock OpenAI
            mock_openai = MockOpenAIProvider()
            llm_service.register_provider(LLMProvider.OPENAI, mock_openai, is_primary=True)
            
            # Mock Anthropic
            mock_anthropic = MockAnthropicProvider()
            llm_service.register_provider(LLMProvider.ANTHROPIC, mock_anthropic)
            
            # Mock Azure
            mock_azure = MockAzureOpenAIProvider()
            llm_service.register_provider(LLMProvider.AZURE_OPENAI, mock_azure)
            
            logger.info("Mock providers initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize mock providers: {str(e)}")
            raise
    
    def _get_api_key(self, key_name: str) -> Optional[str]:
        """Get API key from various sources"""
        
        # Try environment variable first
        api_key = os.getenv(key_name)
        if api_key:
            return api_key
        
        # Try keyring (Memex secrets)
        try:
            api_key = keyring.get_password("memex", key_name.lower())
            if api_key:
                return api_key
        except Exception as e:
            logger.debug(f"Keyring lookup failed for {key_name}: {str(e)}")
        
        # Try alternative names
        alt_names = {
            "OPENAI_API_KEY": ["openai_api_key", "OPENAI_KEY"],
            "ANTHROPIC_API_KEY": ["anthropic_api_key", "ANTHROPIC_KEY", "CLAUDE_API_KEY"],
            "AZURE_OPENAI_API_KEY": ["azure_openai_api_key", "AZURE_API_KEY"]
        }
        
        for alt_name in alt_names.get(key_name, []):
            api_key = os.getenv(alt_name)
            if api_key:
                return api_key
            
            try:
                api_key = keyring.get_password("memex", alt_name.lower())
                if api_key:
                    return api_key
            except Exception:
                continue
        
        return None
    
    def _get_config(self, key_name: str, default: str = None) -> Optional[str]:
        """Get configuration value"""
        return os.getenv(key_name, default)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current AI service status"""
        return {
            "initialized": self.initialized,
            "mock_mode": self.mock_mode,
            "providers": self.available_providers,
            "primary_provider": str(llm_service.primary_provider) if llm_service.primary_provider else None,
            "total_providers": len(llm_service.providers),
            "usage_stats": llm_service.get_usage_stats()
        }
    
    def add_api_key(self, provider: str, api_key: str, **config) -> bool:
        """Add API key for a provider"""
        try:
            provider_upper = provider.upper()
            
            if provider_upper == "OPENAI":
                provider_instance = OpenAIProvider(api_key=api_key, **config)
                llm_service.register_provider(LLMProvider.OPENAI, provider_instance)
                
            elif provider_upper == "ANTHROPIC":
                provider_instance = AnthropicProvider(api_key=api_key, **config)
                llm_service.register_provider(LLMProvider.ANTHROPIC, provider_instance)
                
            elif provider_upper == "AZURE" or provider_upper == "AZURE_OPENAI":
                if "azure_endpoint" not in config:
                    raise ValueError("Azure endpoint required")
                provider_instance = AzureOpenAIProvider(api_key=api_key, **config)
                llm_service.register_provider(LLMProvider.AZURE_OPENAI, provider_instance)
                
            else:
                raise ValueError(f"Unknown provider: {provider}")
            
            # Update available providers
            if provider not in self.available_providers:
                self.available_providers.append(provider)
            
            # Disable mock mode if real provider added
            if self.mock_mode and len([p for p in self.available_providers if "Mock" not in p]) > 0:
                self.mock_mode = False
            
            logger.info(f"Successfully added {provider} provider")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add {provider} provider: {str(e)}")
            return False
    
    def remove_provider(self, provider: str) -> bool:
        """Remove a provider"""
        try:
            provider_enum = LLMProvider(provider.lower())
            
            if provider_enum in llm_service.providers:
                del llm_service.providers[provider_enum]
                
                # Update primary provider if needed
                if llm_service.primary_provider == provider_enum:
                    remaining_providers = list(llm_service.providers.keys())
                    llm_service.primary_provider = remaining_providers[0] if remaining_providers else None
                
                # Update fallback providers
                if provider_enum in llm_service.fallback_providers:
                    llm_service.fallback_providers.remove(provider_enum)
                
                # Update available providers list
                self.available_providers = [p for p in self.available_providers if provider.lower() not in p.lower()]
                
                logger.info(f"Removed {provider} provider")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove {provider} provider: {str(e)}")
            return False
    
    def test_provider(self, provider: str = None) -> Dict[str, Any]:
        """Test a specific provider or all providers"""
        if provider:
            return self._test_single_provider(provider)
        else:
            return self._test_all_providers()
    
    def _test_single_provider(self, provider: str) -> Dict[str, Any]:
        """Test a single provider"""
        try:
            provider_enum = LLMProvider(provider.lower())
            
            if provider_enum not in llm_service.providers:
                return {"success": False, "error": f"Provider {provider} not available"}
            
            # Simple test request
            import asyncio
            
            async def test():
                response = await llm_service.generate(
                    "Hello, this is a test. Please respond with 'Test successful'.",
                    provider=provider_enum,
                    max_tokens=50
                )
                return response
            
            response = asyncio.run(test())
            
            return {
                "success": True,
                "provider": provider,
                "response_time": response.response_time,
                "content": response.content[:100],
                "usage": response.usage.model_dump()
            }
            
        except Exception as e:
            return {
                "success": False,
                "provider": provider,
                "error": str(e)
            }
    
    def _test_all_providers(self) -> Dict[str, Any]:
        """Test all available providers"""
        results = {}
        
        for provider_enum in llm_service.providers:
            provider_name = provider_enum.value
            results[provider_name] = self._test_single_provider(provider_name)
        
        return {
            "total_providers": len(results),
            "successful_providers": len([r for r in results.values() if r.get("success")]),
            "results": results
        }


# Global AI config instance
ai_config = AIConfig()