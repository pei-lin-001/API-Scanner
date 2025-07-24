"""
Gemini vendor implementation
"""

import re
from typing import List, Tuple

import rich
import google.generativeai as genai
from google.api_core import exceptions

from ..base import BaseVendor


class GeminiVendor(BaseVendor):
    """
    Google Gemini API key vendor implementation
    """
    
    def get_vendor_name(self) -> str:
        return "Gemini"
    
    def get_regex_patterns(self) -> List[Tuple[re.Pattern, bool, bool]]:
        return [
            # Standard Gemini API Key pattern
            (re.compile(r"AIzaSy[A-Za-z0-9_-]{33}"), True, False),
            # Alternative pattern for keys that might have slight variations
            (re.compile(r"AIzaSy[A-Za-z0-9_-]{30,40}"), True, False),
        ]
    
    def validate_key(self, api_key: str) -> str:
        """
        验证Gemini API密钥
        
        Args:
            api_key: 要验证的API密钥
            
        Returns:
            str: 验证状态
                - "yes": 密钥有效且可用
                - "authentication_error": 认证失败（永久性错误）
                - "permission_denied": 权限不足（永久性错误）
                - "rate_limit_exceeded": 达到速率限制（临时性错误）
                - "resource_exhausted": 资源耗尽（临时性错误）
                - "insufficient_quota": 配额不足（可能临时）
                - "service_unavailable": 服务不可用（临时性错误）
                - "internal_error": 内部服务器错误（临时性错误）
                - "unknown_error": 其他未知错误（可能临时）
        """
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')
            response = model.generate_content("Hello")
            
            if response and response.text:
                rich.print(f"🔑 [bold green]available Gemini key[/bold green]: [orange_red1]'{api_key}'[/orange_red1]\n")
                return "yes"
            else:
                rich.print(f"[bold yellow]⚠️ Empty response[/bold yellow]: '{api_key[:10]}...{api_key[-10:]}'")
                return "unknown_error"
                
        except Exception as e:
            error_str = str(e).lower()
            error_type = type(e).__name__
            
            # Google API 特定错误处理
            if hasattr(e, 'code'):
                error_code = e.code
                
                # 401 - 未授权/认证失败（永久性错误）
                if error_code == 401 or 'unauthorized' in error_str or 'invalid api key' in error_str:
                    rich.print(f"[bold red]🔐 Authentication failed[/bold red]: '{api_key[:10]}...{api_key[-10:]}'")
                    return "authentication_error"
                
                # 403 - 权限不足（永久性错误）
                elif error_code == 403 or 'permission_denied' in error_str or 'forbidden' in error_str:
                    rich.print(f"[bold red]🚫 Permission denied[/bold red]: '{api_key[:10]}...{api_key[-10:]}'")
                    return "permission_denied"
                
                # 429 - 资源耗尽/配额问题
                elif error_code == 429 or 'resource_exhausted' in error_str or 'quota' in error_str:
                    if 'quota' in error_str or 'limit' in error_str:
                        rich.print(f"[bold yellow]💰 Quota exhausted[/bold yellow]: '{api_key[:10]}...{api_key[-10:]}'")
                        return "insufficient_quota"
                    else:
                        rich.print(f"[bold yellow]🔥 Resource exhausted[/bold yellow]: '{api_key[:10]}...{api_key[-10:]}'")
                        return "resource_exhausted"
                
                # 500, 502, 503, 504 - 服务器错误（临时性）
                elif error_code in [500, 502, 503, 504] or 'unavailable' in error_str:
                    rich.print(f"[bold orange_red1]🔧 Service unavailable ({error_code})[/bold orange_red1]: '{api_key[:10]}...{api_key[-10:]}'")
                    return "service_unavailable"
                
                # 其他错误码
                else:
                    rich.print(f"[bold red]❌ API Error ({error_code})[/bold red]: '{api_key[:10]}...{api_key[-10:]}'")
                    return "unknown_error"
            
            # 基于错误类型和消息的判断
            if 'unauthenticated' in error_str or 'invalid api key' in error_str:
                rich.print(f"[bold red]🔐 Authentication failed[/bold red]: '{api_key[:10]}...{api_key[-10:]}'")
                return "authentication_error"
            
            elif 'permission_denied' in error_str or 'forbidden' in error_str:
                rich.print(f"[bold red]🚫 Permission denied[/bold red]: '{api_key[:10]}...{api_key[-10:]}'")
                return "permission_denied"
            
            elif 'resource_exhausted' in error_str or 'quota' in error_str:
                if 'quota' in error_str or 'billing' in error_str:
                    rich.print(f"[bold yellow]💰 Quota exhausted[/bold yellow]: '{api_key[:10]}...{api_key[-10:]}'")
                    return "insufficient_quota"
                else:
                    rich.print(f"[bold yellow]🔥 Resource exhausted[/bold yellow]: '{api_key[:10]}...{api_key[-10:]}'")
                    return "resource_exhausted"
            
            elif 'rate' in error_str and 'limit' in error_str:
                rich.print(f"[bold yellow]⚠️ Rate limit exceeded[/bold yellow]: '{api_key[:10]}...{api_key[-10:]}'")
                return "rate_limit_exceeded"
            
            elif any(keyword in error_str for keyword in ['unavailable', 'timeout', 'connection', 'network']):
                rich.print(f"[bold orange_red1]🌐 Service unavailable[/bold orange_red1]: '{api_key[:10]}...{api_key[-10:]}'")
                return "service_unavailable"
            
            elif 'internal' in error_str and 'error' in error_str:
                rich.print(f"[bold orange_red1]⚙️ Internal error[/bold orange_red1]: '{api_key[:10]}...{api_key[-10:]}'")
                return "internal_error"
            
            # 检查Google API特定的异常类型
            elif 'GoogleGenerativeAI' in error_type:
                rich.print(f"[bold red]🤖 Gemini API error[/bold red]: {e} - '{api_key[:10]}...{api_key[-10:]}'")
                return "unknown_error"
            
            else:
                rich.print(f"[bold red]❓ Unknown error[/bold red]: {e} - '{api_key[:10]}...{api_key[-10:]}'")
                return "unknown_error"
    
    def get_search_keywords(self) -> List[str]:
        return [
            # 基础Gemini关键词
            "gemini", "google ai", "google-ai", "google_ai", "bard", "palm",
            "google-api-key", "google_api_key", "GOOGLE_API_KEY", "AIzaSy",
            
            # Google AI产品和服务
            "gemini-pro", "gemini-1.5", "gemini-1.5-pro", "gemini-1.5-flash",
            "gemini-2.0", "gemini-2.5", "gemini-pro-vision", "gemini-ultra",
            "palm-2", "palm2", "text-bison", "chat-bison", "code-bison",
            "embedding-gecko", "textembedding-gecko", "multimodalembedding",
            
            # Google Cloud和Vertex AI
            "vertex ai", "vertex-ai", "vertexai", "google cloud", "gcp",
            "google cloud platform", "vertex_ai", "aiplatform", "ai-platform",
            "generativeai", "generative-ai", "generative_ai",
            "google.cloud.aiplatform", "google.generativeai", "vertexai.generative_models",
            
            # API和SDK相关
            "google.generativeai", "genai", "GenerativeModel", "ChatSession",
            "google-generativeai", "google_generativeai", "import google.generativeai",
            "from google.generativeai import", "genai.configure", "genai.GenerativeModel",
            "google.cloud.aiplatform", "vertexai.preview.generative_models",
            
            # 认证和配置
            "service account", "service-account", "service_account", "json key",
            "credentials.json", "service-account-key", "oauth", "oauth2",
            "access token", "access_token", "refresh token", "refresh_token",
            "api_key", "api-key", "apikey", "GOOGLE_APPLICATION_CREDENTIALS",
            
            # 模型配置和参数
            "temperature", "top_k", "top_p", "max_output_tokens", "candidate_count",
            "stop_sequences", "safety_settings", "generation_config", "model_name",
            "harm_category", "harm_probability", "safety_threshold", "response_validation",
            
            # 内容生成和对话
            "generate_content", "generate-content", "chat", "conversation", "prompt",
            "content", "parts", "text", "image", "multimodal", "vision",
            "function_call", "function-call", "tool_use", "code_execution",
            
            # 错误和异常
            "ResourceExhausted", "PermissionDenied", "InvalidArgument", "NotFound",
            "DeadlineExceeded", "Unauthenticated", "Unavailable", "InternalError",
            "GoogleGenerativeAIError", "BlockedPromptException", "StopCandidateException",
            
            # 开发框架和语言
            "python", "javascript", "nodejs", "node.js", "typescript", "java",
            "go", "php", "ruby", "swift", "kotlin", "dart", "flutter",
            "react", "vue", "angular", "next.js", "nuxt", "express",
            
            # AI和机器学习概念
            "large language model", "llm", "language model", "transformer",
            "artificial intelligence", "ai", "machine learning", "ml",
            "natural language processing", "nlp", "conversational ai",
            "generative ai", "text generation", "content creation", "chatbot",
            
            # 高级概念和术语
            "CoT", "chain of thought", "reasoning", "thinking", "logic",
            "DPO", "direct preference optimization", "reinforcement learning",
            "RLHF", "reinforcement learning from human feedback", "fine-tuning",
            "prompt engineering", "few-shot", "zero-shot", "in-context learning",
            
            # 代理和多代理系统
            "agent", "multi-agent", "multi-agent systems", "autonomous agent",
            "ai agent", "intelligent agent", "agent framework", "crew ai",
            "autogen", "langchain", "llamaindex", "semantic kernel",
            
            # 检索增强生成
            "rag", "retrieval-augmented generation", "retrieval augmented generation",
            "vector search", "vector database", "embedding", "embeddings",
            "semantic search", "similarity search", "document retrieval",
            
            # 应用和用例
            "virtual assistant", "personal assistant", "customer service",
            "content strategy", "competitor analysis", "data analysis",
            "keyword research", "keyword clustering", "long-tail keywords",
            "search intent", "personalized ai", "experiment", "lab",
            
            # 配置和环境
            "environment", "config", "configuration", "settings", "dotenv",
            ".env", "env", "process.env", "os.environ", "getenv",
            "GOOGLE_API_KEY", "GEMINI_API_KEY", "BARD_API_KEY", "PALM_API_KEY",
            
            # 中文相关
            "实验", "密钥", "测试", "语言模型", "人工智能", "机器学习",
            "自然语言处理", "对话系统", "文本生成", "内容创作", "智能助手",
            "谷歌", "谷歌AI", "双子座", "巴德", "配置", "设置", "环境变量",
            
            # 技术实现
            "async", "await", "streaming", "server-sent events", "sse",
            "websocket", "real-time", "batch", "concurrent", "parallel",
            "rate limiting", "quota", "billing", "usage", "monitoring",
            
            # 安全和合规
            "safety", "safety_settings", "content filtering", "harm detection",
            "toxicity", "bias", "fairness", "responsible ai", "ethical ai",
            "privacy", "data protection", "gdpr", "compliance", "audit"
        ] 