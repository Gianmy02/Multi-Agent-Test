"""
LangChain-based LLM client for Google Gemini AI.
Simplified implementation using only Google Generative AI.
"""

from abc import ABC, abstractmethod
from typing import Optional
import re
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from . import config


def _mask_sensitive_data(text: str) -> str:
    """Mask sensitive data in text for safe logging.
    
    Args:
        text: Text that may contain sensitive data
        
    Returns:
        Text with sensitive data masked
    """
    # Mask Bearer tokens
    text = re.sub(r'(Bearer\s+)([A-Za-z0-9_\-\.]+)', r'\1***REDACTED***', text)
    # Mask API keys (common patterns)
    text = re.sub(
        r'(api[-_]?key["\']?\s*[=:]\s*["\']?)([A-Za-z0-9_\-]+)',
        r'\1***REDACTED***',
        text,
        flags=re.IGNORECASE
    )
    # Mask tokens (common patterns)
    text = re.sub(
        r'(token["\']?\s*[=:]\s*["\']?)([A-Za-z0-9_\-\.]+)',
        r'\1***REDACTED***',
        text,
        flags=re.IGNORECASE
    )
    return text


class BaseLLMClient(ABC):
    """Base LLM client interface."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate completion from LLM."""
        pass


class LangChainLLMClient(BaseLLMClient):
    """Google Gemini LLM client using LangChain.
    
    Uses Google's Gemini 2.5 Flash model via the v1beta API.
    """
    
    def __init__(
        self,
        provider: str = "google",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        verbose: bool = False,
    ) -> None:
        """
        Initialize LangChain LLM client for Google Gemini.
        
        Args:
            provider: LLM provider (must be 'google')
            api_key: Google API key for Gemini
            model: Model name (default: gemini-2.5-flash)
            temperature: Sampling temperature (0.0-1.0, default from config)
            verbose: Enable verbose logging
        """
        if provider != "google":
            raise ValueError(
                f"Only 'google' provider is supported. Got: {provider}"
            )
        
        self.provider = provider
        self.temperature = temperature if temperature is not None else config.DEFAULT_LLM_TEMPERATURE
        self.verbose = verbose
        self.logger = config.setup_logging(verbose)
        
        if not api_key:
            raise ValueError("Google API key is required")
        
        if self.verbose:
            self.logger.info("Initializing Google Gemini provider")
        
        # Initialize Google Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model=model or "gemini-2.5-flash",  # Gemini 2.5 Flash (v1beta compatible)
            temperature=self.temperature,  # FIX: Use self.temperature (guaranteed float) not parameter
        )
    
    @retry(
        stop=stop_after_attempt(config.API_RETRY_ATTEMPTS),
        wait=wait_exponential(
            multiplier=config.API_RETRY_MULTIPLIER, 
            min=config.API_RETRY_MIN_WAIT, 
            max=config.API_RETRY_MAX_WAIT
        ),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate completion using LangChain with automatic retry for transient failures.
        
        Retries automatically for network errors using exponential backoff configured in config.py.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for context
            
        Returns:
            Generated text completion
            
        Raises:
            RuntimeError: If API call fails after all retry attempts
        """
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        messages.append(HumanMessage(content=prompt))
        
        try:
            response = self.llm.invoke(messages)
            
            # Handle both string and list responses from Google Gemini
            content = response.content
            if isinstance(content, list):
                content = "".join(str(part) for part in content)
            
            return content.strip()
        except Exception as e:
            error_msg = f"Error calling Google Gemini API: {str(e)}"
            if self.verbose:
                self.logger.error(_mask_sensitive_data(error_msg))
            raise RuntimeError(error_msg) from e
