from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView, UpdateView
from .models import Warehouse, Provinsi, KabupatenKota, Kecamatan, KelurahanDesa
from .forms import WarehouseForm, ProvinsiForm, KabupatenKotaForm, KecamatanForm, KelurahanDesaForm
from django.contrib import messages


# Create your views here.
class DashboardView(TemplateView):
    template_name = 'inventory/pages/index.html'

class ListWarehouse(ListView):
    model = Warehouse
    template_name = 'inventory/pages/warehouse/list.html'
    context_object_name = 'list_item'
    ordering = ['code']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fields'] = {
            'code': 'Warehouse Code',
            'name': 'Warehouse Name',
            'zone': 'Zone',
            'phone_number': 'Phone Number',
            'email': 'Email Address',
            'manager': 'Manager'
        }
        context['breadcrumb'] = [
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': 'Warehouse', 'url': 'warehouse_list'},
            {'name': 'List', 'url': None}  # No URL for the last breadcrumb item
        ]

        return context

class CreateWarehouse(CreateView):
    template_name = 'inventory/pages/warehouse/create.html'
    model = Warehouse
    form_class = WarehouseForm
    success_url = reverse_lazy('warehouse_list') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Initialize the form and add it to the context
        context['disable_fields'] = ['province', 'regency', 'district', 'village']
        context['breadcrumb'] = [
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': 'Warehouse', 'url': 'warehouse_list'},
            {'name': 'Register', 'url': None}  # No URL for the last breadcrumb item
        ]
        return context
    
class UpdateWarehouse(UpdateView):
    template_name = 'inventory/pages/warehouse/update.html'
    model = Warehouse
    form_class = WarehouseForm
    success_url = reverse_lazy('warehouse_list') 

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Pastikan form.instance ada sebelum melakukan filter
        if form.instance:
            # Filter queryset untuk field kabupaten berdasarkan provinsi dari request
            if form.instance.province:
                form.fields['regency'].queryset = KabupatenKota.objects.filter(provinsi=form.instance.province)
            else:
                form.fields['regency'].queryset = KabupatenKota.objects.none()

            if form.instance.regency:
                form.fields['district'].queryset = Kecamatan.objects.filter(kabupaten_kota=form.instance.regency)
            else:
                form.fields['district'].queryset = Kecamatan.objects.none()

            if form.instance.district:
                form.fields['village'].queryset = KelurahanDesa.objects.filter(kecamatan=form.instance.district)
            else:
                form.fields['village'].queryset = KelurahanDesa.objects.none()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Initialize the form and add it to the context
        context['disable_fields'] = ['province', 'regency', 'district', 'village']
        context['breadcrumb'] = [
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': 'Warehouse', 'url': 'warehouse_list'},
            {'name': 'Update', 'url': None}  # No URL for the last breadcrumb item
        ]
        return context
    
    def form_valid(self, form):
        # Add a success message to the Django messages framework
        messages.success(self.request, 'Operation was successful!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Custom behavior when form is invalid
        # Add an error message to the Django messages framework
        messages.error(self.request, "There were errors in your form submission.")

        # Optionally, you can also access and modify other fields.
        if 'phone_number' not in form.cleaned_data:
            form.add_error('phone_number', 'phone_number is required!')

        # Optionally, you can add additional custom context if needed
        return self.render_to_response(self.get_context_data(form=form))
    
def get_kabupaten_kota(request):
    provinsi_id = request.GET.get('province')
    kabupaten_kota = KabupatenKota.objects.filter(provinsi_id=provinsi_id)
    options = '<option value="">Select Regency/City</option>'
    for item in kabupaten_kota:
        options += f'<option value="{item.id}">{item.name}</option>'
    return HttpResponse(options)

def get_kecamatan(request):
    kabupaten_kota_id = request.GET.get('regency')
    kecamatan = Kecamatan.objects.filter(kabupaten_kota_id=kabupaten_kota_id)
    options = '<option value="">Select District</option>'
    for item in kecamatan:
        options += f'<option value="{item.id}">{item.name}</option>'
    return HttpResponse(options)

def get_kelurahan_desa(request):
    kecamatan_id = request.GET.get('district')
    kelurahan_desa = KelurahanDesa.objects.filter(kecamatan_id=kecamatan_id)
    options = '<option value="">Select Village/Subdistrict</option>'
    for item in kelurahan_desa:
        options += f'<option value="{item.id}">{item.name}, {item.postal_code}</option>'
    return HttpResponse(options)


