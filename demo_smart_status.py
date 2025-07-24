#!/usr/bin/env python3
"""
智能API密钥状态管理系统演示

演示新的状态管理系统如何智能区分临时性和永久性错误，
避免浪费时间重试已永久失效的密钥。
"""

import sys
import time
from datetime import datetime

import rich
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# 添加src目录到路径
sys.path.insert(0, 'src')

from vendor_factory import VendorFactory
from key_status_manager import get_key_status_manager
from utils import check_key_with_vendor

console = Console()

def demo_key_validation():
    """演示密钥验证和状态管理"""
    console.print(Panel.fit("🤖 智能API密钥状态管理系统演示", style="bold blue"))
    
    factory = VendorFactory()
    status_manager = get_key_status_manager()
    
    # 获取厂商
    openai_vendor = factory.get_vendor('openai')
    gemini_vendor = factory.get_vendor('gemini') 
    siliconflow_vendor = factory.get_vendor('siliconflow')
    
    if not openai_vendor:
        console.print("[red]❌ OpenAI vendor not available[/red]")
        return
    
    console.print("\n📋 演示不同类型的API密钥验证和错误分类...\n")
    
    # 演示密钥样本（这些都是无效的演示密钥）
    demo_keys = [
        {
            'vendor': openai_vendor,
            'key': 'sk-invalid_key_demo_authentication_error_12345',
            'expected': 'authentication_error',
            'description': '无效的OpenAI密钥 (认证错误 - 永久性)'
        },
        {
            'vendor': gemini_vendor,
            'key': 'AIzaSy_invalid_demo_key_1234567890123456789',
            'expected': 'authentication_error', 
            'description': '无效的Gemini密钥 (认证错误 - 永久性)'
        },
        {
            'vendor': siliconflow_vendor,
            'key': 'sk-invalid_demo_key_abcdefghijklmnopqrstuvwxyz123456',
            'expected': 'authentication_error',
            'description': '无效的硅基流动密钥 (认证错误 - 永久性)'
        }
    ]
    
    # 验证演示密钥
    for i, demo in enumerate(demo_keys, 1):
        console.print(f"🔍 [{i}/{len(demo_keys)}] 验证 {demo['description']}")
        
        # 验证密钥
        result = check_key_with_vendor(demo['vendor'], demo['key'])
        
        # 显示结果
        if result == demo['expected']:
            console.print(f"  ✅ 符合预期: {result}")
        else:
            console.print(f"  ⚠️  结果: {result} (预期: {demo['expected']})")
        
        time.sleep(1)  # 避免请求过快
    
    console.print("\n📊 查看状态管理器统计...\n")
    
    # 显示状态统计
    summary = status_manager.get_status_summary()
    vendor_summary = status_manager.get_vendor_summary()
    
    if summary:
        table = Table(title="📈 密钥状态统计", show_header=True)
        table.add_column("状态", style="cyan")
        table.add_column("数量", justify="right", style="magenta")
        table.add_column("类型", style="white")
        
        status_types = {
            "yes": "✅ 可用",
            "authentication_error": "❌ 永久失效",
            "permission_denied": "🚫 永久失效",
            "rate_limit_exceeded": "⚠️ 临时错误",
            "resource_exhausted": "🔥 临时错误", 
            "insufficient_quota": "💰 可能恢复",
            "service_unavailable": "🔧 临时错误",
            "internal_error": "⚙️ 临时错误",
            "unknown_error": "❓ 可能恢复"
        }
        
        for status, count in summary.items():
            status_type = status_types.get(status, "❔ 未知")
            table.add_row(status, str(count), status_type)
        
        console.print(table)
    
    # 显示按厂商分组的统计
    if vendor_summary:
        console.print(f"\n🏭 按厂商分组统计:")
        for vendor_name, stats in vendor_summary.items():
            console.print(f"  📂 {vendor_name}:")
            for status, count in stats.items():
                console.print(f"    • {status}: {count}")
    
    # 演示智能重试判断
    console.print(f"\n🧠 智能重试判断演示...")
    
    retryable_keys = status_manager.get_retryable_keys()
    if retryable_keys:
        console.print(f"  🔄 {len(retryable_keys)} 个密钥可以重试")
    else:
        console.print(f"  ⏰ 暂时没有密钥准备好重试")
        console.print(f"  💡 系统会根据错误类型智能安排重试时间:")
        console.print(f"     • 认证错误/权限不足: 永不重试 (已失效)")
        console.print(f"     • 速率限制: 5分钟后重试")
        console.print(f"     • 资源耗尽: 30分钟后重试")
        console.print(f"     • 服务不可用: 10分钟后重试")
        console.print(f"     • 配额不足: 1小时后重试")

