# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
import os
from random import randint
import datetime as dt
# import pytz
from datetime import datetime
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "msgs_api.settings")
django.setup()

from msgs_app.models import *
from msgs_app.utils import get_user_model
import requests

User = get_user_model()


# user1 = User.objects.all()

# msgs = Message.objects.filter(sender=user1[1], id__gte=10)
# msgs.delete()
# for i in range(20000):
#     msg_new = Message(body='abcd_{}'.format(randint(1,40)), receiver=user1[0], sender=user1[1],
#                       subject='sub_{}'.format(randint(1,40)))
#     msg_new.save()

# print(msgs.count())
# print(msgs)
def js_1():
    data1 = {
        'subject': 'sub_Hello to you',
        'body': 'Hello to you'
    }
    url = 'http://127.0.0.1:8000/webhook/2/'
    response = requests.post(url, data=data1)
    print('af_re')

js_1()