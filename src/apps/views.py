from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from asgiref.sync import async_to_sync
from django.shortcuts import render

from .models import CardModel
from .utils.parser import WildberriesParser
from .filters import ProductFilter
from .serializers import ProductSerializer


class ProductView(viewsets.ModelViewSet):
    # TODO добавить вывод по категории товара
    queryset = CardModel.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilter

    @action(detail=False, methods=['post'])
    def parse_products(self, request):
        """
        Получает словарь с информацией о товарах через WildberriesParser.
        """
        category = request.data.get('category')

        try:
            products_data = async_to_sync(self._run_async_parser)(category)
            for product in list(products_data.values()):
                CardModel.objects.update_or_create(
                    name=product['name'],
                    price=product['price'],
                    discounter_price=product['discounter_price'],
                    rating=product['rating'],
                    feedbacks=product['feedbacks']
                )
            return Response({
                "status": "success",
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    async def _run_async_parser(self, category: str) -> dict:
        async with WildberriesParser(category) as parser:
            return await parser.parse()
        
def main(request):
    return render(request, 'index.html')