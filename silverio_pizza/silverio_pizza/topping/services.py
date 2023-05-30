# services.py
from django.db import transaction, IntegrityError
from django.db.models import Count
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response

from .models import Topping
from .serializers import ToppingSerializer
from ..pizza.models import Pizza, PizzaMasterPiece
from ..topping.models import Topping




class ToppingService:

    @staticmethod
    def update_topping_name(topping_id, new_name):
        try:
            topping = Topping.objects.get(id=topping_id)
            oldPizzas = None
            if topping.pizza_set.exists():
                oldPizzas = list(topping.pizza_set.all())
                # Remove the topping from associated pizzas
                for pizza in topping.pizza_set.all():
                    pizza.toppings.remove(topping)
            topping.name = new_name
            topping.save()
            # Re-add the updated topping to associated pizzas, if needed
            if oldPizzas:
                for pizza in oldPizzas:
                    PizzaMasterPiece.objects.create(pizza=pizza, topping=topping)

            return topping
        except Topping.DoesNotExist:
            raise NotFound({'error': f'Topping does not exist'}, code='invalid')
        except IntegrityError:
            raise NotFound({'error': f'Topping already exists'}, code='invalid')
