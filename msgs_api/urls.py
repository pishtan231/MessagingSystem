from django.contrib import admin
from msgs_app.views import *
from django.conf.urls import url

urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^inbox/(?P<user_id>[\d]+)/$', Inbox.as_view(), name='messages_inbox_user'),
    url(r'^inbox/$' , Inbox.as_view(), name='messages_inbox_auth_user'),
    url(r'^unread/(?P<user_id>[\d]+)/$', Unread.as_view(), name='messages_unread'),
    url(r'^unread/$', Unread.as_view(), name='messages_unread_auth_user'),
    url(r'^delete/(?P<pk>[\d]+)/', MessageDeleteView.as_view(), name='messages_delete'),
    url(r'^read/(?P<pk>\d+)/$', ReadMessage.as_view(), name='messages_detail'),
    url(r'^write/(?P<pk>\d+)/', WriteMessageView.as_view(), name='write'),
]
