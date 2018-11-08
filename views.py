from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError

from decimal import *

from .models import *
from .forms import *

import json
import numpy as np
from collections import OrderedDict
from datetime import datetime, timedelta, date


def get_months(earliest_time):
    if earliest_time is None:
        return []

    months = set()
    dt = earliest_time

    while dt <= date.today():
        months.add(dt.strftime('%Y-%m'))
        dt += timedelta(days=1)

    return sorted(list(months))


@login_required
def index(request):
    user_pools = Pool.objects.filter(membership__user_id=request.user.id)

    if user_pools.count() == 1:
        return redirect('pool-index', pool_id=user_pools.first().id)

    return render(request, 'core/pool_list.html', {'pools': user_pools})


# Pool Views

@login_required
def pool_index(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    if request.user not in pool.members.all():
        raise PermissionDenied

    users = pool.members.all().order_by('username')
    payments = Payment.objects.filter(pool=pool)
    payment_categories = PaymentCategory.objects.filter(pool=pool)
    sorted_category_names = sorted([c.name for c in payment_categories])
    payment_amounts = [float(p.amount) for p in payments]

    total_paid = Decimal('0.00')
    users_paid = {user.id: Decimal('0.00') for user in users}

    earliest_time = min([p.date_made for p in payments]) if payments.count() > 0 else None
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

    if len(payment_months) > 12:
        payment_months = payment_months[-13:]
        for cn in sorted_category_names:
            spending_history[cn]['data'] = spending_history[cn]['data'][-13:]

    for k in payments_by_category_by_user:
        payments_by_category_by_user[k] = json.dumps(list(payments_by_category_by_user[k].values()))

    payment_bins = np.linspace(0, 200, 21, True).astype(np.float64)
    payment_counts = np.histogram(payment_amounts, bins=payment_bins)[0].tolist()

    # noinspection PyTypeChecker
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
            'top': (len(top_paid) == 1 and top_paid[0] == user.id and bottom_paid[0] != user.id),
            'bottom': (len(bottom_paid) == 1 and bottom_paid[0] == user.id and top_paid[0] != user.id)
        }))

    deviations = sorted(deviations, key=lambda d: d[0])

    return render(request, 'core/pool.html', {
        'pool': pool,
        'deviations': deviations,
        'contribution_mean': str(mean_paid.quantize(Decimal('0.01'))),
        'payment_mean': str(mean_payment.quantize(Decimal('0.01'))),
        'spending_history_categories': json.dumps(payment_months),
        'spending_history': json.dumps(list(spending_history.values())),
        'payments_by_category': json.dumps(list(payments_by_category.values())),
        'payments_by_category_by_user': payments_by_category_by_user,
        'payment_hist': json.dumps(payment_hist),
        'total': str(total_paid.quantize(Decimal('0.01'))),
        'number': payments.count()
    })


@login_required
def pool_create(request):
    if request.method == 'POST':
        pf = PoolForm(request.POST)
        if pf.is_valid():
            pool = pf.save()
            Membership.objects.create(pool=pool, user=request.user, owner=True).save()
            return redirect('index')
    else:
        pf = PoolForm()

    return render(request, 'core/pool_create.html', {'form': pf})


# Payment Views

