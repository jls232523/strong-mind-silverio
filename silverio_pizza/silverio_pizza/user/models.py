from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_chef = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Make sure at least one of is_chef or is_owner is True
        # if not self.is_chef and not self.is_owner:
        #     raise ValueError("A user must be either a chef or an owner.")
        super().save(*args, **kwargs)
