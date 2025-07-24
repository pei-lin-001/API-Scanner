#!/usr/bin/env python3
"""
Test script for Multi-Vendor API Key Scanner

This script tests the vendor factory and individual vendor implementations
without performing actual scanning.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import rich
from rich.console import Console
from rich.table import Table

from vendor_factory import VendorFactory

def test_vendor_factory():
    """Test the vendor factory functionality"""
    console = Console()
    
    rich.print("[bold blue]🧪 Testing Vendor Factory...[/bold blue]")
    
    factory = VendorFactory()
    vendors = factory.get_available_vendors()
    
    rich.print(f"✅ Found {len(vendors)} vendors: {list(vendors.keys())}")
    
    # Test individual vendor access
    for vendor_name, vendor in vendors.items():
        rich.print(f"\n🔍 Testing {vendor_name} vendor...")
        
        # Test basic properties
        rich.print(f"  - Name: {vendor.get_vendor_name()}")
        rich.print(f"  - Display Name: {vendor.get_display_name()}")
        rich.print(f"  - Database File: {vendor.get_database_filename()}")
        
        # Test regex patterns
        patterns = vendor.get_regex_patterns()
        rich.print(f"  - Regex Patterns: {len(patterns)} pattern(s)")
        for i, (pattern, many_results, too_long) in enumerate(patterns):
            rich.print(f"    {i+1}. {pattern.pattern} (many_results={many_results}, too_long={too_long})")
        
        # Test keywords
        keywords = vendor.get_search_keywords()
        rich.print(f"  - Search Keywords: {len(keywords)} keyword(s)")
        rich.print(f"    Examples: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")

def test_vendor_selection():
    """Test vendor selection without actual menu display"""
    rich.print("\n[bold blue]🧪 Testing Vendor Selection...[/bold blue]")
    
    factory = VendorFactory()
    
    # Test all vendors
    all_vendors = factory.get_vendors_for_scanning("all")
    rich.print(f"✅ 'all' selection returns {len(all_vendors)} vendors")
    
    # Test individual vendors
    for vendor_name in ["openai", "gemini", "siliconflow"]:
        vendor_list = factory.get_vendors_for_scanning(vendor_name)
        if vendor_list:
            rich.print(f"✅ '{vendor_name}' selection returns {vendor_list[0].name}")
        else:
            rich.print(f"❌ '{vendor_name}' selection failed")
    
    # Test invalid vendor
    invalid_vendors = factory.get_vendors_for_scanning("invalid")
    rich.print(f"✅ Invalid vendor returns {len(invalid_vendors)} vendors (expected 0)")

def test_regex_patterns():
    """Test regex patterns with sample data"""
    rich.print("\n[bold blue]🧪 Testing Regex Patterns...[/bold blue]")
    
    # Sample test data
    test_data = {
        "openai": [
            "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # Classic OpenAI - 使用安全的占位符
            "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ12",  # Project key
            "sk-abcdefghijklmnopqrstuvwxyz1234567890abcdefghij"  # Organization key
        ],
        "gemini": [
            "AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz123456789",  # Gemini API key
        ],
        "siliconflow": [
            "sk-hlgmghidkyerkaqjeonawwlhpsvizkfsspntjywqkzqehhkp",  # SiliconFlow key 1
            "sk-izdctsmxyxdsypxradjlyvbnrrtyjglaiqfkfsvvognfzbkg",  # SiliconFlow key 2
        ]
    }
    
    factory = VendorFactory()
    vendors = factory.get_available_vendors()
    
    for vendor_name in ["openai", "gemini", "siliconflow"]:
        vendor = vendors[vendor_name]
        patterns = vendor.get_regex_patterns()
        test_keys = test_data.get(vendor_name, [])
        
        rich.print(f"\n🔍 Testing {vendor.name} patterns...")
        
        for key in test_keys:
            matched = False
            for pattern, _, _ in patterns:
                if pattern.search(key):
                    rich.print(f"  ✅ '{key[:20]}...' matches pattern")
                    matched = True
                    break
            if not matched:
                rich.print(f"  ❌ '{key[:20]}...' no match found")

def display_summary():
    """Display a summary table of all vendors"""
    rich.print("\n[bold blue]📊 Vendor Summary[/bold blue]")
    
    factory = VendorFactory()
    vendors = factory.get_available_vendors()
    
    table = Table(title="Multi-Vendor API Key Scanner", show_header=True, header_style="bold magenta")
    table.add_column("Vendor", style="cyan", width=12)
    table.add_column("Patterns", style="green", width=10)
    table.add_column("Keywords", style="yellow", width=10)
    table.add_column("Database", style="blue", width=20)
    
    for vendor_name, vendor in vendors.items():
        table.add_row(
            vendor.get_display_name(),
            str(len(vendor.get_regex_patterns())),
            str(len(vendor.get_search_keywords())),
            vendor.get_database_filename()
        )
    
    console = Console()
    console.print(table)

def main():
    """Main test function"""
    rich.print("[bold green]🚀 Multi-Vendor API Key Scanner - Test Suite[/bold green]\n")
    
    try:
        test_vendor_factory()
        test_vendor_selection()
        test_regex_patterns()
        display_summary()
        
        rich.print("\n[bold green]✅ All tests completed successfully![/bold green]")
        rich.print("\n[bold yellow]📝 To run the actual scanner:[/bold yellow]")
        rich.print("   python src/main.py")
        rich.print("\n[bold yellow]📝 To recheck keys:[/bold yellow]")
        rich.print("   python src/recheck_unavailable_keys.py --vendor all")
        
    except Exception as e:
        rich.print(f"\n[bold red]❌ Test failed with error: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 