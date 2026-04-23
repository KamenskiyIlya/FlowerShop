from django.contrib import admin
from .models import Bouquet, Employee, Order, TgUser, Consultation, PromoCode


@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'username', 'phone')
    search_fields = ('telegram_id', 'username', 'phone')
    list_display_links = ('id', 'telegram_id')


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'occasion', 'price', 'in_stock')
    list_filter = ('occasion', 'in_stock')
    search_fields = ('name', 'composition')
    list_display_links = ('id', 'name')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'user',
        'created_at',
        'status',
        'delivery_date',
        'delivery_time',
 
    )
    list_filter = ('status', 'delivery_date', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__phone', 'address')
    list_display_links = ('order_number',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'position', 'condition', 'telegram_id', 'phone')
    list_filter = ('position', 'condition')
    search_fields = ('name', 'phone', 'telegram_id')
    list_display_links = ('id', 'name')
    
    
@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'user_info', 
        'phone', 
        'status', 
        'created_at', 
    )
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at', 'started_at', 'closed_at', 'response_time_display')
    search_fields = ('user__username', 'user__telegram_id', 'phone', 'event')
    list_display_links = ('id', 'user_info')
    
    def user_info(self, obj):
        username = obj.user.username
        return f'@{username} (ID: {obj.user.telegram_id})'
    user_info.short_description = 'Пользователь'
    
    def response_time_display(self, obj):
        if obj.response_time:
            hours = obj.response_time // 60
            minutes = obj.response_time % 60
            return f'{hours} ч. {minutes} мин.'
        return '-'
    response_time_display.short_description = 'Время ответа'


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
        list_display = ('code', 'discount', 'is_active', 'valid_to')
        list_filter = ('is_active',)
        search_fields = ('code',)