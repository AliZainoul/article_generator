#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration Module

This module provides centralized configuration and error handling for the article generator.
"""

import os
import logging

from openai import OpenAI
from dotenv import load_dotenv
from article_generator.colored_logging import setup_colored_logging

# Configure colored logging
setup_colored_logging(level=logging.INFO, format_str='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for storing application settings."""
    # API Provider Configuration
    API_PROVIDER = os.getenv('API_PROVIDER', 'openrouter')
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # Gemini Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
    
    # Model Lists
    CONTENT_VALIDATOR_MODELS = {
        'openrouter': 
                    [                        
                        # "google/gemini-2.0-flash-thinking-exp:free",
                        # "google/gemini-2.0-flash-lite-preview-02-05:free",
                        # "google/gemini-2.0-pro-exp-02-05:free",
                        "deepseek/deepseek-r1-0528:free",
                        # "qwen/qwq-32b:free",
                    ],
        'gemini':   [   
                        # "gemini-2.0-flash",
                        "gemini-3-flash-preview",
                    ],
    }
    
    ARTICLE_PLANNER_MODELS = {
        'openrouter': 
                    [                        
                        # "google/gemini-2.0-flash-thinking-exp:free",
                        # "google/gemini-2.0-flash-lite-preview-02-05:free",
                        # "google/gemini-2.0-pro-exp-02-05:free",
                        "deepseek/deepseek-r1-0528:free",
                        # "qwen/qwq-32b:free",
                    ],
        'gemini':   [   
                        # "gemini-2.0-flash",
                        "gemini-3-flash-preview",
                    ],
    }
    
    ARTICLE_WRITER_MODELS = {
        'openrouter': 
                    [                        
                        # "google/gemini-2.0-flash-thinking-exp:free",
                        # "google/gemini-2.0-flash-lite-preview-02-05:free",
                        # "google/gemini-2.0-pro-exp-02-05:free",
                        "deepseek/deepseek-r1-0528:free",
                        # "qwen/qwq-32b:free",
                    ],
        'gemini':   [   
                        # "gemini-2.0-flash",
                        "gemini-3-flash-preview",
                    ],
    }
    
    # Application Metadata
    #APP_REFERER = "https://github.com/trae-ai/article_generator"
    APP_REFERER = ""
    APP_TITLE = "Article Generator"
    DEFAULT_DELAY_SECONDS = 0


class APIError(Exception):
    """Base exception for API related errors."""
    def __init__(self, message: str):
        """
        Initialize APIError with a message.

        Args:
            message: Error message.
        """
        super().__init__(message)


class ConfigurationError(APIError):
    """Exception raised for configuration issues."""

def create_openai_client(provider: str = "") -> OpenAI:
    """
    Initialize and return an OpenAI client for the specified provider.

    Args:
        provider: The API provider to use (openrouter/gemini)

    Raises:
        ConfigurationError: If the API key is not found for the selected provider
    
    Returns:
        An instance of OpenAI client configured for the provider
    """
    provider = provider or Config.API_PROVIDER
    
    if provider == 'openrouter':
        api_key = Config.OPENROUTER_API_KEY
        base_url = Config.OPENROUTER_BASE_URL
    elif provider == 'gemini':
        api_key = Config.GEMINI_API_KEY
        base_url = Config.GEMINI_BASE_URL
    else:
        raise ConfigurationError(f"Unsupported provider: {provider}")

    if not api_key:
        logger.error(f"{provider.upper()}_API_KEY not found in environment variables")
        raise ConfigurationError(f"{provider} API key not configured. Please check your .env file.")

    return OpenAI(
        base_url=base_url,
        api_key=api_key,
        default_headers={
            "HTTP-Referer": Config.APP_REFERER,
            "X-Title": Config.APP_TITLE
        }
    )
