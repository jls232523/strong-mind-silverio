import pytest

pytestmark = pytest.mark.django_db


class TestPizzaModel:
    def test_str_method(self, pizza_factory):
        factory = pizza_factory(name="test_pizza")

        assert factory.__str__() == "test_pizza"


class TestPizzaMasterPieceModel:
    pass

