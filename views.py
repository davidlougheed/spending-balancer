from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from decimal import *

from .models import Payment, PaymentCategory
from .forms import PaymentForm, PaymentCategoryForm

import json
import numpy as np
from collections import OrderedDict
from datetime import datetime, timedelta, date


def get_months(earliest_time):
    months = set()
    dt = earliest_time

    while dt <= date.today():
        months.add(dt.strftime('%Y-%m'))
        dt += timedelta(days=1)

    return sorted(list(months))


@login_required
def index(request):
    users = User.objects.order_by('username')
    payments = Payment.objects.all()
    payment_categories = PaymentCategory.objects.all()
    sorted_category_names = sorted([c.name for c in payment_categories])
    payment_amounts = [float(p.amount) for p in payments]

    total_paid = Decimal('0.00')
    users_paid = {user.id: Decimal('0.00') for user in users}

    earliest_time = min([p.date_made for p in payments])
    payment_months = get_months(earliest_time)

    spending_history = OrderedDict([(cn, {'name': cn, 'data': [0] * len(payment_months)})
                                    for cn in sorted_category_names])
    payments_by_category = OrderedDict([(cn, {'name': cn, 'y': 0.0}) for cn in sorted_category_names])
    payments_by_category_by_user = OrderedDict(sorted([
        (user.username, OrderedDict([(cn, {'name': cn, 'y': 0.0}) for cn in sorted_category_names]))
        for user in users
    ], key=lambda u: u[0]))

    for payment in payments:
        total_paid += payment.amount
        users_paid[payment.payer.id] += payment.amount

        pmi = payment_months.index(payment.date_made.strftime('%Y-%m'))
        spending_history[payment.category.name]['data'][pmi] += float(payment.amount)

        payments_by_category_by_user[payment.payer.username][payment.category.name]['y'] += float(payment.amount)
        payments_by_category[payment.category.name]['y'] += float(payment.amount)

    for k in payments_by_category_by_user:
        payments_by_category_by_user[k] = json.dumps(list(payments_by_category_by_user[k].values()))

    payment_bins = np.linspace(0, 200, 21, True).astype(np.float64)
    payment_counts = np.histogram(payment_amounts, bins=payment_bins)[0].tolist()

    payment_hist = [[payment_bins[i], payment_counts[i]] for i in range(0, len(payment_counts))]

    mean_paid = Decimal(0)
    mean_payment = Decimal(0)

    if payments.count() > 0:
        mean_payment = total_paid / payments.count()

    if users.count() > 0:
        mean_paid = total_paid / users.count()

    deviations = []
    max_paid = max(users_paid.values())
    min_paid = min(users_paid.values())
    top_paid = [u for u in users_paid if users_paid[u] == max_paid]
    bottom_paid = [u for u in users_paid if users_paid[u] == min_paid]

    for user in users:
        deviation = users_paid[user.id] - mean_paid
        deviations.append((user.username, {
            'amount': str(deviation),
            'signal': 'negative' if deviation < 0 else 'positive',
            'top': (len(top_paid) == 1 and top_paid[0] == user.id),
            'bottom': (len(bottom_paid) == 1 and bottom_paid[0] == user.id)
        }))

    deviations = sorted(deviations, key=lambda d: d[0])

    return render(request, 'core/index.html', {
        'deviations': deviations,
        'contribution_mean': str(mean_paid.quantize(Decimal('0.01'))),
        'payment_mean': str(mean_payment.quantize(Decimal('0.01'))),
        'spending_history_categories': json.dumps(payment_months),
        'spending_history': json.dumps(list(spending_history.values())),
        'payments_by_category': json.dumps(list(payments_by_category.values())),
        'payments_by_category_by_user': payments_by_category_by_user,
        'payment_hist': json.dumps(payment_hist),
        'total': str(total_paid.quantize(Decimal('0.01'))),
        'number': payments.count(),
        'signed_in': request.user.is_authenticated
    })


# Payment Views

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
            pf.save()
            return redirect('payment-list')
    else:
        pf = PaymentForm(initial={
            'date_made': datetime.now().strftime('%Y-%m-%d'),
            'payer': request.user
        })
    return render(request, 'core/payment_add.html', {'form': pf, 'signed_in': request.user.is_authenticated})


# Payment Category Views

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


@login_required
def payment_category_add(request):
    if request.method == 'POST':
        pcf = PaymentCategoryForm(request.POST)
        if pcf.is_valid():
            new_category = pcf.save()
            return redirect('payment-category-list')
    else:
        pcf = PaymentCategoryForm()
    return render(request, 'core/payment_category_add.html', {'form': pcf, 'signed_in': request.user.is_authenticated})


# Authentication Views

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
