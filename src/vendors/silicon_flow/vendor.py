"""
Silicon Flow vendor implementation
"""

import re
from typing import List, Tuple

import rich
import httpx

from ..base import BaseVendor


class SiliconFlowVendor(BaseVendor):
    """
    Silicon Flow API key vendor implementation
    """
    
    def get_vendor_name(self) -> str:
        return "SiliconFlow"
    
    def get_regex_patterns(self) -> List[Tuple[re.Pattern, bool, bool]]:
        return [
            # Silicon Flow API Key pattern: sk- followed by 48 characters (letters and numbers)
            # Updated to be more flexible based on actual key patterns seen
            (re.compile(r"sk-[a-zA-Z0-9]{48}"), True, False),
            # Alternative pattern for keys that might have different lengths (shorter keys observed)
            (re.compile(r"sk-[a-zA-Z0-9]{16,64}"), True, False),
        ]
    
    def validate_key(self, api_key: str) -> str:
        """
        验证硅基流动API密钥
        
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
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "Qwen/Qwen3-32B",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5,
                "temperature": 0.7
            }
            
            response = httpx.post(
                "https://api.siliconflow.cn/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30.0
            )
            
            # 根据HTTP状态码判断
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get("choices") and len(result["choices"]) > 0:
                        rich.print(f"🔑 [bold green]available SiliconFlow key[/bold green]: [orange_red1]'{api_key}'[/orange_red1]\n")
                        return "yes"
                    else:
                        rich.print(f"[bold yellow]⚠️ Empty response[/bold yellow]: '{api_key[:10]}...{api_key[-10:]}'")
                        return "unknown_error"
                except Exception as parse_error:
                    rich.print(f"[bold red]📄 JSON parse error[/bold red]: '{api_key[:10]}...{api_key[-10:]}'")
                    return "unknown_error"
            
            # 错误状态码处理
            elif response.status_code == 401:
                # 401 - 未授权，API密钥无效（永久性错误）
                rich.print(f"[bold red]🔐 Authentication failed[/bold red]: '{api_key[:10]}...{api_key[-10:]}'")
                return "authentication_error"
                
            elif response.status_code == 403:
                # 403 - 权限不足（永久性错误）
                rich.print(f"[bold red]🚫 Permission denied[/bold red]: '{api_key[:10]}...{api_key[-10:]}'")
                return "permission_denied"
                
            elif response.status_code == 429:
                # 429 - 速率限制或配额问题
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get("message", "").lower()
                except:
                    error_message = response.text.lower()
                
                if any(keyword in error_message for keyword in ["quota", "billing", "insufficient", "balance"]):
                    rich.print(f"[bold yellow]💰 Quota insufficient[/bold yellow]: '{api_key[:10]}...{api_key[-10:]}'")
                    return "insufficient_quota"
                else:
                    rich.print(f"[bold yellow]⚠️ Rate limit exceeded[/bold yellow]: '{api_key[:10]}...{api_key[-10:]}'")
                    return "rate_limit_exceeded"
            
            elif response.status_code == 402:
                # 402 - 付费要求（配额不足）
                rich.print(f"[bold yellow]�� Payment required[/bold yellow]: '{api_key[:10]}...{api_key[-10:]}'")
                return "insufficient_quota"
                
            elif response.status_code in [500, 502, 503, 504]:
                # 5xx - 服务器错误（临时性错误）
                rich.print(f"[bold orange_red1]🔧 Server error ({response.status_code})[/bold orange_red1]: '{api_key[:10]}...{api_key[-10:]}'")
                return "service_unavailable"
                
            elif response.status_code == 404:
                # 404 - 端点不存在或模型不可用
                rich.print(f"[bold red]🔍 Endpoint not found[/bold red]: '{api_key[:10]}...{api_key[-10:]}'")
                return "unknown_error"
                
            elif response.status_code == 422:
                # 422 - 请求参数错误
                rich.print(f"[bold red]📝 Invalid request[/bold red]: '{api_key[:10]}...{api_key[-10:]}'")
                return "unknown_error"
                
            else:
                # 其他状态码
                rich.print(f"[bold red]❌ HTTP {response.status_code}[/bold red]: '{api_key[:10]}...{api_key[-10:]}'")
                return "unknown_error"
        
        except httpx.TimeoutException:
            # 请求超时（临时性错误）
            rich.print(f"[bold orange_red1]⏱️ Request timeout[/bold orange_red1]: '{api_key[:10]}...{api_key[-10:]}'")
            return "service_unavailable"
            
        except httpx.ConnectError:
            # 连接错误（临时性错误）
            rich.print(f"[bold orange_red1]🌐 Connection error[/bold orange_red1]: '{api_key[:10]}...{api_key[-10:]}'")
            return "service_unavailable"
            
        except httpx.HTTPError as e:
            # 其他HTTP错误
            rich.print(f"[bold orange_red1]🌐 HTTP error[/bold orange_red1]: {e} - '{api_key[:10]}...{api_key[-10:]}'")
            return "service_unavailable"
            
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
            # 基础硅基流动关键词
            "siliconflow", "silicon flow", "silicon-flow", "silicon_flow",
            "硅基流动", "硅基", "流动", "siliconcloud", "silicon cloud",
            
            # 支持的模型
            "deepseek", "deepseek-chat", "deepseek-coder", "deepseek-v2", "deepseek-v3",
            "qwen", "qwen2", "qwen-plus", "qwen-turbo", "qwen-max", "qwen2.5",
            "llama", "llama2", "llama3", "llama-2", "llama-3", "llama3.1", "llama3.2",
            "baichuan", "baichuan2", "baichuan-13b", "baichuan2-13b", "baichuan2-7b",
            "chatglm", "chatglm2", "chatglm3", "chatglm4", "glm-4", "glm-4v",
            "yi", "yi-34b", "yi-6b", "01-ai", "零一万物",
            
            # 中文大模型
            "中文大模型", "中文模型", "chinese llm", "chinese model", "中文ai",
            "国产大模型", "国产模型", "中国大模型", "本土模型", "自主模型",
            "通义千问", "文心一言", "讯飞星火", "百川", "智谱", "月之暗面",
            "面壁智能", "零一万物", "商汤", "旷视", "云从", "依图",
            
            # API和服务相关
            "siliconflow api", "siliconflow-api", "silicon_flow_api",
            "api.siliconflow.cn", "siliconflow.cn", "silicon-flow.com",
            "chat/completions", "completions", "embedding", "embeddings",
            "models", "model", "stream", "streaming", "非流式", "流式",
            
            # 认证和密钥
            "api key", "api-key", "apikey", "api_key", "密钥", "秘钥",
            "access token", "access_token", "token", "令牌", "访问令牌",
            "bearer", "authorization", "auth", "认证", "授权", "鉴权",
            "sk-", "SILICONFLOW_API_KEY", "SILICON_FLOW_API_KEY",
            
            # 开发和集成
            "openai compatible", "openai兼容", "兼容openai", "openai接口",
            "替代openai", "openai替换", "国产替代", "本土化", "私有化部署",
            "私有化", "本地部署", "edge deployment", "边缘部署",
            
            # 编程语言和框架
            "python", "javascript", "nodejs", "node.js", "typescript", "java",
            "go", "rust", "php", "ruby", "swift", "kotlin", "dart",
            "langchain", "llamaindex", "transformers", "huggingface", "pytorch",
            "tensorflow", "paddle", "mindspore", "oneflow", "megengine",
            
            # 应用场景
            "对话系统", "聊天机器人", "智能客服", "内容生成", "文本生成",
            "代码生成", "代码补全", "翻译", "摘要", "问答系统", "知识图谱",
            "文档处理", "数据分析", "情感分析", "文本分类", "实体识别",
            
            # 技术特性
            "多模态", "multimodal", "视觉理解", "图像理解", "视频理解",
            "语音识别", "语音合成", "tts", "asr", "ocr", "文字识别",
            "函数调用", "function calling", "工具调用", "tool use",
            "代码执行", "code execution", "插件", "plugin", "扩展",
            
            # 性能和优化
            "推理优化", "inference optimization", "加速", "acceleration",
            "量化", "quantization", "蒸馏", "distillation", "压缩", "compression",
            "并行", "parallel", "分布式", "distributed", "集群", "cluster",
            "gpu", "cuda", "tensorrt", "onnx", "openvino", "triton",
            
            # 配置和部署
            "配置", "config", "configuration", "设置", "settings", "环境变量",
            "environment", "env", "docker", "kubernetes", "k8s", "helm",
            "terraform", "ansible", "nginx", "load balancer", "负载均衡",
            
            # 错误和调试
            "error", "exception", "错误", "异常", "调试", "debug",
            "timeout", "超时", "rate limit", "限流", "quota", "配额",
            "billing", "计费", "usage", "使用量", "监控", "monitoring",
            
            # 开源和社区
            "开源", "open source", "github", "gitlab", "社区", "community",
            "贡献", "contribution", "issue", "pull request", "fork", "star",
            "license", "许可证", "apache", "mit", "gpl", "bsd",
            
            # 安全和合规
            "安全", "security", "隐私", "privacy", "数据保护", "data protection",
            "合规", "compliance", "审计", "audit", "日志", "logging",
            "加密", "encryption", "解密", "decryption", "ssl", "tls",
            
            # 特定术语
            "上下文长度", "context length", "窗口大小", "window size",
            "温度", "temperature", "采样", "sampling", "beam search",
            "贪婪搜索", "greedy search", "核采样", "nucleus sampling",
            "重复惩罚", "repetition penalty", "长度惩罚", "length penalty",
            
            # 行业应用
            "金融", "finance", "医疗", "healthcare", "教育", "education",
            "电商", "e-commerce", "游戏", "gaming", "娱乐", "entertainment",
            "新闻", "news", "媒体", "media", "法律", "legal", "政务", "government"
        ] 