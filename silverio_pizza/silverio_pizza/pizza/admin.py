from django.contrib import admin

# Register your models here.
from .models import Pizza, PizzaMasterPiece

admin.site.register(Pizza)
admin.site.register(PizzaMasterPiece)
