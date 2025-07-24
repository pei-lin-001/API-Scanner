"""
Base vendor class for API key scanning and validation
"""

import re
from abc import ABC, abstractmethod
from typing import List, Tuple


class BaseVendor(ABC):
    """
    Abstract base class for API key vendors
    """
    
    def __init__(self):
        self.name = self.get_vendor_name()
        self.regex_patterns = self.get_regex_patterns()
        self.db_filename = f"{self.name.lower()}_keys.db"
    
    @abstractmethod
    def get_vendor_name(self) -> str:
        """
        Get the vendor name
        
        Returns:
            str: Vendor name
        """
        pass
    
    @abstractmethod
    def get_regex_patterns(self) -> List[Tuple[re.Pattern, bool, bool]]:
        """
        Get regex patterns for this vendor
        
        Returns:
            List[Tuple[re.Pattern, bool, bool]]: List of (pattern, too_many_results, too_long)
        """
        pass
    
    @abstractmethod
    def validate_key(self, api_key: str) -> str:
        """
        Validate an API key for this vendor
        
        Args:
            api_key (str): The API key to validate
            
        Returns:
            str: Validation status ('yes', 'permission_denied', 'resource_exhausted', etc.)
        """
        pass
    
    @abstractmethod
    def get_search_keywords(self) -> List[str]:
        """
        Get search keywords specific to this vendor
        
        Returns:
            List[str]: List of keywords
        """
        pass
    
    def get_database_filename(self) -> str:
        """
        Get the database filename for this vendor
        
        Returns:
            str: Database filename
        """
        return self.db_filename
    
    def get_display_name(self) -> str:
        """
        Get the display name for this vendor
        
        Returns:
            str: Display name
        """
        return self.name 