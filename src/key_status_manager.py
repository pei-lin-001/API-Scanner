"""
智能API密钥状态管理器

根据各厂商的错误码和状态，智能判断密钥是否应该被重新检查、暂时禁用或永久禁用。
不同的错误状态有不同的处理策略。
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class KeyStatus(Enum):
    """API密钥状态枚举"""
    AVAILABLE = "yes"                          # 可用
    AUTHENTICATION_ERROR = "authentication_error"     # 认证错误 - 永久失效
    PERMISSION_DENIED = "permission_denied"           # 权限不足 - 永久失效  
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"       # 速率限制 - 临时性
    RESOURCE_EXHAUSTED = "resource_exhausted"         # 资源耗尽 - 临时性
    INSUFFICIENT_QUOTA = "insufficient_quota"         # 配额不足 - 可能临时
    SERVICE_UNAVAILABLE = "service_unavailable"       # 服务不可用 - 临时性
    INTERNAL_ERROR = "internal_error"                 # 内部错误 - 临时性
    UNKNOWN_ERROR = "unknown_error"                   # 未知错误 - 可能临时
    TEMPORARILY_DISABLED = "temporarily_disabled"      # 临时禁用
    PENDING_RECHECK = "pending_recheck"               # 等待重新检查


class KeyStatusManager:
    """
    API密钥状态管理器
    
    智能管理API密钥的各种状态，区分临时性和永久性错误，
    并实现智能重试和状态恢复机制。
    """
    
    # 永久性错误 - 密钥已失效，不应重试
    PERMANENT_ERRORS = {
        KeyStatus.AUTHENTICATION_ERROR,
        KeyStatus.PERMISSION_DENIED
    }
    
    # 临时性错误 - 可能恢复，应该重试
    TEMPORARY_ERRORS = {
        KeyStatus.RATE_LIMIT_EXCEEDED,
        KeyStatus.RESOURCE_EXHAUSTED, 
        KeyStatus.SERVICE_UNAVAILABLE,
        KeyStatus.INTERNAL_ERROR,
        KeyStatus.UNKNOWN_ERROR
    }
    
    # 配额相关错误 - 需要特殊处理
    QUOTA_ERRORS = {
        KeyStatus.INSUFFICIENT_QUOTA
    }
    
    # 重试间隔配置（秒）
    RETRY_INTERVALS = {
        KeyStatus.RATE_LIMIT_EXCEEDED: 300,      # 5分钟后重试
        KeyStatus.RESOURCE_EXHAUSTED: 1800,      # 30分钟后重试
        KeyStatus.SERVICE_UNAVAILABLE: 600,      # 10分钟后重试
        KeyStatus.INTERNAL_ERROR: 900,           # 15分钟后重试
        KeyStatus.INSUFFICIENT_QUOTA: 3600,      # 1小时后重试
        KeyStatus.UNKNOWN_ERROR: 1800,           # 30分钟后重试
    }
    
    # 最大重试次数
    MAX_RETRY_ATTEMPTS = {
        KeyStatus.RATE_LIMIT_EXCEEDED: 10,       # 速率限制最多重试10次
        KeyStatus.RESOURCE_EXHAUSTED: 5,         # 资源耗尽最多重试5次
        KeyStatus.SERVICE_UNAVAILABLE: 8,        # 服务不可用最多重试8次
        KeyStatus.INTERNAL_ERROR: 3,             # 内部错误最多重试3次
        KeyStatus.INSUFFICIENT_QUOTA: 3,         # 配额不足最多重试3次
        KeyStatus.UNKNOWN_ERROR: 2,              # 未知错误最多重试2次
    }

    def __init__(self):
        # 密钥状态跟踪 {api_key: {status, last_check, retry_count, next_retry_time, first_error_time}}
        self.key_tracking: Dict[str, Dict] = {}
        
    def update_key_status(self, api_key: str, status: str, vendor_name: str = "") -> None:
        """
        更新API密钥状态
        
        Args:
            api_key: API密钥
            status: 状态字符串
            vendor_name: 厂商名称（用于日志）
        """
        try:
            key_status = KeyStatus(status)
        except ValueError:
            logger.warning(f"Unknown status '{status}' for key {api_key[:10]}..., treating as unknown_error")
            key_status = KeyStatus.UNKNOWN_ERROR
        
        current_time = datetime.now()
        
        if api_key not in self.key_tracking:
            self.key_tracking[api_key] = {
                'status': key_status,
                'last_check': current_time,
                'retry_count': 0,
                'next_retry_time': None,
                'first_error_time': None,
                'vendor': vendor_name
            }
        
        key_info = self.key_tracking[api_key]
        previous_status = key_info['status']
        key_info['status'] = key_status
        key_info['last_check'] = current_time
        key_info['vendor'] = vendor_name
        
        # 如果状态从错误变为可用，重置重试计数
        if key_status == KeyStatus.AVAILABLE:
            key_info['retry_count'] = 0
            key_info['first_error_time'] = None
            key_info['next_retry_time'] = None
            logger.info(f"✅ {vendor_name} key {api_key[:10]}... recovered and is now available")
        
        # 如果是新的错误或错误类型改变，重置重试计数
        elif previous_status != key_status and key_status != KeyStatus.AVAILABLE:
            if key_info['first_error_time'] is None:
                key_info['first_error_time'] = current_time
            key_info['retry_count'] = 0
            
            # 设置下次重试时间
            if key_status in self.RETRY_INTERVALS:
                retry_interval = self.RETRY_INTERVALS[key_status]
                key_info['next_retry_time'] = current_time + timedelta(seconds=retry_interval)
                logger.info(f"⏰ {vendor_name} key {api_key[:10]}... will be rechecked at {key_info['next_retry_time'].strftime('%H:%M:%S')}")
            
            self._log_status_change(api_key, key_status, vendor_name)
    
    def _log_status_change(self, api_key: str, status: KeyStatus, vendor_name: str) -> None:
        """记录状态变化"""
        key_display = f"{api_key[:10]}..."
        
        if status in self.PERMANENT_ERRORS:
            logger.error(f"❌ {vendor_name} key {key_display} permanently failed: {status.value}")
        elif status in self.TEMPORARY_ERRORS:
            logger.warning(f"⚠️ {vendor_name} key {key_display} temporarily failed: {status.value}")
        elif status in self.QUOTA_ERRORS:
            logger.warning(f"💰 {vendor_name} key {key_display} quota issue: {status.value}")
        else:
            logger.info(f"ℹ️ {vendor_name} key {key_display} status: {status.value}")
    
    def should_retry_key(self, api_key: str) -> bool:
        """
        判断密钥是否应该重试
        
        Args:
            api_key: API密钥
            
        Returns:
            bool: 是否应该重试
        """
        if api_key not in self.key_tracking:
            return False
        
        key_info = self.key_tracking[api_key]
        status = key_info['status']
        current_time = datetime.now()
        
        # 可用状态不需要重试
        if status == KeyStatus.AVAILABLE:
            return False
        
        # 永久性错误不重试
        if status in self.PERMANENT_ERRORS:
            return False
        
        # 检查是否到了重试时间
        if key_info['next_retry_time'] and current_time < key_info['next_retry_time']:
            return False
        
        # 检查是否超过最大重试次数
        max_retries = self.MAX_RETRY_ATTEMPTS.get(status, 2)
        if key_info['retry_count'] >= max_retries:
            logger.warning(f"🚫 Key {api_key[:10]}... exceeded max retries ({max_retries}) for {status.value}")
            return False
        
        return True
    
    def mark_key_for_retry(self, api_key: str) -> None:
        """
        标记密钥进行重试
        
        Args:
            api_key: API密钥
        """
        if api_key not in self.key_tracking:
            return
        
        key_info = self.key_tracking[api_key]
        key_info['retry_count'] += 1
        
        # 计算下次重试时间（指数退避）
        status = key_info['status']
        base_interval = self.RETRY_INTERVALS.get(status, 1800)
        # 指数退避：基础间隔 * 2^重试次数
        retry_interval = base_interval * (2 ** min(key_info['retry_count'] - 1, 5))  # 最大32倍
        key_info['next_retry_time'] = datetime.now() + timedelta(seconds=retry_interval)
        
        logger.info(f"🔄 Retry {key_info['retry_count']} for key {api_key[:10]}... next check at {key_info['next_retry_time'].strftime('%H:%M:%S')}")
    
    def get_retryable_keys(self) -> List[str]:
        """
        获取所有可重试的密钥
        
        Returns:
            List[str]: 可重试的密钥列表
        """
        retryable_keys = []
        current_time = datetime.now()
        
        for api_key, key_info in self.key_tracking.items():
            if self.should_retry_key(api_key):
                retryable_keys.append(api_key)
        
        return retryable_keys
    
    def get_status_summary(self) -> Dict[str, int]:
        """
        获取状态摘要
        
        Returns:
            Dict[str, int]: 各状态的密钥数量
        """
        summary = {}
        for key_info in self.key_tracking.values():
            status = key_info['status'].value
            summary[status] = summary.get(status, 0) + 1
        
        return summary
    
    def get_vendor_summary(self) -> Dict[str, Dict[str, int]]:
        """
        获取按厂商分组的状态摘要
        
        Returns:
            Dict[str, Dict[str, int]]: 按厂商分组的状态统计
        """
        vendor_summary = {}
        
        for key_info in self.key_tracking.values():
            vendor = key_info.get('vendor', 'unknown')
            status = key_info['status'].value
            
            if vendor not in vendor_summary:
                vendor_summary[vendor] = {}
            
            vendor_summary[vendor][status] = vendor_summary[vendor].get(status, 0) + 1
        
        return vendor_summary
    
    def cleanup_old_keys(self, max_age_days: int = 7) -> int:
        """
        清理长时间未检查的密钥记录
        
        Args:
            max_age_days: 最大保留天数
            
        Returns:
            int: 清理的密钥数量
        """
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        keys_to_remove = []
        
        for api_key, key_info in self.key_tracking.items():
            if key_info['last_check'] < cutoff_time:
                keys_to_remove.append(api_key)
        
        for api_key in keys_to_remove:
            del self.key_tracking[api_key]
        
        if keys_to_remove:
            logger.info(f"🧹 Cleaned up {len(keys_to_remove)} old key records")
        
        return len(keys_to_remove)
    
    def get_error_analysis(self, api_key: str) -> Optional[Dict]:
        """
        获取密钥的错误分析信息
        
        Args:
            api_key: API密钥
            
        Returns:
            Optional[Dict]: 错误分析信息
        """
        if api_key not in self.key_tracking:
            return None
        
        key_info = self.key_tracking[api_key]
        status = key_info['status']
        
        analysis = {
            'current_status': status.value,
            'is_permanent': status in self.PERMANENT_ERRORS,
            'is_temporary': status in self.TEMPORARY_ERRORS,
            'is_quota_related': status in self.QUOTA_ERRORS,
            'retry_count': key_info['retry_count'],
            'last_check': key_info['last_check'],
            'next_retry_time': key_info['next_retry_time'],
            'first_error_time': key_info['first_error_time'],
            'vendor': key_info.get('vendor', 'unknown')
        }
        
        # 计算错误持续时间
        if key_info['first_error_time']:
            error_duration = datetime.now() - key_info['first_error_time']
            analysis['error_duration_hours'] = error_duration.total_seconds() / 3600
        
        # 提供建议
        if status in self.PERMANENT_ERRORS:
            analysis['recommendation'] = "密钥已永久失效，建议移除或更换"
        elif status in self.TEMPORARY_ERRORS:
            analysis['recommendation'] = "临时性错误，将自动重试"
        elif status in self.QUOTA_ERRORS:
            analysis['recommendation'] = "配额相关问题，建议检查账户余额或升级计划"
        else:
            analysis['recommendation'] = "状态正常或未知错误"
        
        return analysis


# 全局状态管理器实例
global_key_status_manager = KeyStatusManager()


def get_key_status_manager() -> KeyStatusManager:
    """获取全局密钥状态管理器实例"""
    return global_key_status_manager 