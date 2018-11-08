from django.db import models
from django.contrib.auth.models import User

from datetime import date


class Pool(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)

    members = models.ManyToManyField(User, through='Membership')

    def __str__(self):
        return self.name


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE)
    owner = models.BooleanField(default=False)

    def __str__(self):
        return '{} -> {} (Owner: {})'.format(self.user, self.pool, self.owner)


class PaymentCategory(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Payment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    date_made = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    receipt = models.ImageField(blank=True)

    payer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(PaymentCategory, on_delete=models.SET_NULL, null=True)

    @property
    def recent(self):
        return (date.today() - self.date_made).days < 8

    def __str__(self):
        return '$' + str(self.amount) + ' made ' + str(self.date_made) + ' by ' + str(self.payer) + '.'
