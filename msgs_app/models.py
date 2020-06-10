from django.conf import settings
from django.urls import reverse
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class MessageManager(models.Manager):

    def inbox_for(self, user):
        return self.filter(receiver_deleted=False, sender_deleted=False)

    def unread_for(self, user):
        return self.filter(
                receiver=user,
                receiver_deleted=True,
        ).exclude(read_at__isnull=False)

    def outbox_for(self, user):
        return self.filter(
                sender=user,
                receiver_deleted__isnull=True,
        )

    def trash_for(self, user):
        return self.filter(
                receiver=user,
                receiver_deleted=False,
        ) | self.filter(
                sender=user,
                receiver_deleted__isnull=False,
        )


class Message(models.Model):
    subject = models.CharField(_("Subject"), max_length=140)
    body = models.TextField(_("Body"))
    sender = models.ForeignKey(AUTH_USER_MODEL, related_name='sent_messages', verbose_name=_("Sender"),
                               on_delete=models.PROTECT)
    receiver = models.ForeignKey(AUTH_USER_MODEL, related_name='received_messages', null=True, blank=True,
                                 verbose_name=_("receiver"), on_delete=models.SET_NULL)
    read_at = models.DateTimeField(_("read at"), null=True, blank=True)
    sender_deleted = models.BooleanField(default=False)
    receiver_deleted = models.BooleanField(default=False)

    objects = MessageManager()

    def new(self):
        if self.read_at is not None:
            return False
        return True

    def replied(self):
        if self.replied_at is not None:
            return True
        return False

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('messages_detail', args=[self.id])

    def save(self, **kwargs):
        super(Message, self).save(**kwargs)

    class Meta:
        ordering = ['-id']
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")


# fallback for email notification if django-notification could not be found
if "pinax.notifications" not in settings.INSTALLED_APPS and getattr(settings, 'DJANGO_MESSAGES_NOTIFY', True):
    from .utils import new_message_email

    signals.post_save.connect(new_message_email, sender=Message)
