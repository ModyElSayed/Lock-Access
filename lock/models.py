import re

from django.core.exceptions import ValidationError
from django.db import models
from user.models import User


# Create your models here.
class Card(models.Model):

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.card_holder_id < pow(10, 15):
            raise ValidationError("Card number must be 16 digits long.")

        if len(Card.objects.filter(user=self.user)) > 5:
            raise ValidationError("You have reached the maximum number of cards.")
        super().save(force_insert, force_update, using, update_fields)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_holder_name = models.CharField(max_length=300)
    card_holder_id = models.BigIntegerField(unique=True)

    class AccessLevel(models.TextChoices):
        USER = "user"
        ADMIN = "admin"

    access_level = models.CharField(max_length=8, choices=AccessLevel.choices)


class Lock(models.Model):

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if re.fullmatch(r"^[a-zA-Z\d]+$", self.name) is None or self.name == "":
            raise ValidationError("Lock name must be valid: only letters and numbers are allowed.")

        if len(Lock.objects.filter(user=self.user)) > 2:
            raise ValidationError("You have reached the maximum number of locks.")
        super().save(force_insert, force_update, using, update_fields)

    # The user that owns the lock
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=16, unique=True, blank=False, null=False)


class LockCard(models.Model):

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if len(LockCard.objects.filter(lock=self.lock)) > 2:
            raise ValidationError("You have reached the maximum number of cards assigned to this lock.")
        elif len(LockCard.objects.filter(card=self.card)) > 1:
            raise ValidationError("You have reached the maximum number of locks assigned to this card.")
        else:
            super().save(force_insert, force_update, using, update_fields)

    lock = models.ForeignKey(Lock, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
