from django import forms

from .models import Visit


class VisitForm(forms.ModelForm):

    class Meta:
        model = Visit
        fields = [
            'patient_complaint',
        ]

        widgets = {
            'patient_complaint': forms.Textarea(
                attrs={
                    'rows': 6,
                    'placeholder': 'شکایت یا مشکل اصلی بیمار را وارد کنید...',
                }
            ),
        }