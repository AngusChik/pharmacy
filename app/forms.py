from django import forms
from .models import Product, OrderDetail

class EditProductForm(forms.ModelForm):
    class Meta:
        model = Product  # Specify the model this form is linked to
        fields = [
            'name',
            'brand',
            'price',
            'barcode',
            'item_number',
            'quantity_in_stock',
            'description',
            'category',
            'unit_size',
        ]

class OrderDetailForm(forms.ModelForm):
    class Meta:
        model = OrderDetail
        fields = ['product', 'quantity']

class BarcodeForm(forms.Form):
    barcode = forms.CharField(max_length=30, label="Scan or Enter Barcode")
    quantity = forms.IntegerField(min_value=1, label="Quantity", initial=1)