from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class TgUser(models.Model):
    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name='Telegram ID',
    )
    username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Имя пользователя',
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name='Телефон пользователя'
    )
    
    def __str__(self):
        return f'{self.username} - @{self.telegram_id}'

    class Meta:
        verbose_name = 'Клиент в Telegram'
        verbose_name_plural = 'Клиенты в Telegram'


class Bouquet(models.Model):
    OCCASIONS = [
        ('birthday', 'День рождения'),
        ('wedding', 'Свадьба'),
        ('school', 'В школу'),
        ('no_reason', 'Без повода'),
        ('other', 'Другой повод'),
    ]
    
    name = models.CharField(max_length=50, verbose_name='Название')
    occasion = models.CharField(
        max_length=50,
        choices=OCCASIONS,
        verbose_name='Повод'    
    )
    photo = models.ImageField(
        upload_to='bouquet_photo/',
        verbose_name='Фото',
    )
    meaning = models.TextField(verbose_name='Значение букета')
    composition = models.TextField(verbose_name='Состав')
    price = models.IntegerField(verbose_name='Цена')
    in_stock = models.BooleanField(default=True, verbose_name='В наличии')
    
    def __str__(self):
        return f'{self.name} - {self.price} - {self.in_stock}'

    class Meta:
        verbose_name = 'Букет'
        verbose_name_plural = 'Букеты'

    
class Order(models.Model):
    STATUSES = [
        ('new', 'Новый'),
        ('in_delivery', 'Производится доставка'),
        ('delivered', 'Доставлен'),
    ]
    
    order_number = models.IntegerField(
        unique=True,
        verbose_name='Номер заказа',
    )
    user = models.ForeignKey(
        TgUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='orders',
    )
    bouquet = models.ForeignKey(
        Bouquet,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Букет',
        related_name='bouquet_orders',
    )
    courier = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Курьер',
        related_name='assigned_orders',
        limit_choices_to={'position': 'courier'},
    )
    address = models.TextField(verbose_name='Адрес доставки')
    delivery_date = models.DateField(verbose_name='Дата доставки')
    delivery_time = models.CharField(
        max_length=50,
        verbose_name='Время доставки',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default='new',
        verbose_name='Статус',
    )
    amount = models.IntegerField(verbose_name='Сумма заказа')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self):
        return f'Заказ #{self.order_number} ({self.status})'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Employee(models.Model):
    CONDITIONS = [
        ('work', 'Работает'),
        ('sick', 'Больничный'),
        ('vacation', 'В отпуске'),
    ]
    POSITIONS = [
        ('florist', 'Флорист'),
        ('courier', 'Курьер'),
        ('director', 'Руководитель'),
    ]
    
    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name='Telegram ID',
    )
    name = models.CharField(max_length=50, verbose_name='ФИО')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    position = models.CharField(
        max_length=20,
        choices=POSITIONS,
        verbose_name='Должность'
    )
    condition = models.CharField(
        max_length=20,
        default='work',
        choices=CONDITIONS,
        verbose_name='Состояние'
    )
    
    def clean(self):
        """Проверка перед сохранением, чтобы исключить добавление второго руководителя"""
        if self.position == 'director':
            existing_director = (
                Employee.objects
                .filter(position='director')
                .exclude(id=self.id)
                .first()
            )
            
            if existing_director:
                raise ValidationError(
                    f'Директор уже существует: {existing_director.name}. '
                    'Может быть только один директор'
                )
                
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.name} - {self.position} - {self.condition}'

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'


class Consultation(models.Model):
    STATUSES = [
        ('new', 'Новая заявка'),
        ('in_progress', 'В работе'),
        ('closed', 'Закрыта'),
    ]
    
    user = models.ForeignKey(
        TgUser,
        on_delete=models.CASCADE,
        verbose_name='Клиент',
        related_name='consultations'
    )
    phone = models.CharField(
        max_length=30,
        verbose_name='Номер телефона'
    )
    event = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Повод'
    )
    budget = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name='Бюджет'
    )
    initial_bouquet = models.ForeignKey(
        Bouquet,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='consultations_initial',
        verbose_name='Изначальный букет'
    )
    final_order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='consultations',
        verbose_name='Итоговый заказ'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default='new',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата начала работы'
    )
    
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата закрытия'
    )
    
    def save(self, *args, **kwargs):
        now = timezone.now()
        if self.status == 'in_progress' and not self.started_at:
            self.started_at = now
        if self.status == 'closed' and not self.closed_at:
            self.closed_at = now
        super().save(*args, **kwargs)
    
    @property
    def response_time(self):
        if self.closed_at and self.created_at:
            delta = self.closed_at - self.created_at
            return int(delta.total_seconds() / 60)
        return None
    
    def __str__(self):
        return f'Заявка #{self.id} - {self.get_status_display()} - {self.created_at}'

    class Meta:
        verbose_name = 'Заявка на консультацию'
        verbose_name_plural = 'Заявки на консультацию'
        ordering = ['-created_at']


class PromoCode(models.Model):
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Промокод',
    )
    
    discount = models.IntegerField(verbose_name='Скидка (в рублях)')
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    
    valid_to = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дуйствует до',
    )
    
    def __str__(self):
        return f'{self.code} - {self.discount} руб.'
    
    @property
    def is_valid(self) -> bool:
        if not self.is_active:
            return False
        if self.valid_to and timezone.now() > self.valid_to:
            return False
        
        return True
    
    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'
