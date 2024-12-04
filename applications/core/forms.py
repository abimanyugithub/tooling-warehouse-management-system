from django import forms
from django.urls import reverse
from .models import Provinsi, KabupatenKota, Kecamatan, KelurahanDesa
from .models import Warehouse, ProductCategory, ProductUOM, ProductType, Product, WarehouseProduct
import random

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = [
            'code',
            'name',
            'zone',
            'capacity',
            'manager',
            'address_line1',
            'address_line2',
            'province',
            'regency',
            'district',
            'village',
            'phone_number',
            'email',
            'active'
        ]

        labels = {
            'code': 'Warehouse Code *',
            'name': 'Warehouse Name *',
            'zone': 'Area *',
            'address_line1': 'Address Line 1',
            'address_line2': 'Address Line 2',
            'phone_number': 'Phone Number',
            'email': 'Email Address',
            'province': 'Province',
            'regency': 'Regency',
            'district': 'District',
            'village': 'Village',
            'active':'Mark as active'
        }

        help_texts = {
            'code': 'A unique code for this warehouse (up to 20 characters).',
            'name': 'Enter the full name of the warehouse.',
            'zone': 'Provide a general description of the area within or near the warehouse, e.g., "Zone A".',
            'capacity': 'Enter the maximum storage capacity of this warehouse, e.g., in cubic meters (m³) (optional).',
            'manager': 'Enter the full name of the warehouse manager (optional).',
            'address_line1': 'Enter the primary street address (optional).',
            'address_line2': 'Enter any additional address information (e.g., suite number) (optional).',
            'province': 'Select the province (optional).',
            'regency': 'Select the regency or city (optional).',
            'district': 'Select the district (optional).',
            'village': 'Select the village (optional).',
            'phone_number': 'Enter a contact phone number for the warehouse (e.g., +6281234567890) (optional).',
            'email': 'Enter a contact email address for the warehouse (optional).',
            # 'active': 'Check if this is currently active.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Iterate through each field and set widget attributes
        for field_name, field in self.fields.items():
        
            if self.errors.get(field_name):
                # Add 'is-invalid' class to fields with errors
                field.widget.attrs.update({'class': 'form-control parsley-error'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

            if 'active' in self.fields:
                # Set widget untuk 'active' (misalnya, mengubah checkbox menjadi readonly)
                self.fields['active'].widget.attrs.update({'class': 'form-check form-check-input'})

            if 'code' in self.fields:
                # Menetapkan nilai acak untuk 'order_number' jika field tersebut ada
                self.fields['code'].initial = f"{random.randint(1000, 9999)}"

            # Optionally, add other attributes like autocomplete="off"
            field.widget.attrs.update({'autocomplete': 'off'})

class ProvinsiForm(forms.ModelForm):
    class Meta:
        model = Provinsi
        fields = ['name', 'id_code']

class KabupatenKotaForm(forms.ModelForm):
    class Meta:
        model = KabupatenKota
        fields = ['provinsi', 'name', 'id_code', 'type']

class KecamatanForm(forms.ModelForm):
    class Meta:
        model = Kecamatan
        fields = ['kabupaten_kota', 'name', 'id_code']

class KelurahanDesaForm(forms.ModelForm):
    class Meta:
        model = KelurahanDesa
        fields = ['kecamatan', 'name', 'id_code', 'postal_code']


class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = [
            'name',
            'description',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

        help_texts = {
            'name': 'Enter the name of the product category.',
            'description': 'Provide a detailed description of the category (optional).',
        }

        labels = {
            'name': 'Category Name *',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Iterate through each field and set widget attributes
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                # Add 'is-invalid' class to fields with errors
                field.widget.attrs.update({'class': 'form-control parsley-error'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

            field.widget.attrs.update({'autocomplete': 'off'})

class ProductUOMForm(forms.ModelForm):
    class Meta:
        model = ProductUOM
        fields = [
            'name',
            'code',
            'description',
        ]

        labels = {
            'name': 'UOM Name *',
            'code': 'UOM Code *',
        }
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

        help_texts = {
            'name': 'Enter the name of the unit of measurement (e.g., Kilogram, Liter, Meter). This should be unique.',
            'description': 'Provide a detailed description of the unit of measurement (optional). This can include the usage or details about the unit.',
            'code': 'Enter the unit’s code (e.g., kg for kilogram, l for liter). This will be used for shorthand representation.',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Iterate through each field and set widget attributes
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                # Add 'is-invalid' class to fields with errors
                field.widget.attrs.update({'class': 'form-control parsley-error'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

            field.widget.attrs.update({'autocomplete': 'off'})

class ProductTypeForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = [
            'name',
            'code',
            'description',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

        help_texts = {
            'name': 'Enter a unique name for the product type (e.g., Raw Materials, Finished Goods).',
            'code': 'Enter a code for the product type (e.g., "RM" for Raw Materials, "FG" for Finished Goods)',
            'description': 'Provide an optional description of the product type.',
        }

        labels = {
            'name': 'Product Type Name *',
            'code': 'Product Type Code *',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Iterate through each field and set widget attributes
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                # Add 'is-invalid' class to fields with errors
                field.widget.attrs.update({'class': 'form-control parsley-error'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

            field.widget.attrs.update({'autocomplete': 'off'})

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['sku', 'name', 'product_type', 'category', 'uom', 'description']  # Include other fields if needed

        labels = {
            'sku': 'Product Number *',
            'name': 'Name *',
            'category': 'Category *',
            'product_type': 'Product Type *',
            'uom': 'UOM *'
        }

        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'product_type': forms.Select(attrs={'class': 'form-control'}),
            'uom': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

        help_texts = {
            'category': 'Select the product category.',
            'name': 'The name of the product being added.',
            'description': 'A detailed description of the product (optional).',
            # 'price': 'The price of the product. Leave blank if unknown.',
            # 'stock_quantity': 'The number of items available in stock.',
            'uom': 'Select the unit of measurement for this product.',
            'product_type': 'Choose the type of product.',
            'suppliers': 'Select the suppliers that provide this product.',
            # 'sku': 'A unique code for the product. It will be generated automatically if left blank.'
            'sku': 'A unique code for this product.'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Iterate through each field and set widget attributes
        for field_name, field in self.fields.items():
        
            if self.errors.get(field_name):
                # Add 'is-invalid' class to fields with errors
                field.widget.attrs.update({'class': 'form-control parsley-error'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

            if 'sku' in self.fields:
                # Menetapkan nilai acak untuk 'order_number' jika field tersebut ada
                # Membuat SKU dengan panjang acak antara 2 hingga 7 digit
                length = random.randint(2, 7)  # Menentukan panjang antara 2 dan 7 digit
                
                self.fields['sku'].initial = f"{random.randint(10**(length-1), 10**length - 1)}"

            # Optionally, add other attributes like autocomplete="off"
            field.widget.attrs.update({'autocomplete': 'off'})


class WarehouseProductSearchForm(forms.Form):
    q = forms.CharField(
        label='Search',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Enter product number or name to search.' 
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Iterate through each field and set widget attributes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'autocomplete': 'off'})


class WarehouseProductForm(forms.ModelForm):
    class Meta:
        model = WarehouseProduct
        fields = ['product', 'warehouse']  # The fields we want to include in the form

        widgets = {
            'product': forms.HiddenInput(),  # We use HiddenInput so the user can't change it
            'warehouse': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        # Extract the product_instance from kwargs, passed in the view
        self.product_instance = kwargs.pop('product_instance', None)
        self.warehouse_instance = kwargs.pop('warehouse_instance', None)
        super().__init__(*args, **kwargs)

        if self.product_instance:
            self.fields['product'].initial = self.product_instance
        
        if self.warehouse_instance:
            self.fields['warehouse'].initial = self.warehouse_instance


    def save(self, commit=True):
        # Override the save method to explicitly assign the product
        warehouse_product = super().save(commit=False)
        warehouse_product.product = self.product_instance  # Assign the product instance passed from the view
        warehouse_product.warehouse = self.warehouse_instance

        if commit:
            warehouse_product.save()

        return warehouse_product


   