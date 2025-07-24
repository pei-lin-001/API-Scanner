"""
Configuration module for Multi-Vendor API Key Scanner

This module is now deprecated as configurations are moved to individual vendor modules.
Each vendor (OpenAI, Gemini, SiliconFlow) now defines its own:
- Regex patterns for API key detection
- Search keywords 
- Validation methods
- Database configurations

For vendor-specific configurations, see:
- src/vendors/openai/vendor.py
- src/vendors/gemini/vendor.py  
- src/vendors/silicon_flow/vendor.py
"""

# Legacy configurations - kept for reference
# These are no longer used in the main application

LEGACY_KEYWORDS = [
    "CoT",
    "DPO",
    "RLHF",
    "agent",
    "ai model",
    "aios",
    "api key",
    "api-key",
    "apikey",
    "artificial intelligence",
    "auth_token",
    "authorization",
    "chain of thought",
    "chatbot",
    "client_secret",
    "competitor analysis",
    "content strategy",
    "conversational AI",
    "data analysis",
    "deep learning",
    "direct preference optimization",
    "experiment",
    "gemini",
    "google ai",
    "google-api-key",
    "key",
    "keyword clustering",
    "keyword research",
    "lab",
    "language model experimentation",
    "large language model",
    "llama.cpp",
    "llm",
    "long-tail keywords",
    "machine learning",
    "multi-agent",
    "multi-agent systems",
    "my-secret-key",
    "natural language processing",
    "personalized AI",
    "project",
    "rag",
    "reinforcement learning from human feedback",
    "retrieval-augmented generation",
    "search intent",
    "secret key",
    "semantic search",
    "thoughts",
    "token",
    "virtual assistant",
    "实验",
    "密钥",
    "测试",
    "语言模型",
]

LEGACY_LANGUAGES = [
    "Dotenv",
    "Text",
    "JavaScript",
    "Python",
    "TypeScript",
    "Dockerfile",
    "Markdown",
    '"Jupyter Notebook"',
    "Shell",
    "Java",
    "Go",
    "C%2B%2B",
    "PHP",
    "Ruby",
    "C#",
    "Rust",
    "Kotlin",
    "Swift",
    "YAML",
    "JSON",
]

LEGACY_PATHS = [
    "path:.xml OR path:.json OR path:.properties OR path:.sql OR path:.txt OR path:.log OR path:.tmp OR path:.backup OR path:.bak OR path:.enc",
    "path:.yml OR path:.yaml OR path:.toml OR path:.ini OR path:.config OR path:.conf OR path:.cfg OR path:.env OR path:.envrc OR path:.prod",
    "path:.secret OR path:.private OR path:*.key",
]

# Legacy regex patterns - now moved to vendor modules
import re
LEGACY_REGEX_LIST = [
    # Gemini API Key (now in vendors/gemini/vendor.py)
    (re.compile(r"AIzaSy[A-Za-z0-9_-]{33}"), True, False),
]

# Backward compatibility exports (deprecated)
KEYWORDS = LEGACY_KEYWORDS
LANGUAGES = LEGACY_LANGUAGES  
PATHS = LEGACY_PATHS
REGEX_LIST = LEGACY_REGEX_LIST
