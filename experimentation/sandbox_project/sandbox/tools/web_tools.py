import asyncio
from typing import Dict, List, Optional
import httpx
from playwright.async_api import async_playwright
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider

class WebsiteSpider(Spider):
    name = 'website_spider'
    
    def __init__(self, url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        self.content = []

    def parse(self, response):
        # Extract text content
        text = ' '.join(response.css('*::text').getall())
        self.content.append(text)
        
        # Follow links within same domain
        for href in response.css('a::attr(href)').getall():
            if href.startswith('/') or response.url in href:
                yield response.follow(href, self.parse)

async def scrape_website(url: str) -> str:
    """Scrape entire website and return content as markdown"""
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0',
        'LOG_LEVEL': 'ERROR'
    })
    
    spider = WebsiteSpider(url)
    process.crawl(spider)
    process.start()
    
    return '\n\n'.join(spider.content)

async def web_search(query: str, api_key: str, cx: str) -> List[str]:
    """Perform web search using Google Custom Search API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'https://www.googleapis.com/customsearch/v1',
            params={
                'key': api_key,
                'cx': cx,
                'q': query
            }
        )
        data = response.json()
        return [item['link'] for item in data.get('items', [])]

async def extract_data_from_website(url: str, selectors: Dict[str, str]) -> Dict[str, str]:
    """Extract specific data from website using browser automation"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        
        result = {}
        for key, selector in selectors.items():
            try:
                element = await page.wait_for_selector(selector)
                result[key] = await element.text_content()
            except:
                result[key] = None
        
        await browser.close()
        return result