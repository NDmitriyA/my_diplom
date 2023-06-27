import json

import pytest
import requests
from django.http import JsonResponse

from shops.views import AccountRegister


def test_post_ar():
    with pytest.raises(Exception):
        AccountRegister.post(password='dfhjkd334758227355263')
def test_post_registr_ar():
    response = requests.post(f"http://127.0.0.1:8000/user/register/")
    response_body = response.json(JsonResponse)
    assert response_body['Status'] == False

def test_post_details():
    response = requests.post(f"http://127.0.0.1:8000/api/v1/user/details")
    response_body = response.json(JsonResponse)
    assert response_body['Status'] == False

def test_post_login():
    response = requests.post(f"http://127.0.0.1:8000/api/v1/user/login",json=json.loads('{"email":"drim@tim.com", \
                                    "password":"1234554321q"}'))
    response_body = response.json()
    assert response_body['Status'] == True
    assert response.status_code == 200