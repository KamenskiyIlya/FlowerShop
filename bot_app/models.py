from django.db import models


class TgUser(models.Model):
    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name='Telegram ID',
    )
    username = models.CharField(
        max_length=100,
        blank=True,
        Null=True,
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
    

class Bouquet(models.Model):
    OCASSIONS = [
        ('birthday', 'День рождения'),
        ('wedding', 'Свадьба'),
        ('school', 'В школу'),
        ('no_reason', 'Без повода'),
        ('other', 'Другой повод'),
    ]
    
    name = models.CharField(max_length=50, verbose_name='Название')
    ocassion = models.CharField(
        max_length=50,
        choices=OCASSIONS,
        verbose_name='Повод'    
    )
    photo = models.ImageField(
        upload_to='bouquet_photo/',
        verbose_name='Фото',
    )
    meaning = models.TextField(verbose_name='Значение букета')
    composistion = models.TextField(verbose_name='Состав')
    price = models.IntegerField(verbose_name='Цена')
    in_stock = models.BooleanField(default=True, verbose_name='В наличии')
    
    def __str__(self):
        return f'{self.name} - {self.price} - {self.in_stock}'
    
    
class Order(models.Model):
    STATUSES = [
        ('new', 'Новый'),
        ('delivered', 'Производится доставка'),
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
    created_at = models.DateTimeField(auto_now_add=True)
    

class Employee(models.Model):
    CONDITIONS = [
        ('work', 'Работает'),
        ('sick', 'Больничный'),
        ('vacation', 'В отпуске'),
    ]
    POSITIONS = [
        ('florist', 'Флорист'),
        ('Courier', 'Курьер'),
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
    
    def __str__(self):
        return f'{self.name} - {self.position} - {self.condition}'
    
