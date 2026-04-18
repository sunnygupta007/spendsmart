from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        # We purposely leave out the 'user' field because we will assign it automatically!
        fields = ['category', 'amount', 'transaction_type', 'date', 'notes']
        
        # Customize specific inputs (like the date picker and text area size)
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inject Bootstrap classes into all fields
        for field_name, field in self.fields.items():
            # Dropdowns in Bootstrap use 'form-select', regular inputs use 'form-control'
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'