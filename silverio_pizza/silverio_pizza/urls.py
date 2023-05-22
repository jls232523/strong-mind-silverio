"""
URL configuration for silverio_pizza project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .pizza import views as pizza_views
from .topping import views as topping_views
from .pizza_shop.views import login_chef, login_owner, create_pizza, update_pizza, delete_pizza, create_topping, \
    update_topping, delete_topping

router = DefaultRouter()
router.register(r"topping", topping_views.ToppingView)
router.register(r"pizza", pizza_views.PizzaView)
router.register(r"pizza_masterpiece", pizza_views.PizzaMasterPieceView)



urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("", TemplateView.as_view(template_name='index.html'), name='index'),

    path('login-chef/', login_chef, name='login-chef'),
    path('login-owner/', login_owner, name='login-owner'),
    path('create/pizza/', create_pizza, name='create-pizza'),
    path('update/pizza/<uuid:pizza_id>/', update_pizza, name='update-pizza'),
    path('delete/pizza/<uuid:pizza_id>/', delete_pizza, name='delete-pizza'),
    path('create/topping/', create_topping, name='create-topping'),
    path('update/topping/<uuid:topping_id>/', update_topping, name='update-topping'),
    path('delete/topping/<uuid:topping_id>/', delete_topping, name='delete-topping'),

              ] + router.urls
