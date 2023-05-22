from django.contrib.sites import requests
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from django.shortcuts import get_object_or_404

from .models import Topping
from .permissions import IsChefUser, IsOwnerUser
from .serializers import ToppingSerializer
from .services import ToppingService


class ToppingView(viewsets.ViewSet):
    """
    A Viewset to CRUD toppings
    """

    queryset = Topping.objects.all()
    serializer_class = ToppingSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=ToppingSerializer)
    def list(self, request):
        self.queryset = Topping.objects.all()
        serializer = ToppingSerializer(self.queryset, many=True)
        return Response(serializer.data)

    @extend_schema(request=ToppingSerializer, responses={201: ToppingSerializer, 400: OpenApiResponse(
        response=ToppingSerializer,
        examples=[
            OpenApiExample(
                "Duplicate Entry",
                value={"error": "Duplicate Topping: <name>"},
                status_codes=[400],
                response_only=True,
            )
        ],
    ), 403: OpenApiResponse(
        response=ToppingSerializer,
        examples=[
            OpenApiExample(
                "Forbidden",
                value={"detail": "Authentication credentials were not provided."},
                status_codes=[403],
                response_only=True,
            ),
            OpenApiExample(
                "Not Owner",
                value={"detail": "Only owners are allowed to create toppings."},
                status_codes=[403],
                response_only=True,
            )
        ],
    ),
                                                         })
    def create(self, request):
        if not IsOwnerUser().has_permission(request, self):
            raise PermissionDenied("Only owners are allowed to create toppings.")

        serializer = ToppingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data['name']
        if Topping.objects.filter(name=name).exists():
            return Response({'error':  f'Duplicate Topping: {name}'}, status=400)

        serializer.save()
        return Response(serializer.data, status=201)

    @extend_schema(responses=ToppingSerializer)
    def partial_update(self, request, pk=None):
        if not IsOwnerUser().has_permission(request, self):
            raise PermissionDenied("Only owners are allowed to create toppings.")
        topping = ToppingService.update_topping_name(pk, request.data['name'])
        topping_serializer = ToppingSerializer(topping)
        return Response(topping_serializer.data, status=201)

    @extend_schema(responses=ToppingSerializer)
    def destroy(self, request, pk=None):
        if not IsOwnerUser().has_permission(request, self):
            raise PermissionDenied("Only owners are allowed to create toppings.")

        try:
            topping = Topping.objects.get(pk=pk)
            topping.delete()
            return Response(status=204)

        except Topping.DoesNotExist:
            return Response({'error':  f'Topping {pk} does not exist'}, status=404)

    @extend_schema(responses=ToppingSerializer)
    def retrieve(self, request, pk):
        try:
            topping = Topping.objects.get(pk=pk)
            serializer = ToppingSerializer(topping)
            return Response(serializer.data)
        except Topping.DoesNotExist:
            return Response({'error': 'Topping not found'}, status=404)