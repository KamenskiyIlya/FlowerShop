from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html

from .models import Bouquet, Consultation, Employee, Order, PromoCode, TgUser


@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'username', 'phone')
    search_fields = ('telegram_id', 'username', 'phone')
    list_display_links = ('id', 'telegram_id')


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    fields = ('name', 'photo', 'photo_preview', 'occasion', 'meaning', 'composition', 'price', 'in_stock')
    list_display = ('id', 'name', 'photo_preview', 'occasion', 'price', 'in_stock')
    list_filter = ('occasion', 'in_stock')
    search_fields = ('name', 'composition')
    list_display_links = ('id', 'name')
    readonly_fields = ('photo_preview',)
    
    def photo_preview(self, obj):
        if obj.photo and obj.photo.name:    
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.photo.url
            )
        return 'Нет фото'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = 'admin/bot_app/order/change_list.html'
    list_display = (
        'order_number',
        'user',
        'courier',
        'created_at',
        'status',
        'delivery_date',
        'delivery_time',
    )
    list_filter = ('status', 'delivery_date', 'created_at', 'courier')
    search_fields = ('order_number', 'user__username', 'user__phone', 'address')
    list_display_links = ('order_number',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'stats/',
                self.admin_site.admin_view(self.stats_view),
                name='bot_app_order_stats',
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['order_stats_url'] = reverse('admin:bot_app_order_stats')
        return super().changelist_view(request, extra_context=extra_context)

    def stats_view(self, request):
        orders = (
            Order.objects
            .select_related('user', 'courier', 'bouquet')
            .order_by('-created_at')
        )
        status_map = dict(Order.STATUSES)
        raw_status_stats = (
            Order.objects
            .values('status')
            .annotate(total=Count('id'))
            .order_by('status')
        )
        status_stats = [
            {
                'status': item['status'],
                'label': status_map.get(item['status'], item['status']),
                'total': item['total'],
            }
            for item in raw_status_stats
        ]
        couriers_stats = (
            Employee.objects
            .filter(position='courier')
            .annotate(total_deliveries=Count('assigned_orders'))
            .order_by('name')
        )

        context = dict(
            self.admin_site.each_context(request),
            title='Статистика заказов',
            opts=self.model._meta,
            orders=orders,
            total_orders=orders.count(),
            status_stats=status_stats,
            couriers_stats=couriers_stats,
            unassigned_orders=orders.filter(courier__isnull=True).count(),
        )
        return TemplateResponse(request, 'admin/bot_app/order/stats.html', context)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'position', 'condition', 'telegram_id', 'phone')
    list_filter = ('position', 'condition')
    search_fields = ('name', 'phone', 'telegram_id')
    list_display_links = ('id', 'name')
    
    
@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    change_list_template = 'admin/bot_app/consultation/change_list.html'
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'stats/',
                self.admin_site.admin_view(self.stats_view),
                name='bot_app_consultation_stats',
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['consultation_stats_url'] = reverse('admin:bot_app_consultation_stats')
        return super().changelist_view(request, extra_context=extra_context)

    def stats_view(self, request):
        consultations = (
            Consultation.objects
            .select_related('user', 'initial_bouquet', 'final_order')
            .order_by('-created_at')
        )
        status_map = dict(Consultation.STATUSES)
        raw_status_stats = (
            Consultation.objects
            .values('status')
            .annotate(total=Count('id'))
            .order_by('status')
        )
        status_stats = [
            {
                'status': item['status'],
                'label': status_map.get(item['status'], item['status']),
                'total': item['total'],
            }
            for item in raw_status_stats
        ]

        closed_with_response = [item.response_time for item in consultations if item.response_time is not None]
        average_response_minutes = int(sum(closed_with_response) / len(closed_with_response)) if closed_with_response else None

        context = dict(
            self.admin_site.each_context(request),
            title='Статистика консультаций',
            opts=self.model._meta,
            consultations=consultations,
            total_consultations=consultations.count(),
            status_stats=status_stats,
            new_consultations=consultations.filter(status='new').count(),
            in_progress_consultations=consultations.filter(status='in_progress').count(),
            closed_consultations=consultations.filter(status='closed').count(),
            average_response_minutes=average_response_minutes,
        )
        return TemplateResponse(request, 'admin/bot_app/consultation/stats.html', context)
    
    def user_info(self, obj):
        username = obj.user.username or 'без username'
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
