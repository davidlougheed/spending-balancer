from django.contrib import admin
from core.models import *


@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    pass


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    pass


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass


@admin.register(PaymentCategory)
class PaymentCategoryAdmin(admin.ModelAdmin):
    pass
