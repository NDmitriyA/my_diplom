from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from backendshop.auth_user.models import ConfirmEmailToken
from backendshop.shops.models import Category, Shop, InfoProduct, Order
from backendshop.shops.serializers import UserSerializer, CategorySerializer, ShopSerializer, ProductInfoSerializer, \
    OrderSerializer


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


