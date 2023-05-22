import factory

from ..pizza.models import Pizza, PizzaMasterPiece
from ..topping.models import Topping


class PizzaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Pizza

    name = factory.Sequence(lambda n: "test_pizza_%d" % n)


class ToppingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Topping

    name = factory.Sequence(lambda n: "test_topping_%d" % n)


class PizzaMasterPieceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PizzaMasterPiece

    pizza = factory.SubFactory(PizzaFactory)
    topping = factory.SubFactory(ToppingFactory)
