import httpx
import asyncio
from collections import defaultdict

from decorators import rate_limited


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
    
    async def _get_products_info(self, data: dict) -> dict:
        """
        Выбирает нужную информацию из карточек товаров.
        """
        products_info_dict = defaultdict(dict)
        products = data.get('data').get('products')
        
        for product in products:
            try:
                id = product.get('id')
                price_info = product['sizes'][0]['price']
                products_info_dict[id] = {
                    'name': product['name'], 
                    'rating': product['rating'], 
                    'feedbacks': product['feedbacks'], 
                    'price': price_info['basic'], 
                    'discounter_price': price_info['product'],
                    }
            except (KeyError, IndexError):
                continue
        
        return products_info_dict
    
    async def parse(self) -> dict:
        url = f"https://search.wb.ru/exactmatch/ru/common/v13/search?ab_testing=false&appType=1&curr=rub&dest=-2228364&hide_dtype=13&lang=ru&page=1&query={self.search_query}&resultset=catalog"
        catalog = await self._fetch_page(url)
        products_info = await self._get_products_info(catalog)
        return products_info
    
    # TODO добавить описания