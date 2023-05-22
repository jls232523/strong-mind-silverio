# services.py
from django.db import transaction, IntegrityError
from django.db.models import Count
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response

from .models import Pizza
from .serializers import PizzaSerializer
from ..topping.models import Topping


class PizzaService:
    @staticmethod
    def create_pizza_with_toppings(data):
        pizza_serializer = PizzaSerializer(data=data)
        pizza_serializer.is_valid(raise_exception=True)
        name = pizza_serializer.validated_data['name']

        # validate pizza name is unique
        if Pizza.objects.filter(name=name).exists():
            raise ValidationError({'error': f'Duplicate Pizza: {name}'}, code='invalid')

        toppings_data = pizza_serializer.validated_data.pop('toppings', [])
        validated_toppings = []

        # validate pizza toppings exist
        for topping_data in toppings_data:
            topping_name = topping_data.get('name')
            try:
                topping = Topping.objects.get(name=topping_name)
                validated_toppings.append(topping)
            except Topping.DoesNotExist:
                raise NotFound({'error': f'Topping {topping_name} does not exist'}, code='invalid')

        try:
            with transaction.atomic():
                pizza = pizza_serializer.save()
                pizza.toppings.clear()
                pizza.toppings.add(*validated_toppings)

                # Check for duplicate toppings in other pizzas
                duplicate_pizzas = Pizza.objects.annotate(num_toppings=Count('toppings')).filter(
                    num_toppings=len(validated_toppings)
                ).exclude(pk=pizza.pk)

                # Check if any duplicate pizzas have the same exact toppings
                for duplicate_pizza in duplicate_pizzas:
                    duplicate_toppings = duplicate_pizza.toppings.all()
                    if set(duplicate_toppings) == set(validated_toppings):
                        raise IntegrityError('Topping combination already exists in another pizza.')

        except IntegrityError:
            raise ValidationError({'error': 'Toppings already exist for another pizza'}, code='invalid')

        return pizza
