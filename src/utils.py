"""
Utility functions for API key validation and management
"""

import rich
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vendors.base import BaseVendor

def check_key_with_vendor(vendor: "BaseVendor", api_key: str) -> str:
    """
    使用指定厂商验证API密钥，并集成智能状态管理
    
    Args:
        vendor: 厂商实例
        api_key: 要验证的API密钥
        
    Returns:
        str: 验证状态
    """
    from key_status_manager import get_key_status_manager
    
    status_manager = get_key_status_manager()
    
    # 执行密钥验证
    status = vendor.validate_key(api_key)
    
    # 更新密钥状态到管理器
    status_manager.update_key_status(api_key, status, vendor.name)
    
    # 如果是临时性错误，标记为可重试
    if status in ["rate_limit_exceeded", "resource_exhausted", "service_unavailable", 
                  "internal_error", "insufficient_quota", "unknown_error"]:
        # 不立即标记重试，让状态管理器决定重试时机
        pass
    
    return status


def recheck_failed_keys(vendor: "BaseVendor") -> tuple[int, int]:
    """
    重新检查失败的密钥，仅检查那些可以重试的
    
    Args:
        vendor: 厂商实例
        
    Returns:
        tuple[int, int]: (重新检查的密钥数量, 恢复的密钥数量)
    """
    from key_status_manager import get_key_status_manager
    from manager import DatabaseManager
    
    status_manager = get_key_status_manager()
    
    # 获取该厂商的数据库管理器
    db_manager = DatabaseManager(vendor.get_database_filename(), vendor.name)
    
    with db_manager as mgr:
        # 获取所有非可用状态的密钥
        failed_keys = mgr.get_keys_by_status(['authentication_error', 'permission_denied', 
                                            'rate_limit_exceeded', 'resource_exhausted',
                                            'insufficient_quota', 'service_unavailable',
                                            'internal_error', 'unknown_error'])
    
    if not failed_keys:
        rich.print(f"📋 No failed keys found for {vendor.name}")
        return 0, 0
    
    # 过滤出可重试的密钥
    retryable_keys = []
    for key_data in failed_keys:
        api_key = key_data[0]  # 假设密钥是第一个字段
        if status_manager.should_retry_key(api_key):
            retryable_keys.append(api_key)
    
    if not retryable_keys:
        rich.print(f"⏰ No keys ready for retry for {vendor.name}")
        return 0, 0
    
    rich.print(f"🔄 Rechecking {len(retryable_keys)} retryable keys for {vendor.name}...")
    
    recovered_count = 0
    
    for api_key in retryable_keys:
        rich.print(f"🔍 Rechecking key {api_key[:10]}...")
        
        # 标记开始重试
        status_manager.mark_key_for_retry(api_key)
        
        # 重新验证密钥
        new_status = check_key_with_vendor(vendor, api_key)
        
        # 更新数据库状态
        with db_manager as mgr:
            mgr.update_key_status(api_key, new_status)
        
        if new_status == "yes":
            recovered_count += 1
            rich.print(f"✅ Key {api_key[:10]}... recovered!")
        else:
            rich.print(f"❌ Key {api_key[:10]}... still failed: {new_status}")
    
    rich.print(f"📊 Recheck summary for {vendor.name}: {recovered_count}/{len(retryable_keys)} keys recovered")
    
    return len(retryable_keys), recovered_count


def get_key_status_report() -> str:
    """
    生成密钥状态报告
    
    Returns:
        str: 格式化的状态报告
    """
    from key_status_manager import get_key_status_manager
    
    status_manager = get_key_status_manager()
    
    # 获取整体状态摘要
    overall_summary = status_manager.get_status_summary()
    vendor_summary = status_manager.get_vendor_summary()
    
    report_lines = []
    report_lines.append("🔑 API Key Status Report")
    report_lines.append("=" * 40)
    
    # 整体统计
    report_lines.append("\n📊 Overall Statistics:")
    for status, count in overall_summary.items():
        status_icon = {
            "yes": "✅",
            "authentication_error": "❌",
            "permission_denied": "🚫", 
            "rate_limit_exceeded": "⚠️",
            "resource_exhausted": "🔥",
            "insufficient_quota": "💰",
            "service_unavailable": "🔧",
            "internal_error": "⚙️",
            "unknown_error": "❓"
        }.get(status, "❔")
        
        report_lines.append(f"  {status_icon} {status}: {count}")
    
    # 按厂商统计
    report_lines.append("\n🏭 By Vendor:")
    for vendor_name, vendor_stats in vendor_summary.items():
        report_lines.append(f"\n  📂 {vendor_name}:")
        for status, count in vendor_stats.items():
            status_icon = {
                "yes": "✅",
                "authentication_error": "❌",
                "permission_denied": "🚫",
                "rate_limit_exceeded": "⚠️", 
                "resource_exhausted": "🔥",
                "insufficient_quota": "💰",
                "service_unavailable": "🔧",
                "internal_error": "⚙️",
                "unknown_error": "❓"
            }.get(status, "❔")
            
            report_lines.append(f"    {status_icon} {status}: {count}")
    
    # 可重试密钥统计
    retryable_keys = status_manager.get_retryable_keys()
    if retryable_keys:
        report_lines.append(f"\n🔄 Retryable Keys: {len(retryable_keys)}")
    
    return "\n".join(report_lines)


# Legacy function for backward compatibility
def check_key(api_key: str) -> str:
    """
    Legacy function for Gemini key validation
    
    This function is deprecated. Use check_key_with_vendor instead.
    """
    from vendor_factory import VendorFactory
    
    factory = VendorFactory()
    gemini_vendor = factory.get_vendor('gemini')
    
    if gemini_vendor:
        return check_key_with_vendor(gemini_vendor, api_key)
    else:
        rich.print("[bold red]❌ Gemini vendor not available[/bold red]")
        return "unknown_error"
