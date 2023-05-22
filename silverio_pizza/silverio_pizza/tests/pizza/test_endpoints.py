import json

import pytest
import requests
from django.contrib.auth import get_user_model

from ...user.models import User

pytestmark = pytest.mark.django_db


class TestPizzaEndpoints:
    endpoint = "/api/pizza/"
    topping_endpoint = "/api/topping/"

    def test_pizza_get(self, pizza_factory, api_client):
        pizza_factory.create_batch(4)

        user_model = User

        user = user_model.objects.create_user(username='testuser', password='testpassword')
        client = api_client()
        client.force_authenticate(user=user)

        response = client.get(self.endpoint)

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 4

    def test_pizza_create(self, pizza_factory, api_client):
        user_model = User

        user = user_model.objects.create_user(username='testuser', password='testpassword', is_chef=True)

        client = api_client()
        client.force_authenticate(user=user)
        data = {
            'name': "test",
            'toppings': []
        }

        response = client.post(self.endpoint, data=data, format='json')

        assert response.status_code == 201
        assert json.loads(response.content)['name'] == "test"
        assert len(json.loads(response.content)['toppings']) == 0

    def test_pizza_create_topping_not_exist(self, pizza_factory, api_client):
        user_model = User

        user = user_model.objects.create_user(username='testuser', password='testpassword', is_chef=True)

        client = api_client()
        client.force_authenticate(user=user)
        data = {
            'name': "test",
            'toppings': [{
                'name': "dne"
            }]
        }

        response = client.post(self.endpoint, data=data, format='json')

        assert response.status_code == 404
        assert response.content == b'{"error":"Topping dne does not exist"}'

    def test_pizza_with_owner_perms(self, api_client):
        user_model = User

        user = user_model.objects.create_user(username='testuser', password='testpassword', is_owner=True)

        client = api_client()
        client.force_authenticate(user=user)

        data = {
            'name': "test",
        }

        response = client.post(self.endpoint, data=data, format='json')
        assert response.status_code == 403

        response = client.patch(self.endpoint, data=data, format='json')
        assert response.status_code == 405

        response = client.delete(self.endpoint, data=data, format='json')
        assert response.status_code == 405


    def test_pizza_update(self, pizza_factory, topping_factory, api_client):
        pizza_factory.create_batch(1)
        topping_factory.create_batch(1)

        user_model = User

        user = user_model.objects.create_user(username='testuser', password='testpassword', is_chef=True)
        client = api_client()
        client.force_authenticate(user=user)

        response = client.get(self.endpoint)
        assert response.status_code == 200
        assert len(json.loads(response.content)) == 1

        topping_response = client.get(self.topping_endpoint)
        assert topping_response.status_code == 200
        assert len(json.loads(topping_response.content)) == 1

        data = {
            "name": str(json.loads(response.content)[0]['name']),
            "toppings": [
                {
                    "name": str(json.loads(topping_response.content)[0]['name'])
                }
            ]
        }


        client = api_client()
        client.force_authenticate(user=user)
        response = client.patch(f'/api/pizza/{json.loads(response.content)[0]["id"]}/', data=data,
                                format='json')

        assert response.status_code == 200
        assert json.loads(response.content)['toppings'][0]['name'] == json.loads(topping_response.content)[0]['name']

    def test_pizza_delete(self, pizza_factory, api_client):
        pizza_factory.create_batch(1)

        user_model = User

        user = user_model.objects.create_user(username='testuser', password='testpassword', is_chef=True)
        client = api_client()
        client.force_authenticate(user=user)

        response = client.get(self.endpoint)

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 1

        client.delete(f'/api/pizza/{json.loads(response.content)[0]["id"]}/')
        response = client.get(self.endpoint)

        assert len(json.loads(response.content)) == 0




class TestPizzaMasterPieceEndpoints:
    endpoint = "/api/pizza_masterpiece/"

    def test_pizza_masterpiece_get(self, pizza_master_piece_factory, api_client):
        pizza_master_piece_factory.create_batch(4)

        user_model = User

        user = user_model.objects.create_user(username='testuser', password='testpassword')
        client = api_client()
        client.force_authenticate(user=user)

        response = client.get(self.endpoint)
        assert response.status_code == 200
        assert len(json.loads(response.content)) == 4
