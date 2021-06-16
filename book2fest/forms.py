from django import forms
from book2fest.models import UserProfile, Ticket
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField()


    helper = FormHelper()
    helper.form_id = 'user_profile_crispy_form'
    helper.form_method = 'POST'
    helper.add_input(Submit('save', 'Save'))
    helper.inputs[0].field_classes = 'btn btn-success'

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'organizer']


def form_validation_error(form):
    msg = ""
    for field in form:
        for error in field.errors:
            msg += "%s: %s \\n" % (field.label if hasattr(field, 'label') else 'Error', error)
    return msg


class TicketForm(forms.ModelForm):

    helper = FormHelper()
    helper.form_id = 'ticket-form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Ticket
        fields = ('seat', 'delivery')