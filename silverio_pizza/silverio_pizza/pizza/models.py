import uuid

from django.db import models



# Create your models here.
class Pizza(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4 )
    name = models.CharField(max_length=100, unique=True)
    toppings = models.ManyToManyField('topping.Topping', through='PizzaMasterPiece')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name


class PizzaMasterPiece(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    topping = models.ForeignKey('topping.Topping', on_delete=models.CASCADE, to_field="name")

    class Meta:
        unique_together = ('pizza', 'topping')
