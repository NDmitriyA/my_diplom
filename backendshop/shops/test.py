import pytest
from django.http import request

from shops.views import AccountRegister


def test_post_ar():
    with pytest.raises(Exception):
        AccountRegister.post(password='dfhjkd334758227355263')
