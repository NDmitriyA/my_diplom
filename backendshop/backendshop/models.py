from django.db import models


class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название магазина')
    url = models.URLField(verbose_name='Сайт магазина', null=True, blank=True)
    user = models.OneToOneField(User, verbose_name='Пользователь', blank=True, null=True,
                                on_delete=models.CASCADE)
    status = models.BooleanField(verbose_name='Статус получения заказа', default=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        ordering = ('-name',)

    def __str__(self):
        return f'{self.name} - {self.user}'


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название категории продукта')
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='catigories', blank=True)

    class Meta:
        verbose_name = 'Категория товара'
        verbose_name_plural = 'Категории'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название продукта')
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products',
                                 blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('-name',)

    def __str__(self):
        return f'{self.category} - {self.name}'


class InfoProduct(models.Model):
    model = models.CharField(max_length=100, verbose_name='Модель')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    suggested_retail_price = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')
    product = models.ForeignKey(Product,verbose_name='Продукт', related_name='product_infos',
                                blank=True, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин',related_name='product_infos',
                             blank=True, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информационный список о продуктах'
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop'], name='unique_product_info'),
        ]

    def __str__(self):
        return f'{self.shop.name} - {self.product.name}'


    def __str__(self):
        return self.name


class Parameter(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название параметра')

    class Meta:
        verbose_name = 'Название параметра'
        verbose_name_plural = 'Список параметров'
        ordering = ('-name',)

    def __str__(self):
        return self.name

class ProductParameter(models.Model):
    info_product = models.ForeignKey(InfoProduct, verbose_name='Информация о продукте', blank=True,
                                     related_name='product_parameters', on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name='Параметр', related_name='product_parameters', blank=True,
                                  on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Список параметров'
        constraints = [
            models.UniqueConstraint(fields=['info_product', 'parameter'], name='unique_product_parameter'),
        ]

    def __str__(self):
        return f'{self.info_product.model} - {self.parameter.name}'


