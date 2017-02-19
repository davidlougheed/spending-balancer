from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from decimal import *

from .models import Payment, PaymentCategory
from .forms import PaymentForm, PaymentCategoryForm

import json

@login_required
def index(request):
    users = User.objects.order_by('username')
    payments = Payment.objects.all()

    total_paid = Decimal('0.00')
    users_paid = {}

    payments_by_category = {}

    for payment in payments:
        total_paid += payment.amount
        if payment.payer.id in users_paid:
            users_paid[payment.payer.id] += payment.amount
        else:
            users_paid[payment.payer.id] = payment.amount

        print(payments_by_category)

        if payment.category.name in payments_by_category:
            payments_by_category[payment.category.name]['y'] += float(payment.amount)
        else:
            payments_by_category[payment.category.name] = {
                'name': payment.category.name,
                'y': float(payment.amount)
            }

    print(payments_by_category)

    mean_paid = Decimal(0)
    mean_payment = Decimal(0)

    if payments.count() > 0:
        mean_payment = total_paid / payments.count()

    if users.count() > 0:
        mean_paid = total_paid / users.count()

    deviations = []

    for user in users:
        if user.id in users_paid:
            deviations.append((user.username, {
                'amount': str(users_paid[user.id] - mean_paid),
                'signal': ''
            }))
        else:
            deviations.append((user.username, '0'))

    return render(request, 'core/index.html', {
        'deviations': deviations,
        'contribution_mean': str(mean_paid.quantize(Decimal('0.01'))),
        'payment_mean': str(mean_payment.quantize(Decimal('0.01'))),
        'payments_by_category': json.dumps(list(payments_by_category.values())),
        'total': str(total_paid.quantize(Decimal('0.01'))),
        'number': payments.count(),
        'signed_in': request.user.is_authenticated
    })


@login_required
def payment_list(request):
    payments = Payment.objects.order_by('-date_made')
    return render(request, 'core/payment_list.html', {
        'payments': payments,
        'signed_in': request.user.is_authenticated
    })

@login_required
def payment_detail(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    return render(request, 'core/payment_detail.html', {
        'payment': payment,
        'signed_in': request.user.is_authenticated
    })

@login_required
def payment_add(request):
    if request.method == 'POST':
        pf = PaymentForm(request.POST)
        if pf.is_valid():
            new_payment = pf.save()
            return redirect('payment-list')
    else:
        pf = PaymentForm()
    return render(request, 'core/payment_add.html', {'form': pf, 'signed_in': request.user.is_authenticated})


def payment_category_list(request):
    payment_categories = PaymentCategory.objects.order_by('name')
    return render(request, 'core/payment_category_list.html', {
        'payment_categories': payment_categories,
        'signed_in': request.user.is_authenticated
    })

def payment_category_detail(request, category_id):
    category = get_object_or_404(PaymentCategory, pk=category_id)
    return render(request, 'core/payment_category_detail.html', {
        'category': category,
        'signed_in': request.user.is_authenticated
    })

def payment_category_add(request):
    if request.method == 'POST':
        pcf = PaymentCategoryForm(request.POST)
        if pcf.is_valid():
            new_category = pcf.save()
            return redirect('payment-category-list')
    else:
        pcf = PaymentCategoryForm()
    return render(request, 'core/payment_category_add.html', {'form': pcf, 'signed_in': request.user.is_authenticated})


def sign_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
    return render(request, 'core/sign_in.html', {'signed_in': request.user.is_authenticated})

def sign_out(request):
    logout(request)
    return redirect('index')
