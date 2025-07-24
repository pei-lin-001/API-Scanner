#!/usr/bin/env python3
"""
测试脚本：验证各厂商的正则表达式模式是否能正确匹配API密钥
"""

import sys
import re

# 添加src目录到路径
sys.path.insert(0, 'src')

from vendor_factory import VendorFactory
import rich
from rich.console import Console
from rich.table import Table

console = Console()

def test_regex_patterns():
    """测试所有厂商的正则表达式模式"""
    console.print("🧪 [bold blue]正则表达式模式测试[/bold blue]")
    console.print("=" * 50)
    
    factory = VendorFactory()
    vendors = factory.get_available_vendors()
    
    # 测试样本密钥（从日志中提取的实际找到的密钥）
    test_samples = {
        'siliconflow': [  # 注意小写
            'sk-ccirpxunsbbhdeivzmkelktowphnsissqixllkfkaxgfbxvy',
            'sk-xuuvwffyuzajucdzjzvqyyqydgedsjivrmdhydcsjjwiditr',
            'sk-panvhifcocckarpiphvetbvjqfacbowfdkobwtwnwwlijkzc',
            'sk-kkwvvfrfvwqsilpjukkbhtgpxyhcavehlkhldkyzkoaoifrb',
            'sk-bmemmhdeetfdxozss',  # shorter key
            'sk-srikmhtvuclhfuyyg'   # shorter key
        ],
        'openai': [  # 注意小写
            'sk-proj-abcd1234567890abcd1234567890abcd1234567890abcd1234567890abcd12',
            'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',  # 使用安全的占位符
            'sk-abcdefghijklmnopqrstuvwxyz1234567890abcdefghij',
            'sk-test_key_12345'
        ],
        'gemini': [  # 注意小写
            'AIzaSyDxVQabc123def456ghi789jkl012mno345',
            'AIzaSy_invalid_demo_key_1234567890123456789',
            'AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz123456789'
        ]
    }
    
    for vendor_name, vendor in vendors.items():
        console.print(f"\n📂 [bold cyan]测试 {vendor_name} 厂商[/bold cyan]")
        
        # 创建测试结果表格
        table = Table(title=f"{vendor_name} 正则表达式测试结果", show_header=True)
        table.add_column("测试密钥", style="yellow", min_width=20)
        table.add_column("模式", style="cyan")
        table.add_column("匹配结果", style="white")
        table.add_column("状态", style="white")
        
        samples = test_samples.get(vendor_name, [])
        patterns = vendor.get_regex_patterns()
        
        console.print(f"🔍 共有 {len(patterns)} 个正则模式")
        console.print(f"🎯 测试 {len(samples)} 个样本密钥")
        
        if not samples:
            console.print(f"⚠️ 没有为 {vendor_name} 提供测试样本")
            continue
        
        total_matches = 0
        total_tests = 0
        
        for sample in samples:
            sample_display = f"{sample[:10]}...{sample[-10:]}" if len(sample) > 20 else sample
            matched = False
            
            for i, (regex, too_many_results, too_long) in enumerate(patterns):
                total_tests += 1
                matches = regex.findall(sample)
                
                if matches:
                    matched = True
                    total_matches += 1
                    table.add_row(
                        sample_display,
                        f"模式 {i+1}",
                        f"✅ 匹配: {matches[0][:20]}...",
                        "✅ 成功"
                    )
                    break
            
            if not matched:
                table.add_row(
                    sample_display,
                    "所有模式",
                    "❌ 无匹配",
                    "❌ 失败"
                )
        
        console.print(table)
        
        # 显示统计信息
        success_rate = (total_matches / len(samples) * 100) if samples else 0
        console.print(f"📊 匹配成功率: {success_rate:.1f}% ({total_matches}/{len(samples)})")
        
        if success_rate < 100:
            console.print(f"⚠️ 建议检查和优化 {vendor_name} 的正则表达式模式")

def test_individual_patterns():
    """测试单个模式的详细信息"""
    console.print(f"\n🔬 [bold green]详细模式分析[/bold green]")
    console.print("=" * 50)
    
    factory = VendorFactory()
    vendors = factory.get_available_vendors()
    
    for vendor_name, vendor in vendors.items():
        console.print(f"\n📂 [bold cyan]{vendor_name} 正则模式详情[/bold cyan]")
        
        patterns = vendor.get_regex_patterns()
        for i, (regex, too_many_results, too_long) in enumerate(patterns):
            console.print(f"  🔸 模式 {i+1}: {regex.pattern}")
            console.print(f"     • 结果过多标志: {too_many_results}")
            console.print(f"     • 过长标志: {too_long}")

def main():
    """主函数"""
    console.print("🚀 [bold]开始正则表达式模式测试[/bold]\n")
    
    try:
        # 测试模式匹配
        test_regex_patterns()
        
        # 显示详细模式信息
        test_individual_patterns()
        
        console.print(f"\n✨ [bold green]测试完成![/bold green]")
        console.print(f"\n💡 [bold]建议:[/bold]")
        console.print(f"  • 如果匹配率低，考虑调整正则表达式模式")
        console.print(f"  • 确保模式能匹配实际在GitHub上找到的密钥格式")
        console.print(f"  • 平衡匹配宽松度和准确性")
        
    except Exception as e:
        console.print(f"\n[red]测试过程中出现错误: {e}[/red]")

if __name__ == "__main__":
    main() 