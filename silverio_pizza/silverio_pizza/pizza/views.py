from django.db import transaction
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from .models import Pizza, PizzaMasterPiece
from .serializers import PizzaSerializer, PizzaMasterPieceSerializer
from .permissions import IsChefUser, IsOwnerUser
from .services import PizzaService
from ..topping.models import Topping
from ..topping.serializers import ToppingSerializer


class PizzaView(viewsets.ViewSet):
    """
    A Viewset to CRUD pizzas
    """

    queryset = Pizza.objects.all()
    serializer_class = PizzaSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=PizzaSerializer)
    def list(self, request):
        self.queryset = Pizza.objects.all()
        serializer = PizzaSerializer(self.queryset, many=True)
        return Response(serializer.data)

    @extend_schema(request=PizzaSerializer, responses={201: PizzaSerializer, 400: OpenApiResponse(
        response=PizzaSerializer,
        examples=[
            OpenApiExample(
                "Duplicate Pizza",
                value={"error": "Duplicate Pizza: <name>"},
                status_codes=[400],
                response_only=True,
            ),
            OpenApiExample(
                "Duplicate Toppings",
                value={"error": "Toppings already exist for another pizza"},
                status_codes=[400],
                response_only=True,
            ),
            OpenApiExample(
                "Topping Does Not Exist",
                value={"error": "Topping {topping_name} does not exist"},
                status_codes=[400],
                response_only=True,
            )
        ],
    ), 403: OpenApiResponse(
        response=PizzaSerializer,
        examples=[
            OpenApiExample(
                "Forbidden",
                value={"detail": "Authentication credentials were not provided."},
                status_codes=[403],
                response_only=True,
            ),
            OpenApiExample(
                "Not Owner",
                value={"detail": "Only chefs are allowed to create pizzas."},
                status_codes=[403],
                response_only=True,
            )
        ],
    ),
                                                       })
    def create(self, request):
        if not IsChefUser().has_permission(request, self):
            raise PermissionDenied("Only chefs are allowed to create pizzas.")
        pizza = PizzaService.create_pizza_with_toppings(request.data)
        pizza_serializer = PizzaSerializer(pizza)

        return Response(pizza_serializer.data, status=201)

    @extend_schema(responses=ToppingSerializer)
    def partial_update(self, request, pk=None):
        if not IsChefUser().has_permission(request, self):
            raise PermissionDenied("Only chefs are allowed to create pizzas.")

        pizza = Pizza.objects.get(pk=pk)
        serializer = PizzaSerializer(pizza, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(pizza, serializer.validated_data)
        return Response(serializer.data)

    @extend_schema(responses=PizzaSerializer)
    def destroy(self, request, pk=None):
        if not IsChefUser().has_permission(request, self):
            raise PermissionDenied("Only chefs are allowed to delete pizzas.")

        try:
            pizza = Pizza.objects.get(pk=pk)
            pizza.delete()
            return Response(status=204)

        except Pizza.DoesNotExist:
            return Response({'error': f'Pizza {pk} does not exist'}, status=404)

    @extend_schema(responses=PizzaSerializer)
    def retrieve(self, request, pk):
        try:
            pizza = Pizza.objects.get(pk=pk)
            serializer = PizzaSerializer(pizza)
            return Response(serializer.data)
        except Pizza.DoesNotExist:
            return Response({'error': 'Pizza not found'}, status=404)

class PizzaMasterPieceView(viewsets.ViewSet):
    """
    A Viewset to view all pizza masterpieces
    """

    queryset = PizzaMasterPiece.objects.all()

    @extend_schema(responses=PizzaMasterPieceSerializer)
    def list(self, request):
        serializer = PizzaMasterPieceSerializer(self.queryset, many=True)
        return Response(serializer.data)
