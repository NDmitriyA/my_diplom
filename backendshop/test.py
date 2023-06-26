import pytest
import requests
from django.http import request, JsonResponse

from shops.views import AccountRegister


def test_post_ar():
    with pytest.raises(Exception):
        AccountRegister.post(password='dfhjkd334758227355263')
def test_post_registr_ar():
    response = requests.post(f"http://127.0.0.1:8000/user/register/")
    response_body = response.json(JsonResponse)
    assert response_body['Status'] == False