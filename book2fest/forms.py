from django import forms
from book2fest.models import Artist, OrganizerProfile, UserProfile, Seat, SeatType, Genre, Service, EventProfile, Ticket
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
        fields = ['first_name', 'last_name', 'email']


class OrganizerProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField()


    helper = FormHelper()
    helper.form_id = 'organizer_profile_crispy_form'
    helper.form_method = 'POST'
    helper.add_input(Submit('save', 'Save'))
    helper.inputs[0].field_classes = 'btn btn-success'

    class Meta:
        model = OrganizerProfile
        fields = ['first_name', 'last_name', 'email', 'company', 'short_bio']


class ArtistForm(forms.ModelForm):
    genre = forms.ModelChoiceField(queryset=Genre.objects.all(), required=True)


    helper = FormHelper()
    helper.form_id = 'artist_crispy_form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Submit'))
    helper.inputs[0].field_classes = 'btn btn-success'

    class Meta:
        model = Artist
        fields = ['full_name', 'genre']


class EventProfileForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(queryset=Service.objects.all(), required=False)
    artist_list = forms.ModelMultipleChoiceField(queryset=Artist.objects.all(), required=True)
    event_start = forms.DateTimeField(widget=forms.SelectDateWidget)
    event_end = forms.DateTimeField(widget=forms.SelectDateWidget)



    helper = FormHelper()
    helper.form_id = 'event_crispy_form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Submit'))
    helper.inputs[0].field_classes = 'btn btn-success'

    def clean(self):
        cleaned_data = super(EventProfileForm, self).clean()

        start_date = cleaned_data.get('event_start')
        end_date = cleaned_data.get('event_end')
        max_capacity = cleaned_data.get('max_capacity')

        if start_date > end_date:
            raise forms.ValidationError("Please insert correct start and end dates")

        if max_capacity <= 0:
            raise forms.ValidationError("Please insert a valid max capacity")


    class Meta:
        model = EventProfile
        fields = ['event_name', 'event_start', 'brief_description', 'description', 'event_end', 'city', 'country', 'address', 'max_capacity', 'services', 'artist_list']


class SeatForm(forms.ModelForm):
    seat_type = forms.ModelChoiceField(queryset=SeatType.objects.all(), required=True)
    quantity = forms.IntegerField(required=True)

    helper = FormHelper()
    helper.form_id = 'seat_crispy_form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Submit'))
    helper.inputs[0].field_classes = 'btn btn-success'

    class Meta:
        model = Seat
        fields = ['seat_type', 'row', 'number', 'price', 'quantity']


class TicketForm(forms.ModelForm):

    helper = FormHelper()
    helper.form_id = 'ticket-form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Ticket
        fields = ('seat', 'delivery')

def form_validation_error(form):
    msg = ""
    for field in form:
        for error in field.errors:
            msg += "%s: %s \\n" % (field.label if hasattr(field, 'label') else 'Error', error)
    return msg

