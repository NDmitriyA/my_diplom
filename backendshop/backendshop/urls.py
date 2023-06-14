
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path('api/v1/', include('shops.urls', namespace='shops')),
    path('social-auth/', include('social_django.urls', namespace='social'))
]

