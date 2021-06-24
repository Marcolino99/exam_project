from django import forms
from book2fest.models import Artist, OrganizerProfile, UserProfile, Seat, SeatType, Genre, Service, EventProfile, Ticket, Review, Picture
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, HTML, Field, MultiField, Fieldset


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
        fields = ['full_name', 'genre', 'image']


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
        fields = ['event_name', 'event_start', 'brief_description', 'description', 'event_end', 'city', 'country', 'address', 'how_to_reach', 'max_capacity', 'services', 'artist_list']


class PictureForm(forms.ModelForm):
    img = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    helper = FormHelper()
    helper.form_id = 'picture_crispy_form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Submit'))
    helper.inputs[0].field_classes = 'btn btn-success'

    class Meta:
        model = Picture
        fields = ('name', 'description', 'img')


class SeatForm(forms.ModelForm):
    seat_type = forms.ModelChoiceField(queryset=SeatType.objects.all(), required=True)
    quantity = forms.IntegerField(required=True)

    helper = FormHelper()
    helper.form_id = 'seat_crispy_form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Submit'))
    helper.inputs[0].field_classes = 'btn btn-success'

    def clean(self):
        cleaned_data = super(SeatForm, self).clean()
        quantity = cleaned_data.get('quantity')
        if isinstance(quantity, int) :
            if quantity <= 0:
                self.add_error("quantity","Please insert a positive quantity")

    class Meta:
        model = Seat
        fields = ['seat_type', 'row', 'price', 'number', 'quantity']

class SeatTypeForm(forms.ModelForm):

    helper = FormHelper()
    helper.form_id = 'seat_type_crispy_form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Submit'))
    helper.inputs[0].field_classes = 'btn btn-success'

    class Meta:
        model = SeatType
        fields = ['name']


class TicketForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_id = 'ticket-form'
    helper.form_class = 'form-inline'
    helper.form_method = 'POST'
    helper.layout = Layout(
        Div(
            Div(
                Field('seat', title="Seat", css_class="col-lg seat mr-3"),
                Field('delivery', title="Delivery", css_class="col-lg mr-3"),
                Submit('submit', 'Book', css_class='bg-success col-lg'),
                css_class="row"
            ),
            css_class="container"
        )

    )

    def __init__(self, *args, **kwargs):
        event_pk = kwargs.pop('event_pk', None)  # pop pk event
        super(TicketForm, self).__init__(*args, **kwargs)
        if event_pk:
            self.fields['seat'].queryset = Seat.objects.filter(event_id=event_pk).filter(available=True).order_by('row','number')


        #self.fields['seat'].disabled = True

    class Meta:
        model = Ticket
        fields = ('seat', 'delivery')

class ReviewForm(forms.ModelForm):

    helper = FormHelper()
    helper.form_id = 'review-form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Submit'))


    class Meta:
        model = Review
        fields = ['rating', 'content']

def form_validation_error(form):
    msg = ""
    for field in form:
        for error in field.errors:
            msg += "%s: %s \\n" % (field.label if hasattr(field, 'label') else 'Error', error)
    return msg

