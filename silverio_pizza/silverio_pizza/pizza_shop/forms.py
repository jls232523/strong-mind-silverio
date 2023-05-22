from django import forms

from ..pizza.models import Pizza
from ..topping.models import Topping


class PizzaForm(forms.Form):
    name = forms.CharField(label='Pizza Name', max_length=100)
    toppings = forms.ModelMultipleChoiceField(
        queryset=Topping.objects.all(),
        label='Toppings',
        widget=forms.CheckboxSelectMultiple,
    )

class ToppingForm(forms.Form):
    name = forms.CharField(label='Topping Name', max_length=100)
