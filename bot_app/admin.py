from django.contrib import admin
from .models import Bouquet, Employee, Order, TgUser


@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'username', 'phone')
    search_fields = ('telegram_id', 'username', 'phone')


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'ocassion', 'price', 'in_stock')
    list_filter = ('ocassion', 'in_stock')
    search_fields = ('name', 'composistion')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'order_number', 'user', 'bouquet', 'status',
        'amount', 'delivery_date', 'delivery_time', 'created_at'
    )
    list_filter = ('status', 'delivery_date', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__phone', 'address')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'position', 'condition', 'telegram_id', 'phone')
    list_filter = ('position', 'condition')
    search_fields = ('name', 'phone', 'telegram_id')
