"""
Multi-Vendor API Key Scanner for GitHub
Supports OpenAI, Gemini, and SiliconFlow API keys
"""

import argparse
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List

import rich
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

from manager import CookieManager, DatabaseManager, ProgressManager
from utils import check_key_with_vendor
from vendor_factory import VendorFactory
from vendors.base import BaseVendor

FORMAT = "%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="[%X]")
log = logging.getLogger("API-Scanner")
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)


class MultiVendorAPIKeyScanner:
    """
    Multi-vendor API Key Scanner for GitHub
    """

    def __init__(self, vendors: List[BaseVendor]):
        self.vendors = vendors
        self.driver: webdriver.Chrome | None = None
        self.cookies: CookieManager | None = None
        
        # Initialize database managers for each vendor
        self.dbmgrs = {}
        for vendor in vendors:
            self.dbmgrs[vendor.name] = DatabaseManager(
                vendor.get_database_filename(), 
                vendor.name
            )
        
        # Build candidate URLs for all vendors
        self.candidate_urls = []
        self._build_search_urls()

    def _build_search_urls(self):
        """
        Build search URLs for all vendors using enhanced search configuration
        """
        # Import enhanced search configuration
        from search_config import get_comprehensive_search_config
        
        search_config = get_comprehensive_search_config()
        
        # Enhanced paths to search in - comprehensive coverage
        PATHS = search_config["paths"]
        
        # Enhanced languages - maximum coverage
        LANGUAGES = search_config["languages"]
        
        # Additional search patterns for specific filenames
        FILENAME_PATTERNS = [
            f"filename:{filename}" for filename in search_config["filenames"]
        ]
        
        for vendor in self.vendors:
            rich.print(f"🔍 Building search URLs for [bold]{vendor.name}[/bold]")
            
            for regex, too_many_results, _ in vendor.regex_patterns:
                # Strategy 1: Search in specific file paths
                for path in PATHS:
                    self.candidate_urls.append({
                        'url': f"https://github.com/search?q=(/{regex.pattern}/)+AND+({path})&type=code&ref=advsearch",
                        'vendor': vendor
                    })

                # Strategy 2: Search by programming languages
                for language in LANGUAGES:
                    if too_many_results:  # Use AND condition for high-volume patterns
                        self.candidate_urls.append({
                            'url': f"https://github.com/search?q=(/{regex.pattern}/)+language:{language}&type=code&ref=advsearch",
                            'vendor': vendor
                        })
                    else:  # Simple search for low-volume patterns
                        self.candidate_urls.append({
                            'url': f"https://github.com/search?q=(/{regex.pattern}/)&type=code&ref=advsearch",
                            'vendor': vendor
                        })
                
                # Strategy 3: Search in specific filename patterns
                for filename_pattern in FILENAME_PATTERNS:
                    self.candidate_urls.append({
                        'url': f"https://github.com/search?q=(/{regex.pattern}/)+{filename_pattern}&type=code&ref=advsearch",
                        'vendor': vendor
                    })
                
                # Strategy 4: Combine vendor-specific keywords with regex patterns
                vendor_keywords = vendor.get_search_keywords()
                for keyword in vendor_keywords[:10]:  # Limit to top 10 keywords to avoid too many URLs
                    if too_many_results:
                        self.candidate_urls.append({
                            'url': f"https://github.com/search?q=(/{regex.pattern}/)+{keyword}&type=code&ref=advsearch",
                            'vendor': vendor
                        })
                
                # Strategy 5: Search with code patterns that commonly contain API keys
                code_patterns = search_config["code_patterns"]
                for pattern in code_patterns[:5]:  # Limit to avoid overwhelming number of URLs
                    if "sk-" in pattern or "AIzaSy" in pattern:  # Only use relevant patterns
                        self.candidate_urls.append({
                            'url': f"https://github.com/search?q=(/{regex.pattern}/)+\"{pattern}\"&type=code&ref=advsearch",
                            'vendor': vendor
                        })
            
            rich.print(f"📊 Generated {len([url for url in self.candidate_urls if url['vendor'] == vendor])} search URLs for {vendor.name}")
        
        total_urls = len(self.candidate_urls)
        rich.print(f"🎯 [bold green]Total search URLs generated: {total_urls}[/bold green]")
        rich.print(f"⏱️  Estimated scan time: {total_urls * 0.5:.1f} minutes (assuming 30s per URL)")

    def login_to_github(self):
        """
        Login to GitHub
        """
        rich.print("🌍 Opening Chrome ...")

        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(3)

        self.cookies = CookieManager(self.driver)

        cookie_exists = os.path.exists("cookies.pkl")
        self.driver.get("https://github.com/login")

        if not cookie_exists:
            rich.print("🤗 No cookies found, please login to GitHub first")
            input("Press Enter after you logged in: ")
            self.cookies.save()
        else:
            rich.print("🍪 Cookies found, loading cookies")
            self.cookies.load()

        self.cookies.verify_user_login()

    def _expand_all_code(self):
        """
        Expand all the code in the current page
        """
        elements = self.driver.find_elements(by=By.XPATH, value="//*[contains(text(), 'more match')]")
        for element in elements:
            element.click()

    def _find_urls_and_apis(self, vendor: BaseVendor) -> tuple[list[str], list[str]]:
        """
        Find all the URLs and APIs in the current page for a specific vendor
        """
        apis_found = []
        urls_need_expand = []

        codes = self.driver.find_elements(by=By.CLASS_NAME, value="code-list")  # type: ignore
        for element in codes:
            apis = []
            # Check all regex for this vendor's patterns
            for regex, _, too_long in vendor.regex_patterns:
                if not too_long:
                    apis.extend(regex.findall(element.text))

            if len(apis) == 0:
                # Need to show full code. (because the api key is too long)
                # get the <a> tag
                a_tag = element.find_element(by=By.XPATH, value=".//a")
                urls_need_expand.append(a_tag.get_attribute("href"))
            apis_found.extend(apis)

        return apis_found, urls_need_expand

    def _process_url(self, url_data: dict):
        """
        Process a search query URL for a specific vendor
        """
        if self.driver is None:
            raise ValueError("Driver is not initialized")

        url = url_data['url']
        vendor = url_data['vendor']
        
        rich.print(f"🔍 Processing {vendor.name}: {url[:80]}...")
        self.driver.get(url)

        while True:  # Loop until all the pages are processed
            # If current webpage is reached the rate limit, then wait for 30 seconds
            if self.driver.find_elements(by=By.XPATH, value="//*[contains(text(), 'You have exceeded a secondary rate limit')]"):
                for _ in tqdm(range(30), desc="⏳ Rate limit reached, waiting ..."):
                    time.sleep(1)
                self.driver.refresh()
                continue

            self._expand_all_code()

            apis_found, urls_need_expand = self._find_urls_and_apis(vendor)
            rich.print(f"    🌕 There are {len(urls_need_expand)} URLs waiting to be expanded for {vendor.name}")

            try:
                next_buttons = self.driver.find_elements(by=By.XPATH, value="//a[@aria-label='Next Page']")
                if next_buttons:
                    rich.print("🔍 Clicking next page")
                    WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Next Page']")))
                    next_buttons = self.driver.find_elements(by=By.XPATH, value="//a[@aria-label='Next Page']")
                    next_buttons[0].click()
                else:
                    break
            except Exception:  # pylint: disable=broad-except
                rich.print("⚪️ No more pages")
                break

        # Handle the expand_urls
        for u in tqdm(urls_need_expand, desc=f"🔍 Expanding URLs for {vendor.name} ..."):
            if self.driver is None:
                raise ValueError("Driver is not initialized")

            with self.dbmgrs[vendor.name] as mgr:
                if mgr.get_url(u):
                    rich.print(f"    🔑 skipping url '{u[:10]}...{u[-10:]}'")
                    continue

            self.driver.get(u)
            time.sleep(3)  # TODO: find a better way to wait for the page to load # pylint: disable=fixme

            retry = 0
            while retry <= 3:
                matches = []
                for regex, _, _ in vendor.regex_patterns:
                    matches.extend(regex.findall(self.driver.page_source))
                matches = list(set(matches))

                if len(matches) == 0:
                    rich.print(f"    ⚪️ No matches found in the expanded page, retrying [{retry}/3]...")
                    retry += 1
                    time.sleep(3)
                    continue

                with self.dbmgrs[vendor.name] as mgr:
                    new_apis = [api for api in matches if not mgr.key_exists(api)]
                    new_apis = list(set(new_apis))
                apis_found.extend(new_apis)
                rich.print(f"    🔬 Found {len(matches)} matches in the expanded page, adding them to the list")
                for match in matches:
                    rich.print(f"        '{match[:10]}...{match[-10:]}'")

                with self.dbmgrs[vendor.name] as mgr:
                    mgr.insert_url(u)
                break

        self.check_api_keys_and_save(vendor, apis_found)

    def check_api_keys_and_save(self, vendor: BaseVendor, keys: list[str]):
        """
        Check a list of API keys for a specific vendor
        """
        with self.dbmgrs[vendor.name] as mgr:
            unique_keys = list(set(keys))
            unique_keys = [api for api in unique_keys if not mgr.key_exists(api)]

        def check_single_key(key):
            return check_key_with_vendor(vendor, key)

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(check_single_key, unique_keys))
            with self.dbmgrs[vendor.name] as mgr:
                for idx, result in enumerate(results):
                    mgr.insert(unique_keys[idx], result)

    def search(self, from_iter: int | None = None):
        """
        Search for API keys, and save the results to the database
        """
        progress = ProgressManager()
        total = len(self.candidate_urls)
        pbar = tqdm(
            enumerate(self.candidate_urls),
            total=total,
            desc="🔍 Searching ...",
        )
        if from_iter is None:
            from_iter = progress.load(total=total)

        for idx, url_data in enumerate(self.candidate_urls):
            if idx < from_iter:
                pbar.update()
                time.sleep(0.05)  # let tqdm print the bar
                log.debug("⚪️ Skip %s", url_data['url'])
                continue
            self._process_url(url_data)
            progress.save(idx, total)
            log.debug("🔍 Finished %s", url_data['url'])
            pbar.update()
        pbar.close()

    def deduplication(self):
        """
        Deduplicate all vendor databases
        """
        for vendor in self.vendors:
            with self.dbmgrs[vendor.name] as mgr:
                mgr.deduplicate()

    def update_existed_keys(self):
        """
        Update previously checked API keys in all vendor databases
        """
        for vendor in self.vendors:
            with self.dbmgrs[vendor.name] as mgr:
                rich.print(f"🔄 Updating existed keys for {vendor.name}")
                keys = mgr.all_keys()
                for key in tqdm(keys, desc=f"🔄 Updating {vendor.name} keys ..."):
                    result = check_key_with_vendor(vendor, key[0])
                    mgr.delete(key[0])
                    mgr.insert(key[0], result)

    def update_iq_keys(self):
        """
        Update insufficient quota keys for all vendors
        """
        for vendor in self.vendors:
            with self.dbmgrs[vendor.name] as mgr:
                rich.print(f"🔄 Updating insufficient quota keys for {vendor.name}")
                keys = mgr.all_iq_keys()
                for key in tqdm(keys, desc=f"🔄 Updating {vendor.name} insufficient quota keys ..."):
                    result = check_key_with_vendor(vendor, key[0])
                    mgr.delete(key[0])
                    mgr.insert(key[0], result)

    def get_all_available_keys(self) -> dict:
        """
        Get all available keys from all vendors
        
        Returns:
            dict: Dictionary mapping vendor names to their available keys
        """
        all_keys = {}
        for vendor in self.vendors:
            with self.dbmgrs[vendor.name] as mgr:
                vendor_keys = mgr.all_keys()
                all_keys[vendor.name] = vendor_keys
        return all_keys

    def __del__(self):
        if hasattr(self, "driver") and self.driver is not None:
            self.driver.quit()


