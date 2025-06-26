from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters

from models import CardModel
from utils.parser import WildberriesParser
from filters import ProductFilter
from serializers import ProductSerializer


class ProductView(viewsets.ModelViewSet):
    queryset = CardModel.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (filters.DjangoFilterBackend)
    filterset_class = ProductFilter

    @action(detail=False, methods=['post'])
    async def parse_products(self, request):
        category = request.data.get('category')

        try:
            async with WildberriesParser(category) as parser:
                products_data = await parser.parse()
                for product in products_data:
                    CardModel.objects.create(
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