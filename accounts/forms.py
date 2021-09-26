from django import forms
from django.forms import ValidationError

from .models import Account


class RegistrationForm(forms.ModelForm):

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirm your password',
            }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']

        widgets = {
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your password',
            }),
        }

    def __init__(self, *args, **kwargs):
        """ overriding because we have to add form-control class for all fields and placeholders
        for individual fields."""

        super(forms.ModelForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Mobile Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'


        for field_name, field_obj in self.fields.items():
            field_obj.widget.attrs['class'] = 'form-control'


    def clean(self):
        """ overriding validation method because we have to check whether password and
        confirm_password fields are matching or not """

        cleaned_data = super(forms.ModelForm, self).clean()
        password = cleaned_data['password']
        confirm_password = cleaned_data['confirm_password']

        if password != confirm_password:
            raise ValidationError('Passwords are not matching')