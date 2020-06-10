from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic.detail import SingleObjectMixin
from django.http import QueryDict
import json

from .models import Message
from .forms import ComposeForm
from .utils import get_user_model

from django.views import View
from django.views.generic.list import ListView
from django.views.generic import DeleteView

User = get_user_model()


class WriteMessageView(View):
    form_class = ComposeForm

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        rec = User.objects.get(id=kwargs.get('pk'))

        ordinary_dict = {
            'subject': data.get('subject'),
            'body': data.get('body'),
            'receiver': rec,
        }
        query_dict = QueryDict('', mutable=True)
        query_dict.update(ordinary_dict)

        form = self.form_class(query_dict, receiver_filter=3)
        if form.is_valid():
            form.save(sender=request.user)
        return HttpResponse('Message successfully sent')


class Inbox(ListView):

    model = Message

    def get(self, request, user_id=0, *args, **kwargs):
        if user_id:
            user = User.objects.get(id=user_id)
            message_list = self.model.objects.inbox_for(user)
        else:
            if request.user.is_anonymous:
                return HttpResponseForbidden('Anonymous user can not request messages')
            message_list = self.model.objects.inbox_for(request.user)
        return JsonResponse({'results': list(message_list.values())})


class Unread(Inbox):
    def get(self, request, user_id=0, *args, **kwargs):
        if user_id:
            user = User.objects.get(id=user_id)
            message_list = self.model.objects.unread_for(user)
        else:
            if request.user.is_anonymous:
                return HttpResponseForbidden('Anonymous user can not request messages')
            message_list = self.model.objects.unread_for(request.user)
        return JsonResponse({'results': list(message_list.values())})


class ReadMessage(SingleObjectMixin, View):
    model = Message

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        self.object = self.get_object()
        message = get_object_or_404(Message, id=self.object.pk)

        return HttpResponse(message)


class MessageDeleteView(DeleteView):
    model = Message
    success_url = "/"

    def get(self, requset, pk, *args, **kwargs):
        message = get_object_or_404(Message, id=pk)
        message.sender_deleted = True
        message.save()
        return HttpResponse('The message was successfully deleted')
