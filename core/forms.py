from django import forms
from .models import Comment


class ProfileForm(forms.Form):
    """
    Form for editing ones email address on the profile page
    """
    email = forms.EmailField()


class CommentForm(forms.ModelForm):
    """Form for creating and editing comments."""

    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 3}),
        }
