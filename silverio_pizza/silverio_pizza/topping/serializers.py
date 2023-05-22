from rest_framework import serializers

from .models import Topping


class ToppingSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100)

    @staticmethod
    def validate_name(value):
        return value.lower()

    class Meta:
        model = Topping
        fields = "__all__"
