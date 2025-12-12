from .models import DeliveryCalculation
from django import forms


class DeliveryCalculatorForm(forms.ModelForm):
    class Meta:
        model = DeliveryCalculation
        fields = [
            'pickup_location', 'delivery_location', 
            'length', 'width', 'height', 'weight',
            'package_type', 'is_fragile', 'needs_insurance'
        ]
        widgets = {
            'pickup_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter pickup address'
            }),
            'delivery_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter delivery address'
            }),
            'length': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.1'
            }),
            'width': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.1'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.1'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.0',
                'step': '0.1'
            }),
            'package_type': forms.Select(attrs={'class': 'form-control'}),
            'is_fragile': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'needs_insurance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }