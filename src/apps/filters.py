from django_filters import rest_framework as filters
from django_filters import OrderingFilter

from .models import CardModel

class ProductFilter(filters.FilterSet):
    # Фильтры
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    min_rating = filters.NumberFilter(field_name="rating", lookup_expr='gte')
    max_rating = filters.NumberFilter(field_name="rating", lookup_expr='lte')
    min_feedbacks = filters.NumberFilter(field_name="feedbacks", lookup_expr='gte')
    max_feedbacks = filters.NumberFilter(field_name="feedbacks", lookup_expr='lte')
    
    
    # Сортировка
    o = OrderingFilter(
        fields=(
            ('price', 'price'),
            ('discounter_price', 'discounter_price'),
            ('rating', 'rating'),
            ('feedbacks', 'feedbacks'),
            ('name', 'name')
        )
    )
    
    class Meta:
        model = CardModel
        fields = []