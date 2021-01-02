from django import forms
from .models import Invoice, Product
from .models import Stock


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = '__all__'


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = '__all__'


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


