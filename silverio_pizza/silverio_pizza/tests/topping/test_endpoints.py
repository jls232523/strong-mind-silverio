import json

import pytest
from django.contrib.auth import get_user_model

from ...user.models import User

pytestmark = pytest.mark.django_db


class TestToppingEndpoints:
    endpoint = "/api/topping/"
    pizza_endpoint = "/api/pizza/"

    def test_topping_get(self, topping_factory, api_client):
        topping_factory.create_batch(4)
        user_model = get_user_model()

        user = user_model.objects.create_user(username='testuser', password='testpassword', is_owner=True)
        client = api_client()
        client.force_authenticate(user=user)

        response = client.get(self.endpoint)

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 4

    def test_topping_create(self, pizza_factory, api_client):
        user_model = User

        user = user_model.objects.create_user(username='testuser', password='testpassword', is_owner=True)

        client = api_client()
        client.force_authenticate(user=user)
        data = {
            'name': "test",
        }

        response = client.post(self.endpoint, data=data, format='json')

        assert response.status_code == 201
        assert json.loads(response.content)['name'] == "test"



    def test_topping_with_chef_perms(self, api_client):
        user_model = User

        user = user_model.objects.create_user(username='testuser', password='testpassword', is_chef=True)

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


    def test_topping_update(self, pizza_factory, topping_factory, api_client):
        pizza_factory.create_batch(1)
        topping_factory.create_batch(1)

        user_model = User

        user = user_model.objects.create_user(username='testuser', password='testpassword', is_chef=True, is_owner=True)
        client = api_client()
        client.force_authenticate(user=user)

        response = client.get(self.pizza_endpoint)
        assert response.status_code == 200
        assert len(json.loads(response.content)) == 1

        topping_response = client.get(self.endpoint)
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

        data = {
            "name": "new_name",

        }
        response = client.patch(f'/api/topping/{json.loads(topping_response.content)[0]["id"]}/', data=data,
                                format='json')

        assert response.status_code == 201
        assert json.loads(response.content)['name'] == "new_name"

        #check topping on pizza to ensure update
        response = client.get(self.pizza_endpoint)
        assert response.status_code == 200
        assert json.loads(response.content)[0]['toppings'][0]['name'] == "new_name"

    def test_topping_delete(self, topping_factory, api_client):
        topping_factory.create_batch(1)

        user_model = User

        user = user_model.objects.create_user(username='testuser', password='testpassword', is_owner=True)
        client = api_client()
        client.force_authenticate(user=user)

        response = client.get(self.endpoint)

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 1

        client.delete(f'/api/topping/{json.loads(response.content)[0]["id"]}/')
        response = client.get(self.endpoint)

        assert len(json.loads(response.content)) == 0
