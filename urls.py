from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^pools/(?P<pool_id>[0-9]+)/$', views.pool_index, name='pool-index'),
    url(r'^pools/create/$', views.pool_create, name='pool-create'),

    url(r'^pools/(?P<pool_id>[0-9]+)/payments/$', views.payment_list, name='payment-list'),
    url(r'^pools/(?P<pool_id>[0-9]+)/payments/add/$', views.payment_add, name='payment-add'),
    url(r'^pools/(?P<pool_id>[0-9]+)/payments/(?P<payment_id>[0-9]+)/$', views.payment_detail, name='payment-detail'),
    url(r'^pools/(?P<pool_id>[0-9]+)/payments/(?P<payment_id>[0-9]+)/edit/$', views.payment_edit, name='payment-edit'),

    url(r'^pools/(?P<pool_id>[0-9]+)/categories/$', views.payment_category_list, name='payment-category-list'),
    url(r'^pools/(?P<pool_id>[0-9]+)/categories/add/$', views.payment_category_add, name='payment-category-add'),
    url(r'^pools/(?P<pool_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/$', views.payment_category_detail,
        name='payment-category-detail'),

    url(r'^pools/(?P<pool_id>[0-9]+)/members/$', views.member_list, name='member-list'),
    url(r'^pools/(?P<pool_id>[0-9]+)/members/add/$', views.member_add, name='member-add'),

    url(r'^sign_in/$', views.sign_in, name='sign-in'),
    url(r'^sign_out/$', views.sign_out, name='sign-out'),
    url(r'^register/$', views.register, name='register')
]

# url(r'^users/$', views.user_list, name='user-list'),
# url(r'^users/(?P<pk>[0-9]+)/$', views.user_detail.as_view(), name='user-detail'),
# url(r'^users/(?P<pk>[0-9]+)/payments/$', views.user_payment_list.as_view(), name='user-payment-list'),
