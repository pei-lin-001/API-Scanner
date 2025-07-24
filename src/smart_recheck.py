#!/usr/bin/env python3
"""
智能API密钥重检脚本

基于智能状态管理系统，只重新检查那些有可能恢复的密钥。
区分临时性和永久性错误，避免浪费时间检查已永久失效的密钥。
"""

import argparse
import sys
import time
from datetime import datetime

import rich
from rich.console import Console
from rich.table import Table

# 添加src目录到路径
sys.path.insert(0, '.')

from src.vendor_factory import VendorFactory
from src.utils import recheck_failed_keys, get_key_status_report
from src.key_status_manager import get_key_status_manager

console = Console()


def display_status_dashboard():
    """显示状态仪表板"""
    status_manager = get_key_status_manager()
    
    # 获取统计信息
    overall_summary = status_manager.get_status_summary()
    vendor_summary = status_manager.get_vendor_summary()
    retryable_keys = status_manager.get_retryable_keys()
    
    # 创建总览表格
    table = Table(title="🔑 API Key Status Dashboard", show_header=True)
    table.add_column("Status", style="cyan", min_width=20)
    table.add_column("Count", justify="right", style="magenta")
    table.add_column("Description", style="white")
    
    status_descriptions = {
        "yes": "✅ Available and working",
        "authentication_error": "❌ Invalid/expired (permanent)",
        "permission_denied": "🚫 Access denied (permanent)",
        "rate_limit_exceeded": "⚠️ Rate limited (temporary)",
        "resource_exhausted": "🔥 Resources exhausted (temporary)",
        "insufficient_quota": "💰 Quota insufficient (may recover)",
        "service_unavailable": "🔧 Service down (temporary)",
        "internal_error": "⚙️ Server error (temporary)",
        "unknown_error": "❓ Unknown issue (may recover)"
    }
    
    for status, count in overall_summary.items():
        description = status_descriptions.get(status, "Unknown status")
        table.add_row(status, str(count), description)
    
    console.print(table)
    
    # 显示可重试密钥信息
    if retryable_keys:
        console.print(f"\n🔄 [bold green]{len(retryable_keys)}[/bold green] keys are ready for retry")
    else:
        console.print(f"\n⏰ [yellow]No keys are currently ready for retry[/yellow]")
    
    # 按厂商显示详细信息
    if vendor_summary:
        console.print(f"\n📊 [bold]Breakdown by Vendor:[/bold]")
        for vendor_name, stats in vendor_summary.items():
            total_keys = sum(stats.values())
            available_keys = stats.get('yes', 0)
            percentage = (available_keys / total_keys * 100) if total_keys > 0 else 0
            
            console.print(f"  🏭 [cyan]{vendor_name}[/cyan]: {available_keys}/{total_keys} available ({percentage:.1f}%)")


def smart_recheck_vendor(vendor_name: str) -> tuple[int, int]:
    """
    智能重检指定厂商的密钥
    
    Args:
        vendor_name: 厂商名称
        
    Returns:
        tuple[int, int]: (检查的密钥数量, 恢复的密钥数量)
    """
    factory = VendorFactory()
    vendor = factory.get_vendor(vendor_name)
    
    if not vendor:
        console.print(f"[bold red]❌ Unknown vendor: {vendor_name}[/bold red]")
        return 0, 0
    
    console.print(f"\n🔍 [bold]Smart rechecking {vendor.name} keys...[/bold]")
    
    # 执行智能重检
    checked_count, recovered_count = recheck_failed_keys(vendor)
    
    if checked_count == 0:
        console.print(f"⏰ No {vendor.name} keys are ready for retry at this time")
    else:
        success_rate = (recovered_count / checked_count * 100) if checked_count > 0 else 0
        console.print(f"📈 Recovery rate: {success_rate:.1f}% ({recovered_count}/{checked_count})")
    
    return checked_count, recovered_count


