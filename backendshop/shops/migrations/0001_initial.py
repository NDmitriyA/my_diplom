# Generated by Django 4.2 on 2023-06-26 16:39

from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('company', models.CharField(blank=True, max_length=40, verbose_name='Компания')),
                ('position', models.CharField(blank=True, max_length=40, verbose_name='Должность')),
                ('type', models.CharField(choices=[('shop', 'Магазин'), ('buyer', 'Покупатель')], default='buyer', max_length=5, verbose_name='Тип пользователя')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Список пользователей',
                'ordering': ('email',),
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название категории продукта')),
            ],
            options={
                'verbose_name': 'Категория товара',
                'verbose_name_plural': 'Категории',
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=50, verbose_name='Город')),
                ('street', models.CharField(max_length=100, verbose_name='Улица')),
                ('house', models.CharField(blank=True, max_length=15, verbose_name='Дом')),
                ('structure', models.CharField(blank=True, max_length=15, verbose_name='Корпус')),
                ('building', models.CharField(blank=True, max_length=15, verbose_name='Строение')),
                ('apartment', models.CharField(blank=True, max_length=15, verbose_name='Квартира')),
                ('phone', models.CharField(max_length=20, verbose_name='Телефон')),
                ('phone_2', models.CharField(blank=True, max_length=20, verbose_name='Рабочий телефон')),
                ('user', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Контакты пользователя',
                'verbose_name_plural': 'Список контактов пользователя',
            },
        ),
        migrations.CreateModel(
            name='InfoProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(max_length=100, verbose_name='Модель')),
                ('quantity', models.PositiveIntegerField(verbose_name='Количество')),
                ('price', models.PositiveIntegerField(verbose_name='Цена')),
                ('suggested_retail_price', models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')),
            ],
            options={
                'verbose_name': 'Информация о продукте',
                'verbose_name_plural': 'Информационный список о продуктах',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_time', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('basket', 'Статус корзины'), ('New', 'Новый'), ('Confirmed', 'Подтвержден'), ('Assembled', 'Собран'), ('Sent', 'Отправлен'), ('Delivered', 'Доставлен'), ('Canceled', 'Отменен')], max_length=20, verbose_name='Статус')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Контакт', to='shops.contact', verbose_name='Контакт')),
                ('user', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Список заказов',
                'ordering': ('-data_time',),
            },
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название параметра')),
            ],
            options={
                'verbose_name': 'Название параметра',
                'verbose_name_plural': 'Список параметров',
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название магазина')),
                ('url', models.URLField(blank=True, null=True, verbose_name='Сайт магазина')),
                ('status', models.BooleanField(default=True, verbose_name='Статус получения заказа')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Магазин',
                'verbose_name_plural': 'Магазины',
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='ProductParameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info_product', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_parameters', to='shops.infoproduct', verbose_name='Информация о продукте')),
                ('parameter', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_parameters', to='shops.parameter', verbose_name='Параметр')),
            ],
            options={
                'verbose_name': 'Параметр',
                'verbose_name_plural': 'Список параметров',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название продукта')),
                ('category', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='shops.category', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Продукт',
                'verbose_name_plural': 'Продукты',
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Количество')),
                ('price', models.PositiveIntegerField(default=0, verbose_name='Цена')),
                ('total_cost', models.PositiveIntegerField(default=0, verbose_name='Общая стоимость')),
                ('info_product', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='ordered_items', to='shops.infoproduct', verbose_name='Информация о продукте')),
                ('order', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='ordered_items', to='shops.order', verbose_name='Заказ')),
            ],
            options={
                'verbose_name': 'Заказанная позиция',
                'verbose_name_plural': 'Список заказанных позиций',
            },
        ),
        migrations.AddField(
            model_name='infoproduct',
            name='product',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_infos', to='shops.product', verbose_name='Продукт'),
        ),
        migrations.AddField(
            model_name='infoproduct',
            name='shop',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_infos', to='shops.shop', verbose_name='Магазин'),
        ),
        migrations.CreateModel(
            name='ConfirmEmailToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='When was this token generated')),
                ('key', models.CharField(db_index=True, max_length=64, unique=True, verbose_name='Key')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='confirm_email_tokens', to=settings.AUTH_USER_MODEL, verbose_name='The User which is associated to this password reset token')),
            ],
            options={
                'verbose_name': 'Токен подтверждения Email',
                'verbose_name_plural': 'Токены подтверждения Email',
            },
        ),
        migrations.AddField(
            model_name='category',
            name='shops',
            field=models.ManyToManyField(blank=True, related_name='catigories', to='shops.shop', verbose_name='Магазины'),
        ),
        migrations.AddConstraint(
            model_name='productparameter',
            constraint=models.UniqueConstraint(fields=('info_product', 'parameter'), name='unique_product_parameter'),
        ),
        migrations.AddConstraint(
            model_name='orderitem',
            constraint=models.UniqueConstraint(fields=('order_id', 'info_product'), name='unique_order_item'),
        ),
        migrations.AddConstraint(
            model_name='infoproduct',
            constraint=models.UniqueConstraint(fields=('product', 'shop'), name='unique_product_info'),
        ),
    ]