@login_required
def payment_list(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    if request.user not in pool.members.all():
        raise PermissionDenied

    payments = Payment.objects.filter(pool=pool).order_by('-date_made')
    return render(request, 'core/payment_list.html', {'pool': pool, 'payments': payments})


@login_required
def payment_detail(request, pool_id, payment_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    if request.user not in pool.members.all():
        raise PermissionDenied

    payment = get_object_or_404(Payment, pk=payment_id, pool=pool)
    return render(request, 'core/payment_detail.html', {'pool': pool, 'payment': payment})


@login_required
def payment_add(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    if request.user not in pool.members.all():
        raise PermissionDenied

    if request.method == 'POST':
        pf = PaymentForm(pool, request.POST)
        if pf.is_valid():
            payment = pf.save(commit=False)
            payment.pool = pool
            payment.save()
            return redirect('payment-list', pool_id)

    else:
        pf = PaymentForm(pool, initial={
            'date_made': datetime.now().strftime('%Y-%m-%d'),
            'payer': request.user
        })

    return render(request, 'core/payment_add.html', {'pool': pool, 'form': pf})


@login_required
def payment_edit(request, pool_id, payment_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    if request.user not in pool.members.all():
        raise PermissionDenied

    payment = get_object_or_404(Payment, pk=payment_id)

    if payment.pool_id != pool.id:
        raise Payment.DoesNotExist

    if not payment.recent or payment.payer.id != request.user.id:
        raise PermissionDenied

    if request.method == 'POST':
        pf = PaymentEditForm(pool, request.POST, instance=payment)
        if pf.is_valid():
            pf.save()
            return redirect('payment-list', pool_id)
    else:
        pf = PaymentEditForm(pool, instance=payment)

    return render(request, 'core/payment_edit.html', {'pool': pool, 'form': pf, 'payment': payment})


# Payment Category Views

def payment_category_list(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    if request.user not in pool.members.all():
        raise PermissionDenied

    payment_categories = PaymentCategory.objects.filter(pool=pool).order_by('name')
    return render(request, 'core/payment_category_list.html', {'pool': pool, 'payment_categories': payment_categories})


def payment_category_detail(request, pool_id, category_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    if request.user not in pool.members.all():
        raise PermissionDenied

    category = get_object_or_404(PaymentCategory, pk=category_id)

    if category.pool_id != pool.id:
        raise PaymentCategory.DoesNotExist

    return render(request, 'core/payment_category_detail.html', {'pool': pool, 'category': category})


@login_required
def payment_category_add(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    if request.user not in pool.members.all():
        raise PermissionDenied

    if request.method == 'POST':
        pcf = PaymentCategoryForm(request.POST)
        if pcf.is_valid():
            pc = pcf.save(commit=False)
            pc.pool = pool
            pc.save()
            return redirect('payment-category-list', pool_id)
    else:
        pcf = PaymentCategoryForm()

    return render(request, 'core/payment_category_add.html', {'pool': pool, 'form': pcf})


# Member Views

@login_required
def member_list(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    if request.user not in pool.members.all():
        raise PermissionDenied

    members = pool.members.all().order_by('username')

    return render(request, 'core/member_list.html', {'pool': pool, 'members': members})


@login_required
def member_add(request, pool_id):
    errors = []

    pool = get_object_or_404(Pool, pk=pool_id)

    if request.user not in pool.members.all() or request.user not in pool.members.filter(membership__owner=True):
        raise PermissionDenied

    # TODO: More Error Handling

    if request.method == 'POST':
        mf = MemberForm(request.POST)
        if mf.is_valid():
            username = mf.cleaned_data['username']
            # TODO: Make this a validator instead
            try:
                member = User.objects.get(username=username)
                Membership.objects.create(user=member, pool=pool, owner=False)
                return redirect('member-list', pool.id)
            except User.DoesNotExist:
                errors.append({
                    'name': 'User Does Not Exist',
                    'details': 'The user with the provided username does not exist.'
                })
        else:
            errors.append({
                'name': 'Missing Field(s)',
                'details': 'Please fill out all required fields.'
            })
    else:
        mf = MemberForm()

    return render(request, 'core/member_add.html', {'pool': pool, 'form': mf, 'errors': errors})


# Authentication Views

def sign_in(request):
    # TODO: More Errors

    if request.user.is_authenticated():
        return redirect('index')

    errors = []

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            errors.append({
                'name': 'Wrong Username or Password',
                'details': 'Please try again with correct credentials.'
            })

    return render(request, 'core/sign_in.html', {'errors': errors})


@login_required()
def sign_out(request):
    logout(request)
    return redirect('index')


def register(request):
    # TODO: More Errors

    if request.user.is_authenticated():
        return redirect('index')

    errors = []

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            try:
                user = User.objects.create_user(username, email, password)
                login(request, user)
                return redirect('index')
            except IntegrityError:
                errors.append({
                    'name': 'Username Error',
                    'details': 'A user with that username already exists.'
                })

    return render(request, 'core/register.html', {'errors': errors})
