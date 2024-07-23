from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    re_path(r'^pools/(?P<pool_id>[0-9]+)/$', views.pool_index, name='pool-index'),
    re_path(r'^pools/create/$', views.pool_create, name='pool-create'),

    re_path(r'^pools/(?P<pool_id>[0-9]+)/payments/$', views.payment_list, name='payment-list'),
    re_path(r'^pools/(?P<pool_id>[0-9]+)/payments/add/$', views.payment_add, name='payment-add'),
    re_path(
        r'^pools/(?P<pool_id>[0-9]+)/payments/(?P<payment_id>[0-9]+)/$', views.payment_detail, name='payment-detail'),
    re_path(
        r'^pools/(?P<pool_id>[0-9]+)/payments/(?P<payment_id>[0-9]+)/edit/$', views.payment_edit, name='payment-edit'),

    re_path(r'^pools/(?P<pool_id>[0-9]+)/categories/$', views.payment_category_list, name='payment-category-list'),
    re_path(r'^pools/(?P<pool_id>[0-9]+)/categories/add/$', views.payment_category_add, name='payment-category-add'),
    re_path(r'^pools/(?P<pool_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/$', views.payment_category_detail,
        name='payment-category-detail'),

    re_path(r'^pools/(?P<pool_id>[0-9]+)/members/$', views.member_list, name='member-list'),
    re_path(r'^pools/(?P<pool_id>[0-9]+)/members/add/$', views.member_add, name='member-add'),

    re_path(r'^sign_in/$', views.sign_in, name='sign-in'),
    re_path(r'^sign_out/$', views.sign_out, name='sign-out'),
    re_path(r'^register/$', views.register, name='register')
]

# url(r'^users/$', views.user_list, name='user-list'),
# url(r'^users/(?P<pk>[0-9]+)/$', views.user_detail.as_view(), name='user-detail'),
# url(r'^users/(?P<pk>[0-9]+)/payments/$', views.user_payment_list.as_view(), name='user-payment-list'),
