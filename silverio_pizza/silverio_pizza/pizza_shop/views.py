import base64
import json
import os

import requests
from django.contrib.auth import login, authenticate

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.views.decorators.csrf import  csrf_protect
from dotenv import load_dotenv
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from .forms import PizzaForm, ToppingForm
from ..pizza.models import Pizza
from ..topping.models import Topping
from ..topping.services import ToppingService
from ..settings import base

def login_chef(request):
    load_dotenv()
    username = os.getenv('CHEF_USERNAME')
    password = os.getenv('CHEF_PASSWORD')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return load_pizzas_for_chef(request, user)

    return JsonResponse({'detail': 'Unable to log in with provided credentials.'}, status=401)


def login_owner(request):
    load_dotenv()
    username = os.getenv('OWNER_USERNAME')
    password = os.getenv('OWNER_PASSWORD')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return load_toppings_for_owner(request, user)
    return JsonResponse({'detail': 'Unable to log in with provided credentials.'}, status=401)


def load_toppings_for_owner(request, user):
    try:
        token, created = Token.objects.get_or_create(user=user)
    except ObjectDoesNotExist:
        return ValidationError('user not found.', code='invalid')
    url = reverse('topping-list')
    complete_url = 'http://' + request.get_host() + url

    # Make a GET request to the ToppingView's list method
    response = requests.get(complete_url, headers={'Authorization': f'Token {token}'})
    if response.status_code == 200:
        toppings = response.json()
        context = {'toppings': toppings}

        # Store the token in the session
        request.session['token'] = token.key
        request.session['user'] = user.username
        request.session.save()

        return render(request, 'manage_toppings.html', context)
    else:
        return HttpResponse('Unable to get toppings.', status=500)


def load_pizzas_for_chef(request, user):
    try:
        token, created = Token.objects.get_or_create(user=user)
    except ObjectDoesNotExist:
        return ValidationError('user not found.', code='invalid')
    url = reverse('pizza-list')
    complete_url = 'http://' + request.get_host() + url

    # Make a GET request to the ToppingView's list method
    response = requests.get(complete_url, headers={'Authorization': f'Token {token}'})
    if response.status_code == 200:
        pizzas = response.json()
        context = {'pizzas': pizzas}
        # Store the token in the session
        request.session['token'] = token.key
        request.session['user'] = user.username
        request.session.save()

        return render(request, 'manage_pizza.html', context)
    else:
        return HttpResponse('Unable to get toppings.', status=500)


@csrf_protect
def create_pizza(request):
    if request.method == 'POST':
        form = PizzaForm(request.POST)
        if form.is_valid():
            json_data = process_pizza_form(form)
            token = get_session_token(request)
            complete_url = get_complete_url(request, 'pizza-list')
            response = requests.post(complete_url, headers={'Authorization': f'Token {token}', 'Content-Type':
                'application/json'}, data=json_data)
            if response.status_code == 201:
                return login_chef(request)
            else:
                return HttpResponse(response.content)
        # else:
        #     return HttpResponse(form.errors)
    else:
        form = PizzaForm()

    token = get_session_token(request)
    complete_url = get_complete_url(request, 'topping-list')

    response = requests.get(complete_url, headers={'Authorization': f'Token {token}'})
    if response.status_code == 200:
        toppings = response.json()
        context = {'toppings': toppings, 'form': form, 'error': form.errors}
        return render(request, 'create_pizza.html', context)
    else:
        return HttpResponse(response.content)

@csrf_protect
def update_pizza(request, pizza_id):

    if request.POST.get('_method') == 'PATCH':
        form = PizzaForm(request.POST)
        if form.is_valid():
            json_data = process_pizza_form(form)

            token = get_session_token(request)
            complete_url = get_complete_url(request, 'pizza-list') + str(pizza_id) + '/'
            response = requests.patch(complete_url, headers={'Authorization': f'Token {token}', 'Content-Type':
                'application/json'}, data=json_data)

            if response.status_code == 200:
                return login_chef(request)

            else:
                return HttpResponse(str(response.content), status=response.status_code)
    else:
        # Retrieve the pizza instance
        token = get_session_token(request)
        complete_url = get_complete_url(request, 'pizza-list') + str(pizza_id)
        response = requests.get(complete_url, headers={'Authorization': f'Token {token}'})
        pizza = response.json()

        complete_url = get_complete_url(request, 'topping-list')

        response = requests.get(complete_url, headers={'Authorization': f'Token {token}'})
        if response.status_code == 200:
            toppings = response.json()
            context = {'pizza': pizza, 'toppings': toppings}
            return render(request, 'update_pizza.html', context)
        else:
            return HttpResponse(str(response.content), status=response.status_code)

    # Default response in case no other conditions are met
    return HttpResponse(status=500)  # Adjust the status code as needed


