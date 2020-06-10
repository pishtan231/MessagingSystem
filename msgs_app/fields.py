from django import forms
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _

from .utils import get_user_model, get_username_field

User = get_user_model()


class CommaSeparatedUserInput(widgets.Input):
    input_type = 'text'

    def render(self, name, value, **kwargs):
        if value is None:
            value = ''
        elif isinstance(value, (list, tuple)):
            value = (', '.join([getattr(user, get_username_field()) for user in value]))
        return super(CommaSeparatedUserInput, self).render(name, value, **kwargs)


class CommaSeparatedUserField(forms.Field):
    widget = CommaSeparatedUserInput

    def __init__(self, *args, **kwargs):
        receiver_filter = kwargs.pop('receiver_filter', None)
        self._receiver_filter = receiver_filter
        super(CommaSeparatedUserField, self).__init__(*args, **kwargs)

    def clean(self, value):
        super(CommaSeparatedUserField, self).clean(value)
        if not value:
            return ''
        if isinstance(value, (list, tuple)):
            return value

        names = set(value.split(','))
        names_set = set([name.strip() for name in names if name.strip()])
        users = list(User.objects.filter(**{'%s__in' % get_username_field(): names_set}))
        unknown_names = names_set ^ set([getattr(user, get_username_field()) for user in users])

        receiver_filter = self._receiver_filter
        invalid_users = []
        if receiver_filter is not None:
            for r in users:
                if receiver_filter(r) is False:
                    users.remove(r)
                    invalid_users.append(getattr(r, get_username_field()))

        if unknown_names or invalid_users:
            raise forms.ValidationError(
                    _(u"The following usernames are incorrect: %(users)s") % {'users': ', '.join(
                            list(unknown_names)+invalid_users
                    )}
            )

        return users

    def prepare_value(self, value):
        if value is None:
            value = ''
        elif isinstance(value, (list, tuple)):
            value = (', '.join([getattr(user, get_username_field()) for user in value]))
        return value
