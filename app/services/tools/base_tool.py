"""Base Tool with caching and retry logic for API calls"""

import os
import json
import hashlib
import time
from typing import Any, Dict, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class DataCache:
    """Simple file-based caching for API responses"""
    
    def __init__(self, cache_dir: str = ".cache/api_cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_cache_key(self, key_str: str) -> str:
        """Generate a unique cache key from input string"""
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve cached data if exists and not expired"""
        cache_key = self._get_cache_key(key)
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check expiration
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                # Cache expired, remove file
                cache_path.unlink()
                return None
            
            logger.debug(f"Cache hit for key: {key[:50]}...")
            return cache_data['data']
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Cache read error: {e}")
            # Remove corrupted cache file
            cache_path.unlink(missing_ok=True)
            return None
    
    def set(self, key: str, data: Any) -> None:
        """Store data in cache"""
        cache_key = self._get_cache_key(key)
        cache_path = self._get_cache_path(cache_key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'key': key[:100],  # Store first 100 chars for debugging
            'data': data
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Cache set for key: {key[:50]}...")
        except Exception as e:
            logger.error(f"Cache write error: {e}")
    
    def clear(self) -> None:
        """Clear all cache files"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        logger.info("Cache cleared")


class RobustRequests:
    """HTTP requests with retry logic and better error handling"""
    
    @staticmethod
    def create_session(
        total_retries: int = 3,
        backoff_factor: float = 1.0,
        status_forcelist: tuple = (429, 500, 502, 503, 504)
    ) -> requests.Session:
        """Create a requests session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=total_retries,
            read=total_retries,
            connect=total_retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    @staticmethod
    def get_with_retry(
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = 30,
        **kwargs
    ) -> requests.Response:
        """Make GET request with automatic retry on failure"""
        session = RobustRequests.create_session()
        
        try:
            response = session.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout,
                **kwargs
            )
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for URL: {url}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for URL: {url}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code} for URL: {url}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for URL {url}: {e}")
            raise
        finally:
            session.close()


def with_cache(cache: DataCache):
    """Decorator to add caching to a function"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call the actual function
            result = func(*args, **kwargs)
            
            # Store in cache if successful
            if result and not isinstance(result, str) or (isinstance(result, str) and not result.startswith("오류")):
                cache.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


def rate_limit(calls_per_second: float = 1.0):
    """Decorator to rate limit function calls"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator


class EnhancedBaseTool:
    """Base class for tools with caching and retry capabilities"""
    
    def __init__(self, cache_ttl_hours: int = 24, enable_cache: bool = True):
        self.enable_cache = enable_cache
        if enable_cache:
            cache_dir = os.getenv("CACHE_DIR", ".cache/tools")
            self.cache = DataCache(cache_dir=cache_dir, ttl_hours=cache_ttl_hours)
        else:
            self.cache = None
        
        self.session = RobustRequests.create_session()
    
    def get_cached_or_fetch(
        self,
        cache_key: str,
        fetch_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Get data from cache or fetch if not cached"""
        if self.cache and self.enable_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
        
        # Fetch new data
        result = fetch_func(*args, **kwargs)
        
        # Cache the result
        if self.cache and self.enable_cache and result:
            self.cache.set(cache_key, result)
        
        return result
    
    def make_api_request(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = 30
    ) -> requests.Response:
        """Make API request with retry logic"""
        return RobustRequests.get_with_retry(
            url=url,
            params=params,
            headers=headers,
            timeout=timeout
        )


# Cache configurations for different data types
CACHE_CONFIGS = {
    "academic": {"ttl_hours": 72},      # 3 days for academic papers
    "statistics": {"ttl_hours": 24},    # 1 day for economic stats
    "news": {"ttl_hours": 1},           # 1 hour for news
    "social": {"ttl_hours": 0.5},       # 30 minutes for social media
}


def get_cache_for_type(data_type: str) -> DataCache:
    """Get appropriate cache instance for data type"""
    config = CACHE_CONFIGS.get(data_type, {"ttl_hours": 24})
    cache_dir = f".cache/{data_type}"
    return DataCache(cache_dir=cache_dir, ttl_hours=config["ttl_hours"])