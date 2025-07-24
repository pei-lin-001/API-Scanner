"""
OpenAI vendor implementation
"""

import re
from typing import List, Tuple

import rich
from openai import OpenAI
from openai._exceptions import (
    APIError, 
    AuthenticationError, 
    RateLimitError, 
    PermissionDeniedError, 
    APIConnectionError,
    InternalServerError
)

from ..base import BaseVendor


class OpenAIVendor(BaseVendor):
    """
    OpenAI API key vendor implementation
    """
    
    def get_vendor_name(self) -> str:
        return "OpenAI"
    
    def get_regex_patterns(self) -> List[Tuple[re.Pattern, bool, bool]]:
        return [
            # Classic OpenAI API Key pattern: sk-... (legacy format)
            (re.compile(r"sk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}"), True, False),
            # New OpenAI API Key pattern (project keys)
            (re.compile(r"sk-proj-[A-Za-z0-9_-]{64}"), True, False),
            # Organization keys (newer format)
            (re.compile(r"sk-[A-Za-z0-9]{48}"), True, False),
            # More flexible pattern for various key lengths and formats (including underscores)
            (re.compile(r"sk-[A-Za-z0-9_-]{10,64}"), True, False),
        ]
    
    def validate_key(self, api_key: str) -> str:
        """
        验证OpenAI API密钥
        
        Args:
            api_key: 要验证的API密钥
            
        Returns:
            str: 验证状态
                - "yes": 密钥有效且可用
                - "authentication_error": 认证失败（永久性错误）
                - "permission_denied": 权限不足（永久性错误）
                - "rate_limit_exceeded": 达到速率限制（临时性错误）
                - "insufficient_quota": 配额不足（可能临时）
                - "service_unavailable": 服务不可用（临时性错误）
                - "internal_error": 内部服务器错误（临时性错误）
                - "unknown_error": 其他未知错误（可能临时）
        """
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            rich.print(f"🔑 [bold green]available OpenAI key[/bold green]: [orange_red1]'{api_key}'[/orange_red1]\n")
            return "yes"
            
        except AuthenticationError as e:
            # 401 - API密钥无效或已失效（永久性错误）
            rich.print(f"[bold red]🔐 Authentication failed[/bold red]: '{api_key[:10]}...{api_key[-10:]}'")
            return "authentication_error"
            
        except PermissionDeniedError as e:
            # 403 - 权限不足，可能是组织限制（永久性错误）
            rich.print(f"[bold red]🚫 Permission denied[/bold red]: '{api_key[:10]}...{api_key[-10:]}'")
            return "permission_denied"
            
        except RateLimitError as e:
            # 429 - 速率限制或配额不足
            error_message = str(e).lower()
            if 'quota' in error_message or 'billing' in error_message or 'insufficient_quota' in error_message:
                # 配额不足 - 可能是临时的（如果用户充值）
                rich.print(f"[bold yellow]💰 Quota insufficient[/bold yellow]: '{api_key[:10]}...{api_key[-10:]}'")
                return "insufficient_quota"
            else:
                # 速率限制 - 临时性错误
                rich.print(f"[bold yellow]⚠️ Rate limit exceeded[/bold yellow]: '{api_key[:10]}...{api_key[-10:]}'")
                return "rate_limit_exceeded"
                
        except APIConnectionError as e:
            # 网络连接问题 - 临时性错误
            rich.print(f"[bold orange_red1]🌐 Connection error[/bold orange_red1]: '{api_key[:10]}...{api_key[-10:]}'")
            return "service_unavailable"
            
        except InternalServerError as e:
            # 500 - 内部服务器错误 - 临时性错误
            rich.print(f"[bold orange_red1]⚙️ Internal server error[/bold orange_red1]: '{api_key[:10]}...{api_key[-10:]}'")
            return "internal_error"
            
        except APIError as e:
            # 其他API错误，根据状态码判断
            error_code = getattr(e, 'status_code', None)
            error_message = str(e).lower()
            
            if error_code == 402 or 'insufficient_quota' in error_message:
                rich.print(f"[bold yellow]💰 Quota insufficient[/bold yellow]: '{api_key[:10]}...{api_key[-10:]}'")
                return "insufficient_quota"
            elif error_code == 429:
                rich.print(f"[bold yellow]⚠️ Rate limit exceeded[/bold yellow]: '{api_key[:10]}...{api_key[-10:]}'")
                return "rate_limit_exceeded"
            elif error_code in [500, 502, 503, 504]:
                rich.print(f"[bold orange_red1]🔧 Server error ({error_code})[/bold orange_red1]: '{api_key[:10]}...{api_key[-10:]}'")
                return "service_unavailable"
            else:
                rich.print(f"[bold red]❌ API Error ({error_code})[/bold red]: '{api_key[:10]}...{api_key[-10:]}'")
                return "unknown_error"
                
        except Exception as e:
            # 其他未知错误
            error_str = str(e).lower()
            
            # 检查是否是网络相关错误
            if any(keyword in error_str for keyword in ['timeout', 'connection', 'network', 'dns']):
                rich.print(f"[bold orange_red1]🌐 Network error[/bold orange_red1]: '{api_key[:10]}...{api_key[-10:]}'")
                return "service_unavailable"
            
            # 检查是否是SSL/TLS错误
            if any(keyword in error_str for keyword in ['ssl', 'tls', 'certificate']):
                rich.print(f"[bold orange_red1]🔒 SSL/TLS error[/bold orange_red1]: '{api_key[:10]}...{api_key[-10:]}'")
                return "service_unavailable"
            
            rich.print(f"[bold red]❓ Unknown error[/bold red]: {e} - '{api_key[:10]}...{api_key[-10:]}'")
            return "unknown_error"
    
    def get_search_keywords(self) -> List[str]:
        return [
            # 基础OpenAI关键词
            "openai", "chatgpt", "gpt-3", "gpt-4", "gpt-3.5", "gpt-4o", "gpt-4-turbo",
            "openai-api-key", "openai_api_key", "OPENAI_API_KEY", "sk-",
            
            # OpenAI产品和服务
            "davinci", "curie", "babbage", "ada", "text-davinci", "text-curie",
            "code-davinci", "gpt-35-turbo", "whisper", "dall-e", "dallee", "dalle",
            "embedding", "embeddings", "fine-tune", "fine-tuning", "completion",
            "chat_completion", "chat-completion", "completions",
            
            # OpenAI API相关
            "chat.completions", "openai.chat", "openai.completion", "openai.embeddings",
            "openai client", "openai_client", "OpenAI()", "openai.OpenAI",
            "from openai import", "import openai", "openai.api_key",
            
            # 模型名称和版本
            "gpt-3.5-turbo", "gpt-4-1106-preview", "gpt-4-vision-preview",
            "text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large",
            "whisper-1", "dall-e-2", "dall-e-3", "tts-1", "tts-1-hd",
            
            # API配置和参数
            "temperature", "max_tokens", "top_p", "frequency_penalty", "presence_penalty",
            "stop", "stream", "logit_bias", "user", "messages", "role", "content",
            "system", "assistant", "function_call", "tools", "tool_calls",
            
            # 通用AI和机器学习术语
            "language model", "llm", "large language model", "transformer",
            "artificial intelligence", "ai", "machine learning", "ml",
            "natural language processing", "nlp", "conversational ai",
            "text generation", "chat bot", "chatbot", "virtual assistant",
            "prompt engineering", "prompt", "few-shot", "zero-shot",
            
            # 认证和安全相关
            "api key", "api-key", "apikey", "secret key", "secret-key", "secretkey",
            "auth_token", "auth-token", "authorization", "bearer", "token",
            "client_secret", "client-secret", "app_secret", "app-secret",
            "credentials", "authentication", "auth", "secret", "key",
            
            # 开发相关
            "nodejs", "node.js", "python", "javascript", "typescript", "react",
            "next.js", "nextjs", "express", "flask", "django", "fastapi",
            "streamlit", "gradio", "langchain", "llamaindex", "huggingface",
            
            # 错误和异常
            "RateLimitError", "APIError", "AuthenticationError", "InvalidRequestError",
            "OpenAIError", "APIConnectionError", "ServiceUnavailableError",
            "InternalServerError", "PermissionError", "InvalidAPIKey",
            
            # 配置文件和环境变量
            "OPENAI_API_KEY", "OPENAI_API_BASE", "OPENAI_ORG_ID", "OPENAI_PROJECT_ID",
            "process.env.OPENAI", "os.environ", "getenv", "dotenv", ".env",
            "config", "settings", "configuration", "environment",
            
            # 业务和用例相关
            "customer service", "content generation", "code generation", "translation",
            "summarization", "question answering", "sentiment analysis", "classification",
            "creative writing", "email automation", "documentation", "tutoring",
            
            # 技术实现相关
            "streaming", "async", "await", "callback", "webhook", "api endpoint",
            "rest api", "http", "https", "json", "response", "request",
            "headers", "curl", "postman", "axios", "fetch", "requests",
            
            # 成本和计费相关
            "billing", "usage", "cost", "pricing", "quota", "rate limit",
            "tokens", "token count", "token limit", "credits", "subscription"
        ] 