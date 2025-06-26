from rest_framework import serializers
from models import CardModel


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardModel
        fields = ['name', 'price', 'discounter_price', 'rating', 'feedback']