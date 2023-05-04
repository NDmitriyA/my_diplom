from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
from rest_framework.views import APIView

from backendshop.shops.serializers import UserSerializer


class AccountRegister(APIView):
    """регистрация покупателей"""
    throttle_scope = 'anon'

    def Post(self, request, *args, **kwargs):
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
                    return JsonResponse

