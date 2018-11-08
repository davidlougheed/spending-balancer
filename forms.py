from django import forms
from django.forms import Form, ModelForm, DateInput
from .models import *
from django.contrib.auth.models import User


class SignInForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username']


class PoolForm(ModelForm):
    class Meta:
        model = Pool
        fields = ['name']


class PaymentCategoryForm(ModelForm):
    class Meta:
        model = PaymentCategory
        fields = ['name']


class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ['date_made', 'amount', 'receipt', 'category', 'payer']
        widgets = {'date_made': DateInput(attrs={'placeholder': 'YYYY-MM-DD'})}

    def __init__(self, pool, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['receipt'].required = False
        self.fields['category'].queryset = PaymentCategory.objects.filter(pool=pool)
        self.fields['payer'].queryset = User.objects.filter(membership__pool=pool).order_by('username')


class PaymentEditForm(ModelForm):
    class Meta:
        model = Payment
        fields = ['date_made', 'amount', 'category']
        widgets = {'date_made': DateInput(attrs={'placeholder': 'YYYY-MM-DD'})}

    def __init__(self, pool, *args, **kwargs):
        super(PaymentEditForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = PaymentCategory.objects.filter(pool=pool)


class MemberForm(Form):
    username = forms.CharField(label='Username', max_length=100)
