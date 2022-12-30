from dataclasses import fields
from pyexpat import model
from django import forms
from vendor.models import Vendor
from accounts.validators import images_validator


class VendorForm(forms.ModelForm):
    vendor_license = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[images_validator])

    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']
