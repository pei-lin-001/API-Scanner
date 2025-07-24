"""
Vendor factory for managing different API key vendors
"""

from typing import Dict, List, Optional

import rich
from rich.console import Console
from rich.table import Table

from vendors import BaseVendor, OpenAIVendor, GeminiVendor, SiliconFlowVendor


class VendorFactory:
    """
    Factory class for managing API key vendors
    """
    
    def __init__(self):
        self._vendors: Dict[str, BaseVendor] = {
            "openai": OpenAIVendor(),
            "gemini": GeminiVendor(), 
            "siliconflow": SiliconFlowVendor()
        }
    
    def get_available_vendors(self) -> Dict[str, BaseVendor]:
        """
        Get all available vendors
        
        Returns:
            Dict[str, BaseVendor]: Dictionary of vendor name to vendor instance
        """
        return self._vendors.copy()
    
    def get_vendor(self, vendor_name: str) -> Optional[BaseVendor]:
        """
        Get a specific vendor by name
        
        Args:
            vendor_name (str): Name of the vendor
            
        Returns:
            Optional[BaseVendor]: Vendor instance or None if not found
        """
        return self._vendors.get(vendor_name.lower())
    
    def display_vendor_menu(self) -> str:
        """
        Display interactive vendor selection menu
        
        Returns:
            str: Selected vendor name
        """
        console = Console()
        
        # Create table showing available vendors
        table = Table(title="🔍 API Key Scanner - 选择厂商", show_header=True, header_style="bold magenta")
        table.add_column("序号", style="cyan", width=6)
        table.add_column("厂商名称", style="green", width=15) 
        table.add_column("描述", style="yellow", width=40)
        table.add_column("数据库文件", style="blue", width=20)
        
        vendors_list = list(self._vendors.items())
        
        for idx, (key, vendor) in enumerate(vendors_list, 1):
            descriptions = {
                "openai": "OpenAI GPT-3/4 API Keys",
                "gemini": "Google Gemini AI API Keys", 
                "siliconflow": "硅基流动 API Keys"
            }
            table.add_row(
                str(idx),
                vendor.get_display_name(),
                descriptions.get(key, ""),
                vendor.get_database_filename()
            )
        
        table.add_row("0", "全部", "扫描所有厂商的 API Keys", "各自独立数据库")
        
        console.print(table)
        console.print()
        
        while True:
            try:
                choice = input("请选择要扫描的厂商 (输入序号): ").strip()
                
                if choice == "0":
                    return "all"
                elif choice.isdigit():
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(vendors_list):
                        vendor_key = vendors_list[choice_idx][0]
                        selected_vendor = vendors_list[choice_idx][1]
                        rich.print(f"✅ 已选择: [bold green]{selected_vendor.get_display_name()}[/bold green]")
                        rich.print(f"📂 数据库文件: [blue]{selected_vendor.get_database_filename()}[/blue]")
                        return vendor_key
                
                rich.print("[bold red]❌ 无效选择，请重新输入![/bold red]")
                
            except (ValueError, KeyboardInterrupt):
                rich.print("[bold red]❌ 输入错误或操作被取消![/bold red]")
                continue
    
    def get_vendors_for_scanning(self, selection: str) -> List[BaseVendor]:
        """
        Get vendors based on user selection
        
        Args:
            selection (str): User selection ("all" or specific vendor name)
            
        Returns:
            List[BaseVendor]: List of vendors to scan
        """
        if selection == "all":
            return list(self._vendors.values())
        else:
            vendor = self.get_vendor(selection)
            return [vendor] if vendor else [] 