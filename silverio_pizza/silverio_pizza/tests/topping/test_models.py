import pytest

pytestmark = pytest.mark.django_db


class TestToppingModel:
    def test_str_method(self, topping_factory):
        factory = topping_factory(name="test_top")

        assert factory.__str__() == "test_top"



