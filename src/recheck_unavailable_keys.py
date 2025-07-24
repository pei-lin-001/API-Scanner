"""
Re-check unavailable API keys for multiple vendors
"""

import argparse
from concurrent.futures import ThreadPoolExecutor

import rich
from tqdm import tqdm

from manager import DatabaseManager
from utils import check_key_with_vendor
from vendor_factory import VendorFactory


def recheck_keys(vendor_name: str = None):
    """
    Re-check all unavailable keys in the database for specified vendor(s).
    """
    factory = VendorFactory()
    
    if vendor_name == "all" or vendor_name is None:
        vendors = list(factory.get_available_vendors().values())
        rich.print("[bold yellow]Re-checking keys for all vendors...[/bold yellow]")
    else:
        vendor = factory.get_vendor(vendor_name)
        if not vendor:
            rich.print(f"[bold red]Unknown vendor: {vendor_name}[/bold red]")
            return
        vendors = [vendor]
        rich.print(f"[bold yellow]Re-checking keys for {vendor.name}...[/bold yellow]")
    
    for vendor in vendors:
        rich.print(f"\n🔍 Processing {vendor.name} vendor...")
        
        db_manager = DatabaseManager(vendor.get_database_filename(), vendor.name)
        with db_manager as mgr:
            keys_to_recheck = mgr.all_unavailable_keys()

        if not keys_to_recheck:
            rich.print(f"[bold yellow]No unavailable keys to re-check for {vendor.name}.[/bold yellow]")
            continue

        # Extract the key string from each tuple
        keys = [key[0] for key in keys_to_recheck]
        rich.print(f"Found {len(keys)} unavailable {vendor.name} keys to re-check.")

        def check_single_key(key):
            return check_key_with_vendor(vendor, key)

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(
                tqdm(
                    executor.map(check_single_key, keys),
                    total=len(keys),
                    desc=f"Re-checking {vendor.name} keys",
                )
            )

        with db_manager as mgr:
            for key, status in zip(keys, results):
                mgr.delete(key)
                mgr.insert(key, status)
        
        rich.print(f"[bold green]Finished re-checking all unavailable {vendor.name} keys.[/bold green]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Re-check unavailable API keys for multiple vendors.")
    parser.add_argument(
        "--vendor",
        type=str,
        default="all",
        help="The vendor to re-check keys for (openai, gemini, siliconflow, or all). Default: all",
    )
    args = parser.parse_args()
    recheck_keys(vendor_name=args.vendor)