def demo_error_analysis():
    """演示错误分析功能"""
    console.print(Panel.fit("🔍 错误分析演示", style="bold green"))
    
    status_manager = get_key_status_manager()
    
    # 获取所有跟踪的密钥
    if not status_manager.key_tracking:
        console.print("[yellow]没有找到跟踪的密钥数据[/yellow]")
        return
    
    # 分析第一个密钥作为示例
    api_key = list(status_manager.key_tracking.keys())[0]
    analysis = status_manager.get_error_analysis(api_key)
    
    if analysis:
        table = Table(title=f"🔍 密钥分析: {api_key[:10]}...", show_header=True)
        table.add_column("属性", style="cyan")
        table.add_column("值", style="white")
        
        table.add_row("当前状态", analysis['current_status'])
        table.add_row("厂商", analysis['vendor'])
        table.add_row("是否永久失效", "是" if analysis['is_permanent'] else "否")
        table.add_row("是否临时错误", "是" if analysis['is_temporary'] else "否")
        table.add_row("是否配额相关", "是" if analysis['is_quota_related'] else "否")
        table.add_row("重试次数", str(analysis['retry_count']))
        table.add_row("最后检查", analysis['last_check'].strftime('%Y-%m-%d %H:%M:%S'))
        
        if analysis['next_retry_time']:
            table.add_row("下次重试", analysis['next_retry_time'].strftime('%Y-%m-%d %H:%M:%S'))
        
        if analysis.get('error_duration_hours'):
            table.add_row("错误持续时间", f"{analysis['error_duration_hours']:.1f} 小时")
        
        table.add_row("建议", analysis['recommendation'])
        
        console.print(table)

def main():
    console.print("🚀 [bold]开始智能API密钥状态管理系统演示[/bold]\n")
    
    try:
        # 演示密钥验证
        demo_key_validation()
        
        console.print("\n" + "="*50 + "\n")
        
        # 演示错误分析
        demo_error_analysis()
        
        console.print(f"\n✨ [bold green]演示完成![/bold green]")
        console.print(f"\n💡 [bold]关键优势:[/bold]")
        console.print(f"  🎯 智能错误分类 - 区分临时性和永久性错误")
        console.print(f"  ⏰ 智能重试调度 - 根据错误类型安排重试时间") 
        console.print(f"  🔄 指数退避重试 - 避免过度请求")
        console.print(f"  📊 详细状态跟踪 - 完整的错误历史和分析")
        console.print(f"  💰 成本节约 - 避免重试已失效的密钥")
        
        console.print(f"\n🛠️  [bold]使用方法:[/bold]")
        console.print(f"  • python src/smart_recheck.py --status  # 查看状态")
        console.print(f"  • python src/smart_recheck.py --vendor openai  # 重检OpenAI")
        console.print(f"  • python src/smart_recheck.py --analyze <key>  # 分析特定密钥")
        
    except KeyboardInterrupt:
        console.print(f"\n[yellow]演示被用户中断[/yellow]")
    except Exception as e:
        console.print(f"\n[red]演示过程中出现错误: {e}[/red]")

if __name__ == "__main__":
    main() 