def main(from_iter: int | None = None, check_existed_keys_only: bool = False, 
         check_insuffcient_quota: bool = False, vendor_selection: str | None = None):
    """
    Main function to scan GitHub for available API Keys from multiple vendors
    """
    factory = VendorFactory()
    
    # Get vendor selection
    if vendor_selection is None:
        vendor_selection = factory.display_vendor_menu()
    
    vendors = factory.get_vendors_for_scanning(vendor_selection)
    
    if not vendors:
        rich.print("[bold red]❌ No valid vendors selected![/bold red]")
        return
    
    rich.print(f"🚀 Starting scan for: [bold green]{', '.join([v.name for v in vendors])}[/bold green]")
    
    scanner = MultiVendorAPIKeyScanner(vendors)

    if not check_existed_keys_only:
        scanner.login_to_github()
        scanner.search(from_iter=from_iter)

    if check_insuffcient_quota:
        scanner.update_iq_keys()

    scanner.update_existed_keys()
    scanner.deduplication()
    
    all_keys = scanner.get_all_available_keys()

    # Display results
    total_keys = sum(len(keys) for keys in all_keys.values())
    rich.print(f"\n🔑 [bold green]Scan Complete! Total available keys: {total_keys}[/bold green]")
    
    for vendor_name, keys in all_keys.items():
        if keys:
            rich.print(f"\n📂 [bold cyan]{vendor_name} Keys ({len(keys)}):[/bold cyan]")
            for key in keys:
                rich.print(f"  [bold green]{key[0]}[/bold green]")
        else:
            rich.print(f"\n📂 [bold yellow]{vendor_name}: No available keys found[/bold yellow]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-vendor API Key Scanner")
    parser.add_argument("--from-iter", type=int, default=None, help="Start from the specific iteration")
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug mode, otherwise INFO mode. Default is False (INFO mode)",
    )
    parser.add_argument(
        "-ceko",
        "--check-existed-keys-only",
        action="store_true",
        default=False,
        help="Only check existed keys",
    )
    parser.add_argument(
        "-ciq",
        "--check-insuffcient-quota",
        action="store_true",
        default=False,
        help="Check and update status of the insuffcient quota keys",
    )
    parser.add_argument(
        "--vendor",
        type=str,
        default=None,
        help="Pre-select vendor (openai, gemini, siliconflow, or all)",
    )
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    main(
        from_iter=args.from_iter,
        check_existed_keys_only=args.check_existed_keys_only,
        check_insuffcient_quota=args.check_insuffcient_quota,
        vendor_selection=args.vendor,
    )
