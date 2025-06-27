import httpx
import asyncio
from collections import defaultdict

from .decorators import rate_limited


class WildberriesParser:
    """
    Парсит Wildberries используя WB API и httpx.
    """
    def __init__(self, search_query: str):
        self.search_query = search_query
        self.base_url = "https://www.wildberries.ru"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        self.session = httpx.AsyncClient(headers=self.headers)
        self.products_info = defaultdict(dict)

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()

    @rate_limited(100)
    # TODO добавить кеш
    async def _fetch_page(self, url: str) -> dict:
        """
        Получает карточки товаров со страницы.
        """
        response = await self.session.get(url)
        catalog = response.json()
        return catalog
    
    async def _get_products_info(self, data: dict):
        """
        Выбирает нужную информацию из карточек товаров.
        """
        products = data.get('data').get('products')
        
        for product in products:
            try:
                id = product.get('id')
                price_info = product['sizes'][0]['price']
                self.products_info[id] = {
                    'name': product['name'], 
                    'rating': product['rating'], 
                    'feedbacks': product['feedbacks'], 
                    'price': price_info['basic'], 
                    'discounter_price': price_info['product'],
                    }
            except (KeyError, IndexError):
                continue
        
        return
    
    async def parse(self) -> dict:
        page = 1
        url = f"https://search.wb.ru/exactmatch/ru/common/v13/search?ab_testing=false&appType=1&curr=rub&dest=-2228364&hide_dtype=13&lang=ru&page={page}&query={self.search_query}&resultset=catalog"
        while True:
            catalog = await self._fetch_page(url)
            if not catalog or len(catalog.get('data').get('products')) <= 0:
                break
            await self._get_products_info(catalog)
            page += 1
            
        return self.products_info