from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^payments/$', views.payment_list, name='payment-list'),
    url(r'^payments/add/$', views.payment_add, name='payment-add'),
    url(r'^payments/(?P<payment_id>[0-9]+)/$', views.payment_detail, name='payment-detail'),

    url(r'^categories/$', views.payment_category_list, name='payment-category-list'),
    url(r'^categories/add/$', views.payment_category_add, name='payment-category-add'),
    url(r'^categories/(?P<category_id>[0-9]+)/$', views.payment_category_detail, name='payment-category-detail'),

    url(r'^sign_in/$', views.sign_in, name='sign-in'),
    url(r'^sign_out/$', views.sign_out, name='sign-out'),
]

# url(r'^users/$', views.user_list, name='user-list'),
# url(r'^users/(?P<pk>[0-9]+)/$', views.user_detail.as_view(), name='user-detail'),
# url(r'^users/(?P<pk>[0-9]+)/payments/$', views.user_payment_list.as_view(), name='user-payment-list'),
