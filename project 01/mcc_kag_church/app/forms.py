from django import forms
from .models import FirstTimeVisitor

class FirstTimeVisitorForm(forms.ModelForm):
    class Meta:
        model = FirstTimeVisitor
        fields = ['name', 'email', 'phone', 'visit_date', 'questions']
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date'}),
            'questions': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'questions': 'Any special needs or questions?',
            'visit_date': 'When do you plan to visit?'
        }

from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={
                'placeholder': 'Subject of your message'
            }),
            'message': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Your message here...'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['subject'].required = True
        self.fields['message'].required = True
        
        # Add CSS classes and IDs
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'id': f'id_{field}'
            })