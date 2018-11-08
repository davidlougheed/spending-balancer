from django import forms
from django.forms import ModelForm, DateInput
from .models import *
from django.contrib.auth.models import User


class SignInForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username']


class PaymentCategoryForm(ModelForm):
    class Meta:
        model = PaymentCategory
        fields = ['name']


class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ['date_made', 'amount', 'receipt', 'category', 'payer']
        widgets = {'date_made': DateInput(attrs={'placeholder': 'YYYY-MM-DD'})}

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['receipt'].required = False


class PaymentEditForm(ModelForm):
    class Meta:
        model = Payment
        fields = ['date_made', 'amount', 'category']
        widgets = {'date_made': DateInput(attrs={'placeholder': 'YYYY-MM-DD'})}

    def __init__(self, *args, **kwargs):
        super(PaymentEditForm, self).__init__(*args, **kwargs)