def smart_recheck_all() -> dict:
    """
    智能重检所有厂商的密钥
    
    Returns:
        dict: 各厂商的检查结果
    """
    factory = VendorFactory()
    vendors = factory.get_available_vendors()
    
    results = {}
    total_checked = 0
    total_recovered = 0
    
    console.print(f"\n🚀 [bold]Smart rechecking all vendors...[/bold]")
    
    for vendor_name, vendor in vendors.items():
        checked, recovered = smart_recheck_vendor(vendor_name)
        results[vendor_name] = (checked, recovered)
        total_checked += checked
        total_recovered += recovered
    
    # 显示总体结果
    console.print(f"\n📊 [bold]Overall Results:[/bold]")
    console.print(f"  🔍 Total keys checked: {total_checked}")
    console.print(f"  ✅ Total keys recovered: {total_recovered}")
    
    if total_checked > 0:
        overall_success_rate = (total_recovered / total_checked * 100)
        console.print(f"  📈 Overall recovery rate: {overall_success_rate:.1f}%")
    
    return results


def analyze_key(api_key: str):
    """分析特定密钥的状态"""
    status_manager = get_key_status_manager()
    analysis = status_manager.get_error_analysis(api_key)
    
    if not analysis:
        console.print(f"[yellow]No tracking data found for key {api_key[:10]}...[/yellow]")
        return
    
    # 创建分析表格
    table = Table(title=f"🔍 Analysis for Key {api_key[:10]}...", show_header=True)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Current Status", analysis['current_status'])
    table.add_row("Vendor", analysis['vendor'])
    table.add_row("Is Permanent Error", "Yes" if analysis['is_permanent'] else "No")
    table.add_row("Is Temporary Error", "Yes" if analysis['is_temporary'] else "No")
    table.add_row("Is Quota Related", "Yes" if analysis['is_quota_related'] else "No")
    table.add_row("Retry Count", str(analysis['retry_count']))
    table.add_row("Last Check", analysis['last_check'].strftime('%Y-%m-%d %H:%M:%S'))
    
    if analysis['next_retry_time']:
        table.add_row("Next Retry", analysis['next_retry_time'].strftime('%Y-%m-%d %H:%M:%S'))
    
    if analysis.get('error_duration_hours'):
        table.add_row("Error Duration", f"{analysis['error_duration_hours']:.1f} hours")
    
    table.add_row("Recommendation", analysis['recommendation'])
    
    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="Smart API Key Recheck Tool")
    parser.add_argument(
        "--vendor", 
        choices=["openai", "gemini", "siliconflow", "all"],
        help="Vendor to recheck (default: all)"
    )
    parser.add_argument(
        "--status", 
        action="store_true",
        help="Show status dashboard only"
    )
    parser.add_argument(
        "--analyze",
        type=str,
        help="Analyze specific API key"
    )
    parser.add_argument(
        "--report",
        action="store_true", 
        help="Generate detailed status report"
    )
    parser.add_argument(
        "--cleanup",
        type=int,
        default=7,
        help="Cleanup old tracking data (days, default: 7)"
    )
    
    args = parser.parse_args()
    
    console.print("🤖 [bold blue]Smart API Key Recheck Tool[/bold blue]")
    console.print("=" * 50)
    
    # 清理旧数据
    if args.cleanup > 0:
        status_manager = get_key_status_manager()
        cleaned_count = status_manager.cleanup_old_keys(args.cleanup)
        if cleaned_count > 0:
            console.print(f"🧹 Cleaned up {cleaned_count} old tracking records")
    
    # 显示状态仪表板
    if args.status:
        display_status_dashboard()
        return
    
    # 分析特定密钥
    if args.analyze:
        analyze_key(args.analyze)
        return
    
    # 生成详细报告
    if args.report:
        report = get_key_status_report()
        console.print(report)
        return
    
    # 显示当前状态
    display_status_dashboard()
    
    # 执行智能重检
    if args.vendor == "all" or args.vendor is None:
        results = smart_recheck_all()
    else:
        checked, recovered = smart_recheck_vendor(args.vendor)
        results = {args.vendor: (checked, recovered)}
    
    # 显示更新后的状态
    console.print(f"\n📊 [bold]Updated Status:[/bold]")
    display_status_dashboard()
    
    # 提供后续建议
    console.print(f"\n💡 [bold]Tips:[/bold]")
    console.print("  • 临时性错误的密钥会在适当时间自动重试")
    console.print("  • 永久性错误的密钥不会重试，建议更换")
    console.print("  • 配额不足的密钥可能在充值后恢复")
    console.print("  • 使用 --analyze <key> 查看特定密钥的详细状态")


if __name__ == "__main__":
    main() 