@csrf_protect
def delete_pizza(request, pizza_id):
    token = get_session_token(request)
    complete_url = get_complete_url(request, 'pizza-list') + str(pizza_id) + '/'
    response = requests.delete(complete_url, headers={'Authorization': f'Token {token}'})
    return login_chef(request)


def get_session_token(request):
    return request.session.get('token')


def get_complete_url(request, path):
    url = reverse(path)
    if base.DEBUG == "0":
        return 'https://' + request.get_host() + "/api" + url
    else:
        return 'http://' + request.get_host() + "/api" + url


def process_pizza_form(form):
    # Process the form data
    name = form.cleaned_data['name']
    toppings = form.cleaned_data.get('toppings', [])
    toppings_data = [
        {
            'name': topping.name,
        }
        for topping in toppings
    ]

    data = {
        'name': name,
        'toppings': toppings_data
    }

    return json.dumps(data)

def process_topping_form(form):
    # Process the form data
    name = form.cleaned_data['name']

    data = {
        'name': name,
    }

    return json.dumps(data)


@csrf_protect
def create_topping(request):
    if request.method == 'POST':
        form = ToppingForm(request.POST)

        if form.is_valid():
            json_data = process_topping_form(form)
            token = get_session_token(request)
            complete_url = get_complete_url(request, 'topping-list')

            response = requests.request(url=complete_url, headers={'Authorization': f'Token {token}', 'Content-Type':
                'application/json'}, data=json_data, method='POST')

            if response.status_code == 201:
                return login_owner(request)
            else:
                return HttpResponse(response)
    else:
        form = ToppingForm()

    token = get_session_token(request)
    complete_url = get_complete_url(request, 'topping-list')

    response = requests.get(complete_url, headers={'Authorization': f'Token {token}'})
    if response.status_code == 200:
        toppings = response.json()
        context = {'toppings': toppings, 'form': form}
        return render(request, 'create_topping.html', context)
    else:
        return HttpResponse('Unable to get toppings.', status=500)


@csrf_protect
def update_topping(request, topping_id):
    if request.POST.get('_method') == 'PATCH':
        form = ToppingForm(request.POST)
        if form.is_valid():
            #ToppingService.update_topping_name(topping_id, form.cleaned_data['name'])

            json_data = process_topping_form(form)
            token = get_session_token(request)
            complete_url = get_complete_url(request, 'topping-list') + str(topping_id) + '/'
            response = requests.patch(complete_url, headers={'Authorization': f'Token {token}', 'Content-Type':
                'application/json'}, data=json_data)

            if response.status_code == 201:
                return login_owner(request)

            else:
                return HttpResponse(str(response.content), status=response.status_code)
    else:
        # Retrieve the topping instance
        token = get_session_token(request)
        complete_url = get_complete_url(request, 'topping-list') + str(topping_id)
        response = requests.get(complete_url, headers={'Authorization': f'Token {token}'})

        if response.status_code == 200:
            topping = response.json()
            context = {'topping': topping}
            return render(request, 'update_topping.html', context)
        else:
            return HttpResponse(str(response.content), status=response.status_code)

    # Default response in case no other conditions are met
    return HttpResponse(status=500)  # Adjust the status code as needed


@csrf_protect
def delete_topping(request, topping_id):
    token = get_session_token(request)
    complete_url = get_complete_url(request, 'topping-list') + str(topping_id) + '/'
    response = requests.delete(complete_url, headers={'Authorization': f'Token {token}'})
    return login_owner(request)
