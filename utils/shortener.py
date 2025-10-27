import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class URLShortener:
    """Handle URL shortening operations"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url
    
    async def shorten_url(self, url: str) -> str:
        """
        Shorten URL using configured shortener service
        
        Args:
            url: The URL to shorten
            
        Returns:
            Shortened URL or original URL if shortening fails
        """
        if not self.api_key or not self.base_url:
            logger.warning("Shortener not configured")
            return url
        
        try:
            async with aiohttp.ClientSession() as session:
                api_url = f"{self.base_url}/api"
                params = {
                    "api": self.api_key,
                    "url": url
                }
                
                async with session.get(api_url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        shortened = data.get("shortenedUrl")
                        
                        if shortened:
                            logger.info(f"URL shortened successfully: {url} -> {shortened}")
                            return shortened
                        else:
                            logger.warning("No shortened URL in response")
                            return url
                    else:
                        logger.error(f"Shortener API returned status {response.status}")
                        return url
                        
        except aiohttp.ClientError as e:
            logger.error(f"Network error during URL shortening: {e}")
            return url
        except Exception as e:
            logger.error(f"Unexpected error during URL shortening: {e}")
            return url
    
    async def shorten_cuttly(self, url: str, api_key: str) -> str:
        """
        Shorten URL using Cuttly service
        
        Args:
            url: The URL to shorten
            api_key: Cuttly API key
            
        Returns:
            Shortened URL or original URL if shortening fails
        """
        try:
            async with aiohttp.ClientSession() as session:
                api_url = f"https://cutt.ly/api/api.php"
                params = {
                    "key": api_key,
                    "short": url
                }
                
                async with session.get(api_url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("url", {}).get("status") == 7:
                            shortened = data["url"]["shortLink"]
                            logger.info(f"Cuttly shortened: {url} -> {shortened}")
                            return shortened
                        else:
                            logger.warning(f"Cuttly error: {data.get('url', {}).get('status')}")
                            return url
                    else:
                        return url
                        
        except Exception as e:
            logger.error(f"Cuttly shortening error: {e}")
            return url
    
    async def shorten_bitly(self, url: str, api_key: str) -> str:
        """
        Shorten URL using Bitly service
        
        Args:
            url: The URL to shorten
            api_key: Bitly API access token
            
        Returns:
            Shortened URL or original URL if shortening fails
        """
        try:
            async with aiohttp.ClientSession() as session:
                api_url = "https://api-ssl.bitly.com/v4/shorten"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "long_url": url
                }
                
                async with session.post(api_url, headers=headers, json=payload, timeout=10) as response:
                    if response.status == 200 or response.status == 201:
                        data = await response.json()
                        shortened = data.get("link")
                        
                        if shortened:
                            logger.info(f"Bitly shortened: {url} -> {shortened}")
                            return shortened
                        else:
                            return url
                    else:
                        logger.error(f"Bitly error: {response.status}")
                        return url
                        
        except Exception as e:
            logger.error(f"Bitly shortening error: {e}")
            return url
    
    async def shorten_tinyurl(self, url: str) -> str:
        """
        Shorten URL using TinyURL (no API key required)
        
        Args:
            url: The URL to shorten
            
        Returns:
            Shortened URL or original URL if shortening fails
        """
        try:
            async with aiohttp.ClientSession() as session:
                api_url = f"http://tinyurl.com/api-create.php?url={url}"
                
                async with session.get(api_url, timeout=10) as response:
                    if response.status == 200:
                        shortened = await response.text()
                        
                        if shortened and shortened.startswith("http"):
                            logger.info(f"TinyURL shortened: {url} -> {shortened}")
                            return shortened
                        else:
                            return url
                    else:
                        return url
                        
        except Exception as e:
            logger.error(f"TinyURL shortening error: {e}")
            return url
    
    async def shorten_isgd(self, url: str) -> str:
        """
        Shorten URL using is.gd (no API key required)
        
        Args:
            url: The URL to shorten
            
        Returns:
            Shortened URL or original URL if shortening fails
        """
        try:
            async with aiohttp.ClientSession() as session:
                api_url = "https://is.gd/create.php"
                params = {
                    "format": "simple",
                    "url": url
                }
                
                async with session.get(api_url, params=params, timeout=10) as response:
                    if response.status == 200:
                        shortened = await response.text()
                        
                        if shortened and shortened.startswith("http"):
                            logger.info(f"is.gd shortened: {url} -> {shortened}")
                            return shortened.strip()
                        else:
                            return url
                    else:
                        return url
                        
        except Exception as e:
            logger.error(f"is.gd shortening error: {e}")
            return url
    
    async def shorten_with_retry(self, url: str, services: list = None) -> str:
        """
        Try multiple shortening services with fallback
        
        Args:
            url: The URL to shorten
            services: List of services to try (in order)
            
        Returns:
            Shortened URL from first successful service, or original URL
        """
        if not services:
            services = ['primary', 'tinyurl', 'isgd']
        
        for service in services:
            try:
                if service == 'primary' and self.api_key and self.base_url:
                    result = await self.shorten_url(url)
                    if result != url:
                        return result
                
                elif service == 'tinyurl':
                    result = await self.shorten_tinyurl(url)
                    if result != url:
                        return result
                
                elif service == 'isgd':
                    result = await self.shorten_isgd(url)
                    if result != url:
                        return result
                
            except Exception as e:
                logger.error(f"Error with {service}: {e}")
                continue
        
        logger.warning(f"All shortening services failed for: {url}")
        return url


# Convenience functions
async def shorten_url(url: str, api_key: str = None, shortener_url: str = None) -> str:
    """
    Convenience function to shorten a URL
    
    Args:
        url: URL to shorten
        api_key: API key for shortener service
        shortener_url: Base URL of shortener service
        
    Returns:
        Shortened URL or original URL if shortening fails
    """
    shortener = URLShortener(api_key, shortener_url)
    return await shortener.shorten_url(url)


async def batch_shorten_urls(urls: list, api_key: str = None, shortener_url: str = None) -> list:
    """
    Shorten multiple URLs
    
    Args:
        urls: List of URLs to shorten
        api_key: API key for shortener service
        shortener_url: Base URL of shortener service
        
    Returns:
        List of shortened URLs
    """
    shortener = URLShortener(api_key, shortener_url)
    shortened_urls = []
    
    for url in urls:
        shortened = await shortener.shorten_url(url)
        shortened_urls.append(shortened)
    
    return shortened_urls


async def get_shortener_stats(api_key: str, shortener_url: str) -> Optional[dict]:
    """
    Get statistics from shortener service
    
    Args:
        api_key: API key for shortener service
        shortener_url: Base URL of shortener service
        
    Returns:
        Statistics dictionary or None if request fails
    """
    try:
        async with aiohttp.ClientSession() as session:
            api_url = f"{shortener_url}/api/stats"
            params = {"api": api_key}
            
            async with session.get(api_url, params=params, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
                    
    except Exception as e:
        logger.error(f"Error getting shortener stats: {e}")
        return None
