# books/forms.py
from django import forms
from .models import Review, Bookshelf

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

class BookshelfForm(forms.ModelForm):
    class Meta:
        model = Bookshelf
        fields = ['status']