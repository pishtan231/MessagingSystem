from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from .models import Message
from .fields import CommaSeparatedUserField
from .serializer import FormSerializer

notification = None


class ComposeForm(forms.Form):
    receiver = CommaSeparatedUserField(label=_(u"Receiver"))
    subject = forms.CharField(label=_(u"Subject"), max_length=140)
    body = forms.CharField(label=_(u"Body"), widget=forms.Textarea(attrs={'rows': '12', 'cols': '55'}))

    def __init__(self, *args, **kwargs):
        receiver_filter = kwargs.pop('receiver_filter', None)
        super(ComposeForm, self).__init__(*args, **kwargs)
        if receiver_filter is not None:
            self.fields['receiver']._receiver_filter = receiver_filter

    def save(self, sender, parent_msg=None):
        receivers = [self.data['receiver']]
        subject = self.data['subject']
        body = self.data['body']

        message_list = []
        for r in receivers:
            msg = Message(
                sender=r,
                receiver=r,
                subject=subject,
                body=body,
            )
            if parent_msg is not None:
                msg.parent_msg = parent_msg
                parent_msg.replied_at = timezone.now()
                parent_msg.save()
            msg.save()
            message_list.append(msg)
            if notification:
                if parent_msg is not None:
                    notification.send([sender], "messages_replied", {'message': msg,})
                    notification.send([r], "messages_reply_received", {'message': msg,})
                else:
                    notification.send([sender], "messages_sent", {'message': msg,})
                    notification.send([r], "messages_received", {'message': msg,})
        return message_list

    def is_valid(self):
        serializer = self.Meta.serializer(data=self.data)
        valid = serializer.is_valid(raise_exception=True)
        return valid

    class Meta(object):
        serializer = FormSerializer
