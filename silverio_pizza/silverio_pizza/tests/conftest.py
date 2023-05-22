import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

from .factories import PizzaMasterPieceFactory, PizzaFactory, ToppingFactory

register(PizzaMasterPieceFactory)
register(PizzaFactory)
register(ToppingFactory)


@pytest.fixture
def api_client():
    return APIClient
