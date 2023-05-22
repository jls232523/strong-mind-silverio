from django.db import transaction, IntegrityError
from django.db.models import Count
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from .models import Pizza, PizzaMasterPiece
from ..topping.models import Topping
from ..topping.serializers import ToppingSerializer


class PizzaSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100)
    toppings = ToppingSerializer(many=True)  # Nested serializer for toppings

    @staticmethod
    def validate_name(value):
        return value.lower()

    def update(self, instance, validated_data):
        toppings_data = validated_data.pop('toppings', [])
        # Update pizza fields
        instance.name = validated_data.get('name', instance.name)
        # Update other fields as needed
        instance.save()  # Save pizza instance first

        validated_toppings = []

        # validate pizza toppings exist
        for topping_data in toppings_data:
            topping_name = topping_data.get('name')
            try:
                topping = Topping.objects.get(name=topping_name)
                validated_toppings.append(topping)
            except Topping.DoesNotExist:
                raise NotFound({'error': f'Topping {topping_name} does not exist'}, code='invalid')

        # Validate pizza toppings are unique across different pizzas
        try:
            with transaction.atomic():
                instance.toppings.clear()
                instance.toppings.add(*validated_toppings)

                # Check for duplicate toppings in other pizzas
                duplicate_toppings = Pizza.objects.annotate(num_toppings=Count('toppings')).filter(
                    num_toppings=len(validated_toppings), toppings__in=validated_toppings).exclude(pk=instance.pk)
                if duplicate_toppings.exists():
                    raise IntegrityError('Duplicate toppings found in other pizzas.')

        except IntegrityError:
            raise ValidationError({'error': 'Toppings already exist for another pizza'}, code='invalid')

        return instance

    class Meta:
        model = Pizza
        fields = "__all__"


class PizzaMasterPieceSerializer(serializers.ModelSerializer):
    pizza = PizzaSerializer()
    topping = ToppingSerializer()

    class Meta:
        model = PizzaMasterPiece
        fields = "__all__"
