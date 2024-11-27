from django import forms
from django.urls import reverse
from .models import Provinsi, KabupatenKota, Kecamatan, KelurahanDesa, Warehouse

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
        ]

        labels = {
            'code': 'Warehouse Code *',
            'name': 'Warehouse Name *',
            'zone': 'Zone *',
            'address_line1': 'Address Line 1',
            'address_line2': 'Address Line 2',
            'phone_number': 'Phone Number',
            'email': 'Email Address',
            'province': 'Province',
            'regency': 'Regency',
            'district': 'District',
            'village': 'Village',
        }

        help_texts = {
            'code': 'A unique code for this warehouse (up to 20 characters).',
            'name': 'Enter the full name of the warehouse.',
            'zone': 'Provide a general description of the zone within or near the warehouse, e.g., "Zone A".',
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
