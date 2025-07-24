#!/usr/bin/env python3
"""
浏览器稳定性测试脚本
"""

import sys
import time
import rich
from rich.console import Console

# 添加src目录到路径
sys.path.insert(0, 'src')

from vendor_factory import VendorFactory
from main import MultiVendorAPIKeyScanner

console = Console()

def test_browser_initialization():
    """测试浏览器初始化"""
    console.print("🧪 [bold blue]测试浏览器初始化[/bold blue]")
    
    try:
        factory = VendorFactory()
        vendors = factory.get_available_vendors()
        siliconflow_vendor = vendors.get('siliconflow')
        
        if not siliconflow_vendor:
            console.print("❌ SiliconFlow vendor not found")
            return False
            
        scanner = MultiVendorAPIKeyScanner([siliconflow_vendor])
        
        console.print("🌍 Starting browser...")
        scanner.login_to_github()
        
        console.print("✅ Browser initialized successfully")
        
        # 测试基本操作
        console.print("🔍 Testing basic operations...")
        
        # 测试页面导航
        scanner.driver.get("https://github.com")
        time.sleep(2)
        
        title = scanner.driver.title
        console.print(f"📄 Page title: {title}")
        
        # 测试连接稳定性
        for i in range(3):
            console.print(f"🔄 Connection test {i+1}/3...")
            try:
                scanner.driver.title
                console.print("    ✅ Connection OK")
            except Exception as e:
                console.print(f"    ❌ Connection failed: {e}")
                return False
            time.sleep(1)
        
        console.print("✅ Browser stability test passed")
        
        # 清理
        scanner.driver.quit()
        return True
        
    except Exception as e:
        console.print(f"❌ Browser test failed: {e}")
        return False

def test_regex_validation():
    """测试正则表达式验证"""
    console.print("\n🧪 [bold blue]测试正则表达式验证[/bold blue]")
    
    # 重新运行正则测试
    try:
        import subprocess
        result = subprocess.run(['python', 'test_regex_patterns.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            console.print("✅ Regex patterns test passed")
            return True
        else:
            console.print(f"❌ Regex patterns test failed: {result.stderr}")
            return False
            
    except Exception as e:
        console.print(f"❌ Failed to run regex test: {e}")
        return False

def main():
    """主测试函数"""
    console.print("🚀 [bold]开始浏览器稳定性测试[/bold]\n")
    
    tests = [
        ("正则表达式测试", test_regex_validation),
        ("浏览器初始化测试", test_browser_initialization)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        console.print(f"\n📋 运行测试: {test_name}")
        console.print("=" * 50)
        
        try:
            if test_func():
                passed += 1
                console.print(f"✅ {test_name} 通过")
            else:
                console.print(f"❌ {test_name} 失败")
        except Exception as e:
            console.print(f"❌ {test_name} 异常: {e}")
    
    console.print(f"\n📊 [bold]测试结果: {passed}/{total} 通过[/bold]")
    
    if passed == total:
        console.print("🎉 [bold green]所有测试通过！浏览器稳定性良好。[/bold green]")
        console.print("\n💡 [bold]建议:[/bold]")
        console.print("  • 您现在可以重新运行扫描程序")
        console.print("  • 如果仍遇到问题，请检查网络连接")
    else:
        console.print("⚠️ [bold yellow]部分测试失败，请检查以下项目:[/bold yellow]")
        console.print("  • Chrome浏览器是否正确安装")
        console.print("  • ChromeDriver是否可用")
        console.print("  • 网络连接是否正常")
        console.print("  • 防火墙设置是否阻止连接")

if __name__ == "__main__":
    main() 