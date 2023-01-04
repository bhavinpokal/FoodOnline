from dataclasses import fields
from django import forms
from accounts.validators import images_validator
from menu.models import Category, FoodItem


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']


class FoodItemForm(forms.ModelForm):
    # category = forms.ChoiceField(widget=forms.Select(
    #     attrs={'class': 'chosen-select'}))
    image = forms.FileField(widget=forms.FileInput(
        attrs={'class': 'browse-menu-icon-file', 'style': 'display: none;'}), validators=[images_validator])
    # is_available = forms.BooleanField(
    #     widget=forms.CheckboxInput(attrs={'class': 'btn bgcolor'}))

    class Meta:
        model = FoodItem
        fields = ['category', 'food_title', 'description',
                  'price', 'image', 'is_available']
