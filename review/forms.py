from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

        widgets = {
            'rating': forms.Select(
                attrs={
                    'class': 'review-rating-input',
                }
            ),
            'comment': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': 'نظر خود را درباره تجربه ویزیت و پزشک بنویسید...',
                    'class': 'review-comment-input',
                }
            ),
        }