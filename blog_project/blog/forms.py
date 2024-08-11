from django import forms
from .models import Post, Comment, Tag


class PostForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    class Meta:
        model = Post
        fields = ['title', 'text', 'tags', 'is_private']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

