from distutils.util import strtobool

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError
from django.db.models import Q, Sum, F, Prefetch
from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from ujson import loads as load_json

from auth_user.models import ConfirmEmailToken, Contact
from shops.models import Category, Shop, InfoProduct, Order, OrderItem
from shops.serializers import UserSerializer, CategorySerializer, ShopSerializer, ProductInfoSerializer, \
    OrderSerializer, OrderItemSerializer, ContactSerializer


class AccountRegister(APIView):
    """регистрация покупателей"""
    throttle_scope = 'anon'

    def post(self, request, *args, **kwargs):
        if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(request.data):
            errors = {}
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                """проверяем данные на уникальность имени пользователя"""
                request.data.update({})
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны обходимые данные'})


class AccountConfirm(APIView):
    """подтверждение почтового адреса"""
    throttle_scope = 'anon'

    def post(self, request, *args, **kwargs):
        if {'email', 'token'}.issubset(request.data):
            token = ConfirmEmailToken.objects.fiter(user__email=request.data['email'],
                                                    key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return Response({'Status': True})
            else:
                return Response({'Status': False, 'Errors': 'Не правиль указан токен или email'})
        return Response({'Status': False, 'Errors': 'Не указаны необходимые данные'},
                        status=status.HTTP_400_BAD_REQUEST)


class AccountLogin(APIView):
    """авторизация пользователей"""

    throttle_scope = 'anon'

    def post(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({'Status': True, 'Token': token.key})
            return Response({'Status': False, 'Errors': 'Ошибка авторизации'},
                            status=status.HTTP_403_FORBIDDEN)
        return Response({'Status': False, 'Errors': 'Не указаны необходимые данные'},
                        status=status.HTTP_400_BAD_REQUEST)


class DetailsAccount(APIView):
    """работа с данными пользователей"""
    throttle_scope = 'user'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Требуется вход в систему'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """создание данных пользователя"""
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Требуется вход в систему'},
                            status=status.HTTP_403_FORBIDDEN)
        """проверяем и сохраняем пароль"""
        if 'password' in request.data:
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                return Response({'Status': False, 'Errors': {'password': password_error}})
            else:
                request.user.set_password(request.data['password'])
        # проверяем остальные данные
        user_serialiszer = UserSerializer(request.data, data=request.data, partial=True)
        if user_serialiszer.is_valid():
            user_serialiszer.save()
            return Response({'Status': True}, status=status.HTTP_201_CREATED)
        else:
            return Response({'Status': False, 'Errors': user_serialiszer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


class CategoryView(viewsets.ModelViewSet):
    """просмотр категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    ordering = ('name',)


class ShopView(viewsets.ModelViewSet):
    """просомтр списка магазинов"""
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    ordering = ('name',)


class InfoProductView(viewsets.ReadOnlyModelViewSet):
    """поиск товаров"""
    throttle_scope = 'anon'
    serializer_class = ProductInfoSerializer
    ordering = ('product',)

    def get_queryset(self):
        query = Q(shop__state=True)
        shop_id = self.request.query_params.get('shop_id')
        category_id = self.request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        # фильтруем и отбрасываем дубликаты
        queryset = not InfoProduct.objects.filter(query).select_related(
            'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()
        return queryset

class BasketView(APIView):
    """работа с корзиной пользователя"""

    throttle_scope = 'user'

    #получить корзину
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status':False, 'Error': 'Требуется вход в систему'},
                                status=status.HTTP_403_FORBIDDEN)
        basket = Order.objects.filter(user_id=request.user.id, status='basket').prefetch_related(
            'ordered_items__product_info__product_category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Требуется вход в систему'},
                                status=status.HTTP_403_FORBIDDEN)
        items_basket = request.data.get('items')
        if items_basket:
            try:
                items_dict = load_json(items_basket)
            except ValueError:
                JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
                objects_created = 0
                for order_items in items_dict:
                    order_items.update({'order': basket.id})
                    serializer = OrderItemSerializer(data=order_items)
                    if serializer.is_valid():
                        try:
                            serializer.save()
                        except IntegrityError as error:
                            return JsonResponse({'Status': False, 'Errors': str(error)})
                        else:
                            objects_created += 1
                    else:
                        JsonResponse({'Status': False, 'Errors': serializer.errors})
                return JsonResponse({'Status': True, 'Создано объектов': objects_created})
            return JsonResponse({'Status': False, 'Errors': 'Не указаны необходимые данные'})

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Требуется вход в систему'},
                                status=status.HTTP_403_FORBIDDEN)
        items_sting = request.data.get('items')
        if items_sting:
            item_list = items_sting.split(',')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
            query = Q()
            objects_delete = False
            for order_item_id in item_list:
                query = query | Q(order_id=basket.id, id=order_item_id)
                objects_delete = True
            if objects_delete:
                delete_count = OrderItem.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': delete_count})
            return JsonResponse({'Status': False, 'Error': 'Не указаны необходимые данные'})

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Требуется вход в систему'},
                                status=status.HTTP_403_FORBIDDEN)
        items_posit = request.data.get('items')
        if items_posit:
            try:
                items_dict = load_json(items_posit)
            except ValueError:
                JsonResponse({'Status': False, 'Error': 'Не верный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
                objects_update = 0
                for order_item in items_dict:
                    if type(order_item['id']) == int and type(order_item['quantity']) == int:
                        objects_update += OrderItem.objects.filter(order_id=basket.id,
                                                                   id=order_item['id']).update(quantity=order_item
                                                                                              ['quantity'])
                    return JsonResponse({'Status': True, 'Обновлено объектов': objects_update})
                return JsonResponse({'Status': False, 'Error': 'Не указаны необходимые данные'})

    class OrderView(APIView):
        '''получение и размещение заказов пользователями'''
        throttle_scope = 'user'

        def get(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response({'Status': False, 'Error': 'Требуется вход в систему'},
                                status=status.HTTP_403_FORBIDDEN)
            order = Order.objects.filter(
                user_id=request.user.id).exclude(status='basket').select_related('contact').prefetch_related(
                    'ordered_items').annotate(total_quantity=Sum('ordered_items__quantity'),
                      total_sum=Sum('ordered_items__total_amount')).dictinct()

            serializer = OrderSerializer(order, many=True)
            return Response(serializer.data)

        def post(self, request, *args, **kwargs):
            '''размещение заказа,отправка письма об изменении статуса заказа'''

            if not request.user.is_authenticated:
                return Response({'Status': False, 'Error': 'Требуется вход в систему'},
                                status=status.HTTP_403_FORBIDDEN)
            if request.data['id'].isdigit():
                try:
                    is_update = Order.objects.filter(id=request.data['id'], user_id=request.user.id).update(
                        contact_id=request.data['contact'], status='new')
                except IntegrityError as error:
                    return Response({'Status': False, 'Error': 'Неправильно указаны необходимые данные'},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    if is_update:
                        request.user.email_user(f'Обновление статуса заказа','Заказ сформирован',
                                                from_email=settings.EMAIL_HOST_USER)
                        return Response({'Status': True})
            return Response({'Status': False, 'Error': 'Не указаны необходимые данные'},
                            status=status.HTTP_400_BAD_REQUEST)

class ContactView(APIView):
    '''работа с контактами покупателей'''

    throttle_scope = 'user'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Требуется вход в систему'},
                                status=status.HTTP_403_FORBIDDEN)
        contact = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    '''добавить контакт'''
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Требуется вход в систему'},
                                status=status.HTTP_403_FORBIDDEN)
        if {'city', 'phone'}.issubset(request.data):
            request.data._mutable = True
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                JsonResponse({'Status': False, 'Error': serializer.errors})
        return JsonResponse({'Status': False, 'Error': 'Не указаны необходимые данные'})

    '''удалить контакт'''
    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Требуется вход в систему'},
                                status=status.HTTP_403_FORBIDDEN)
        items_cont = request.data.get('items')
        if items_cont:
            items_list = items_cont.split(',')
            query = Q()
            objects_delete = False
            for contact_id in items_list:
                if contact_id.isdigit():
                    query = query | Q(user_id=request.user.id, id=contact_id)
                    objects_delete = True
            if objects_delete:
                delete_count = Contact.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'удалено объектов': delete_count})
            return JsonResponse({'Status': False, 'Error': 'Не указаны необходимые данные'})

    '''редактировать контак'''
    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Требуется вход в систему'},
                                status=status.HTTP_403_FORBIDDEN)
        if 'id' in request.data:
            if request.data['id'].isdigit():
                contact = Contact.objects.filter(id=request.data['id'], user_id=request.user.id).first()
                if contact:
                    serializer = ContactSerializer(contact, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return JsonResponse({'Status': True})
                    else:
                        JsonResponse({'Status': False, 'Error': serializer.errors})
        return JsonResponse({'Status': False, 'Error': 'Не указаны необходимые данные'})

class PartnerOrders(APIView):
    '''получение заказов поставщиками'''
    throttle_scope = 'user'
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Требуется вход в систему'},
                            status=status.HTTP_403_FORBIDDEN)
        if request.user.type != 'shop':
            return Response({'Status': False, 'Error': 'Только для магазинов'},
                            status=status.HTTP_403_FORBIDDEN)

        pr = Prefetch('ordered_items', queryset=OrderItem.objects.filter(shop__user_id=request.user.id))
        order = Order.objects.filter(
            ordered_items__shop__user_id=request.user.id).exclude(status='basket') \
            .prefetch_related(pr).select_related('contact').annotate(
            total_sum=Sum('ordered_items__total_amount'),
            total_quantity=Sum('ordered_items__quantity'))

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

class PartherState(APIView):
    '''работа со статусом поставщика'''
    throttle_scope = 'user'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Требуется вход в систему'},
                            status=status.HTTP_403_FORBIDDEN)

        if request.user.type != 'shop':
            return Response({'Status': False, 'Error': 'Только для магазинов'},
                            status=status.HTTP_403_FORBIDDEN)

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

        # Изменить текущий статус получения заказов у магазина
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Требуется вход в систему'}, status=status.HTTP_403_FORBIDDEN)

        if request.user.type != 'shop':
            return Response({'Status': False, 'Error': 'Только для магазинов'}, status=status.HTTP_403_FORBIDDEN)

        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(state=strtobool(state))
                return Response({'Status': True})
            except ValueError as error:
                return Response({'Status': False, 'Errors': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'Status': False, 'Error': 'Не указан аргумент state.'},
                        status=status.HTTP_400_BAD_REQUEST)

    class PartnerUpdate(APIView):
        '''обновления прайса от поставщика'''
        throttle_scope = 'partner'

        def post(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response({'Status': False, 'Error': 'Требуется вход в систему'},
                                status=status.HTTP_403_FORBIDDEN)

            if request.user.type != 'shop':
                return Response({'Status': False, 'Error': 'Только для магазинов'},
                                status=status.HTTP_403_FORBIDDEN)

            file = request.FILES
            if file:
                user_id = request.user.id
                import_shop_data(file, user_id)

                return Response({'Status': True})

            return Response({'Status': False, 'Error': 'Не указаны необходимые данные'},
                            status=status.HTTP_400_BAD_REQUEST)





