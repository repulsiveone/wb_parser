from django.db import models


class CardModel(models.Model):
    name = models.CharField("название", max_length=300)
    price = models.IntegerField()
    discounter_price = models.IntegerField()
    rating = models.IntegerField()
    feedbacks = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['price']),
            models.Index(fields=['rating']),
        ]