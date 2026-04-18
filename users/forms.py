from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

# 1. Custom Registration Form
class CustomRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',) # You can add 'email' here later if you want

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Loop through every field and inject the Bootstrap 'form-control' class
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

# 2. Custom Login Form
class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Loop through every field and inject the Bootstrap 'form-control' class
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'