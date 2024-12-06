import uuid
from django import forms
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView, UpdateView, DetailView, View, FormView
from .models import Warehouse, KabupatenKota, Kecamatan, KelurahanDesa
from .models import ProductCategory, ProductUOM, ProductType, Product, WarehouseProduct
from .models import StockAdjustment
from django.db.models import Q

from .forms import WarehouseForm, ProductCategoryForm, ProductUOMForm, ProductTypeForm, ProductForm
from .forms import WarehouseProductSearchForm, WarehouseProductForm, StockAdjustmentForm
import re
from django.contrib import messages
from django.forms import TextInput, Select

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

def get_queryset_by_status(model, status):
    """
    Fungsi ini akan mengembalikan queryset berdasarkan status:
    - 'published' (deleted_at is null)
    - 'trash' (deleted_at is not null)
    - 'all' (semua data)
    """
    if status == 'published':
        return model.objects.filter(deleted_at__isnull=True)
    elif status == 'trash':
        return model.objects.filter(deleted_at__isnull=False)
    else:
        return model.objects.all()
    
# Fungsi untuk memisahkan nama model
def get_separated_model_name(model_name):
    separated = re.findall('[A-Z][^A-Z]*', model_name)
    return ' '.join(separated)

def get_deleted_and_not_deleted_counts(model):
    # Menghitung jumlah item yang dihapus (soft delete)
    deleted_count = model.objects.filter(deleted_at__isnull=False).count()
    
    # Menghitung jumlah item yang tidak dihapus (soft delete)
    not_deleted_count = model.objects.filter(deleted_at__isnull=True).count()
    
    return deleted_count, not_deleted_count

def get_status(request):
    # Mengambil status dari parameter GET, defaultnya adalah 'published'
    return request.GET.get('status', 'published')

def get_delete_restore_button(obj):
    if obj.deleted_at is None:
        # Tombol untuk hapus (soft delete)
        return f'<button data-bs-toggle="tooltip" title="Move to trash" type="button" class="btn btn-lg btn-danger btn-icon btn-round ms-auto" id="delete"><i class="fa fa-trash-alt"></i></button>'
    else:
        # Tombol untuk pulihkan (restore)
        return f'<button data-bs-toggle="tooltip" title="Restore" type="button" class="btn btn-lg btn-secondary btn-icon btn-round ms-auto" id="restore"><i class="fas fa-undo-alt"></i></button>'

def add_datetime_fields_to_form(form, obj):
    """
    Menambahkan field 'created_at', 'updated_at', dan 'deleted_at' ke form dan menonaktifkannya
    """
    # Menambahkan 'created_at' ke form dan menonaktifkan (readonly)
    form.fields['created_at'] = forms.DateTimeField(
        initial=obj.created_at, 
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        required=False
    )
    
    # Menambahkan 'updated_at' ke form dan menonaktifkan (readonly)
    form.fields['updated_at'] = forms.DateTimeField(
        initial=obj.updated_at, 
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        required=False
    )
    
    # Menambahkan 'deleted_at' ke form dan menonaktifkan (readonly)
    form.fields['deleted_at'] = forms.DateTimeField(
        initial=obj.deleted_at, 
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        required=False
    )

    return form

# Create your views here.
class DashboardView(TemplateView):
    template_name = 'core/pages/index.html'

class ListWarehouse(ListView):
    model = Warehouse
    template_name = 'core/pages/warehouse/list.html'
    context_object_name = 'list_item'
    ordering = ['code']

    def get_queryset(self):
        # Mendapatkan parameter 'status' dari query string
        status = self.request.GET.get('status', 'published')  # Default ke 'published'

        # Menggunakan fungsi pembantu untuk mendapatkan queryset berdasarkan status
        return get_queryset_by_status(self.model, status)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)
        context['fields'] = {
            'code': 'Warehouse Code',
            'name': 'Warehouse Name',
            'zone': 'Area',
            'phone_number': 'Phone Number',
            'email': 'Email Address',
            'manager': 'Manager',
        }
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('warehouse_list')},
            {'name': 'List', 'url': None}  # No URL for the last breadcrumb item
        ]

        # Mengambil list_item dari context yang sudah disediakan oleh ListView
        for item in context['list_item']:
            context['class_color'] = 'table-danger' if item.deleted_at else ''
        
        # Menggunakan fungsi pembantu untuk menghitung deleted_count dan not_deleted_count
        deleted_count, not_deleted_count = get_deleted_and_not_deleted_counts(self.model)
        context['deleted_count'] = deleted_count
        context['not_deleted_count'] = not_deleted_count
        
        # Menggunakan fungsi pembantu untuk mendapatkan status
        context['status'] = get_status(self.request)

        # context['card_sub'] = f'<div class="card-sub bg-transparent"><em>Note: The table displays only the first {self.paginate_by} records.</em></div>'
        return context

class CreateWarehouse(CreateView):
    template_name = 'core/pages/warehouse/create.html'
    model = Warehouse
    form_class = WarehouseForm
    success_url = reverse_lazy('warehouse_list') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)
        # Initialize the form and add it to the context
        
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('warehouse_list')},
            {'name': 'Register', 'url': None}  # No URL for the last breadcrumb item
        ]
        # Get the previous URL (referrer)
        
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Operation was successful!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Custom behavior when form is invalid
        # Add an error message to the Django messages framework
        messages.error(self.request, "There were errors in your form submission.")

        # Optionally, you can add additional custom context if needed
        return self.render_to_response(self.get_context_data(form=form))
    
class UpdateWarehouse(UpdateView):
    template_name = 'core/pages/warehouse/update.html'
    model = Warehouse
    form_class = WarehouseForm
    success_url = reverse_lazy('warehouse_list') 
    context_object_name = 'item'

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
        model_name_separated = get_separated_model_name(self.model.__name__)
        # Initialize the form and add it to the context
        
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('warehouse_list')},
            {'name': 'Edit', 'url': None}  # No URL for the last breadcrumb item
        ]
        # Get the previous URL (referrer)
        
        return context
    
    def form_valid(self, form):
        # Add a success message to the Django messages framework
        messages.success(self.request, 'Operation was successful!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Custom behavior when form is invalid
        # Add an error message to the Django messages framework
        messages.error(self.request, "There were errors in your form submission.")

        # Optionally, you can add additional custom context if needed
        return self.render_to_response(self.get_context_data(form=form))

class DetailWarehouse(DetailView):
    model = Warehouse
    template_name = 'core/pages/warehouse/detail.html'
    context_object_name = 'item'  # This is the object name you'll use in the template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)

        # Inisialisasi form dengan instance objek yang sedang ditampilkan
        form = WarehouseForm(instance=self.object)
        
        # Menggunakan fungsi pembantu untuk menambahkan field 'created_at', 'updated_at', 'deleted_at'
        update_form = add_datetime_fields_to_form(form, self.object)

        # Menonaktifkan setiap field dalam form
        for field in update_form.fields.values():
            field.disabled = True
        
        context['form'] = update_form     
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('warehouse_list')},
            {'name': 'Detail', 'url': None}  # No URL for the last breadcrumb item
        ]

        # Get the instance of the object being viewed (this is your model instance)
        obj = self.object

        # Filter the related fields based on the instance data
        if obj.province:
            context['regencies'] = KabupatenKota.objects.filter(provinsi=obj.province)
        else:
            context['regencies'] = KabupatenKota.objects.none()

        if obj.regency:
            context['districts'] = Kecamatan.objects.filter(kabupaten_kota=obj.regency)
        else:
            context['districts'] = Kecamatan.objects.none()

        if obj.district:
            context['villages'] = KelurahanDesa.objects.filter(kecamatan=obj.district)
        else:
            context['villages'] = KelurahanDesa.objects.none()

        # Menggunakan fungsi pembantu untuk mendapatkan HTML tombol
        context['button_delete'] = get_delete_restore_button(obj)

        return context
    
class SoftDeleteWarehouse(View):
    def post(self, request, pk):
        item = get_object_or_404(Warehouse, pk=pk)

        if item.deleted_at is None:
            item.soft_delete()  # Soft delete the item
        else:
            item.restore()
        messages.success(request, 'The item has been successfully deleted.')

        return redirect('warehouse_list')
    

class ListProductCategory(ListView):
    model = ProductCategory
    template_name = 'core/pages/product/category/list.html'
    context_object_name = 'list_item'
    ordering = ['name']

    def get_queryset(self):
        # Mendapatkan parameter 'status' dari query string
        status = self.request.GET.get('status', 'published')  # Default ke 'published'

        # Menggunakan fungsi pembantu untuk mendapatkan queryset berdasarkan status
        return get_queryset_by_status(self.model, status)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)
        context['fields'] = {
            'name': 'Category Name',
            'description': 'Description',
        }

        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('product_category_list')},
            {'name': 'List', 'url': None}  # No URL for the last breadcrumb item
        ]

        # Mengambil list_item dari context yang sudah disediakan oleh ListView
        for item in context['list_item']:
            context['class_color'] = 'table-danger' if item.deleted_at else ''
        
        # Menggunakan fungsi pembantu untuk menghitung deleted_count dan not_deleted_count
        deleted_count, not_deleted_count = get_deleted_and_not_deleted_counts(self.model)
        context['deleted_count'] = deleted_count
        context['not_deleted_count'] = not_deleted_count
        
        # Menggunakan fungsi pembantu untuk mendapatkan status
        context['status'] = get_status(self.request)

        return context

class CreateProductCategory(CreateView):
    template_name = 'core/pages/product/category/create.html'
    model = ProductCategory
    form_class = ProductCategoryForm
    success_url = reverse_lazy('product_category_list')

    def get_context_data(self, **kwargs):
        # Get the context data from ListView (for the book list)
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('product_category_list')},
            {'name': 'Register', 'url': None}  # No URL for the last breadcrumb item
        ]
        
        context['subtitle'] = 'Register'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Operation was successful!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "There were errors in your form submission.")

        return self.render_to_response(self.get_context_data(form=form))
    
    
class UpdateProductCategory(UpdateView):
    template_name = 'core/pages/product/category/create.html'
    model = ProductCategory
    form_class = ProductCategoryForm
    success_url = reverse_lazy('product_category_list') 
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        # Get the context data from ListView (for the book list)
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('product_category_list')},
            {'name': 'Edit', 'url': None}  # No URL for the last breadcrumb item
        ]
        
        context['subtitle'] = 'Edit'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Operation was successful!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "There were errors in your form submission.")

        return self.render_to_response(self.get_context_data(form=form))

class DetailProductCategory(DetailView):
    model = ProductCategory
    template_name = 'core/pages/product/category/detail.html'
    context_object_name = 'item'  # This is the object name you'll use in the template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)

        # Inisialisasi form dengan instance objek yang sedang ditampilkan
        form = ProductCategoryForm(instance=self.object)
        
        # Menggunakan fungsi pembantu untuk menambahkan field 'created_at', 'updated_at', 'deleted_at'
        update_form = add_datetime_fields_to_form(form, self.object)

        # Menonaktifkan setiap field dalam form
        for field in update_form.fields.values():
            field.disabled = True
        
        context['form'] = update_form
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('product_category_list')},
            {'name': 'Detail', 'url': None}  # No URL for the last breadcrumb item
        ]

        # Menggunakan fungsi pembantu untuk mendapatkan HTML tombol
        context['button_delete'] = get_delete_restore_button(self.object)
        
        return context
    
    
class SoftDeleteProductCategory(View):
    def post(self, request, pk):
        item = get_object_or_404(ProductCategory, pk=pk)

        if item.deleted_at is None:
            item.soft_delete()  # Soft delete the item
        else:
            item.restore()
        messages.success(request, 'The item has been successfully deleted.')

        return redirect('product_category_list')
    
    
class ListProductUOM(ListView):
    model = ProductUOM
    template_name = 'core/pages/product/uom/list.html'
    context_object_name = 'list_item'
    ordering = ['name']

    def get_queryset(self):
        # Mendapatkan parameter 'status' dari query string
        status = self.request.GET.get('status', 'published')  # Default ke 'published'

        # Menggunakan fungsi pembantu untuk mendapatkan queryset berdasarkan status
        return get_queryset_by_status(self.model, status)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)
        context['fields'] = {
            'name': 'UoM Name',
            'code': 'UoM Code',
            'description': 'Description',
        }

        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('product_uom_list')},
            {'name': 'List', 'url': None}  # No URL for the last breadcrumb item
        ]

        # Mengambil list_item dari context yang sudah disediakan oleh ListView
        for item in context['list_item']:
            context['class_color'] = 'table-danger' if item.deleted_at else ''
        
        # Menggunakan fungsi pembantu untuk menghitung deleted_count dan not_deleted_count
        deleted_count, not_deleted_count = get_deleted_and_not_deleted_counts(self.model)
        context['deleted_count'] = deleted_count
        context['not_deleted_count'] = not_deleted_count
        
        # Menggunakan fungsi pembantu untuk mendapatkan status
        context['status'] = get_status(self.request)

        return context
    
class CreateProductUOM(CreateView):
    template_name = 'core/pages/product/category/create.html'
    model = ProductUOM
    form_class = ProductUOMForm
    success_url = reverse_lazy('product_uom_list')

    def get_context_data(self, **kwargs):
        # Get the context data from ListView (for the book list)
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('product_uom_list')},
            {'name': 'Register', 'url': None}  # No URL for the last breadcrumb item
        ]
        
        context['subtitle'] = 'Register'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Operation was successful!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "There were errors in your form submission.")

        return self.render_to_response(self.get_context_data(form=form))
    
class UpdateProductUOM(UpdateView):
    template_name = 'core/pages/product/category/create.html'
    model = ProductUOM
    form_class = ProductUOMForm
    success_url = reverse_lazy('product_uom_list')

    def get_context_data(self, **kwargs):
        # Get the context data from ListView (for the book list)
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('product_uom_list')},
            {'name': 'Register', 'url': None}  # No URL for the last breadcrumb item
        ]
        
        context['subtitle'] = 'Edit'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Operation was successful!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "There were errors in your form submission.")

        return self.render_to_response(self.get_context_data(form=form))
    
class DetailProductUOM(DetailView):
    model = ProductUOM
    template_name = 'core/pages/product/uom/detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)

        # Inisialisasi form dengan instance objek yang sedang ditampilkan
        form = ProductUOMForm(instance=self.object)
        
        # Menggunakan fungsi pembantu untuk menambahkan field 'created_at', 'updated_at', 'deleted_at'
        update_form = add_datetime_fields_to_form(form, self.object)

        # Menonaktifkan setiap field dalam form
        for field in update_form.fields.values():
            field.disabled = True
        
        context['form'] = update_form
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('product_uom_list')},
            {'name': 'Detail', 'url': None}  # No URL for the last breadcrumb item
        ]

        # Menggunakan fungsi pembantu untuk mendapatkan HTML tombol
        context['button_delete'] = get_delete_restore_button(self.object)
        
        return context
    
class SoftDeleteProductUOM(View):
    def post(self, request, pk):
        item = get_object_or_404(ProductUOM, pk=pk)

        if item.deleted_at is None:
            item.soft_delete()  # Soft delete the item
        else:
            item.restore()
        messages.success(request, 'The item has been successfully deleted.')

        return redirect('product_uom_list')

class ListProductType(ListView):
    model = ProductType
    template_name = 'core/pages/product/type/list.html'
    context_object_name = 'list_item'
    ordering = ['name']

    def get_queryset(self):
        # Mendapatkan parameter 'status' dari query string
        status = self.request.GET.get('status', 'published')  # Default ke 'published'

        # Menggunakan fungsi pembantu untuk mendapatkan queryset berdasarkan status
        return get_queryset_by_status(self.model, status)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)
        context['fields'] = {
            'name': 'Type Name',
            'code': 'Type Code',
            'description': 'Description',
        }

        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('product_type_list')},
            {'name': 'List', 'url': None}  # No URL for the last breadcrumb item
        ]

        # Mengambil list_item dari context yang sudah disediakan oleh ListView
        for item in context['list_item']:
            context['class_color'] = 'table-danger' if item.deleted_at else ''
            
        # Menggunakan fungsi pembantu untuk menghitung deleted_count dan not_deleted_count
        deleted_count, not_deleted_count = get_deleted_and_not_deleted_counts(self.model)
        context['deleted_count'] = deleted_count
        context['not_deleted_count'] = not_deleted_count
        
        # Menggunakan fungsi pembantu untuk mendapatkan status
        context['status'] = get_status(self.request)

        return context
    
class CreateProductType(CreateView):
    template_name = 'core/pages/product/type/create.html'
    model = ProductType
    form_class = ProductTypeForm
    success_url = reverse_lazy('product_type_list')

    def get_context_data(self, **kwargs):
        # Get the context data from ListView (for the book list)
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('product_type_list')},
            {'name': 'Register', 'url': None}  # No URL for the last breadcrumb item
        ]
        
        context['subtitle'] = 'Register'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Operation was successful!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "There were errors in your form submission.")

        return self.render_to_response(self.get_context_data(form=form))
    
class DetailProductType(DetailView):
    model = ProductType
    template_name = 'core/pages/product/type/detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)

        # Inisialisasi form dengan instance objek yang sedang ditampilkan
        form = ProductTypeForm(instance=self.object)
        
        # Menggunakan fungsi pembantu untuk menambahkan field 'created_at', 'updated_at', 'deleted_at'
        update_form = add_datetime_fields_to_form(form, self.object)
        
        # Menonaktifkan setiap field dalam form
        for field in update_form.fields.values():
            field.disabled = True
        
        context['form'] = update_form
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('product_type_list')},
            {'name': 'Detail', 'url': None}  # No URL for the last breadcrumb item
        ]

        # Menggunakan fungsi pembantu untuk mendapatkan HTML tombol
        context['button_delete'] = get_delete_restore_button(self.object)
        
        return context
    
class UpdateProductType(UpdateView):
    template_name = 'core/pages/product/category/create.html'
    model = ProductType
    form_class = ProductTypeForm
    success_url = reverse_lazy('product_type_list')

    def get_context_data(self, **kwargs):
        # Get the context data from ListView (for the book list)
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('product_uom_list')},
            {'name': 'Register', 'url': None}  # No URL for the last breadcrumb item
        ]
        
        context['subtitle'] = 'Edit'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Operation was successful!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "There were errors in your form submission.")

        return self.render_to_response(self.get_context_data(form=form))

class SoftDeleteProductType(View):
    def post(self, request, pk):
        item = get_object_or_404(ProductType, pk=pk)

        if item.deleted_at is None:
            item.soft_delete()  # Soft delete the item
        else:
            item.restore()
        messages.success(request, 'The item has been successfully deleted.')

        return redirect('product_type_list')
    

class ListProduct(ListView):
    model = Product
    template_name = 'core/pages/product/list.html'
    context_object_name = 'list_item'
    ordering = ['name']

    def get_queryset(self):
        # Mendapatkan parameter 'status' dari query string
        status = self.request.GET.get('status', 'published')  # Default ke 'published'

        # Menggunakan fungsi pembantu untuk mendapatkan queryset berdasarkan status
        return get_queryset_by_status(self.model, status)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)
        context['fields'] = {
            'sku': 'Product No.',
            'name': 'Product Name',
            'category': 'Category',
            'product_type': 'Type',
            'uom': 'UOM',
        }

        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('product_list')},
            {'name': 'List', 'url': None}  # No URL for the last breadcrumb item
        ]

        # Mengambil list_item dari context yang sudah disediakan oleh ListView
        for item in context['list_item']:
            context['class_color'] = 'table-danger' if item.deleted_at else ''
            
        # Menggunakan fungsi pembantu untuk menghitung deleted_count dan not_deleted_count
        deleted_count, not_deleted_count = get_deleted_and_not_deleted_counts(self.model)
        context['deleted_count'] = deleted_count
        context['not_deleted_count'] = not_deleted_count
        
        # Menggunakan fungsi pembantu untuk mendapatkan status
        context['status'] = get_status(self.request)
        
        # Menggunakan fungsi pembantu untuk mendapatkan status
        context['status'] = get_status(self.request)
        return context

class CreateProduct(CreateView):
    template_name = 'core/pages/product/create.html'
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('product_list')

    def get_context_data(self, **kwargs):
        # Get the context data from ListView (for the book list)
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('product_list')},
            {'name': 'Register', 'url': None}  # No URL for the last breadcrumb item
        ]
        
        context['subtitle'] = 'Register'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Operation was successful!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "There were errors in your form submission.")

        return self.render_to_response(self.get_context_data(form=form))
    
class UpdateProduct(UpdateView):
    template_name = 'core/pages/product/create.html'
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('product_list')

    def get_context_data(self, **kwargs):
        # Get the context data from ListView (for the book list)
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('product_list')},
            {'name': 'Register', 'url': None}  # No URL for the last breadcrumb item
        ]
        
        context['subtitle'] = 'Edit'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Operation was successful!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "There were errors in your form submission.")

        return self.render_to_response(self.get_context_data(form=form))
    
class DetailProduct(DetailView):
    model = Product
    template_name = 'core/pages/product/detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)
        
        # Inisialisasi form dengan instance objek yang sedang ditampilkan
        form = ProductForm(instance=self.object)
        
        # Menggunakan fungsi pembantu untuk menambahkan field 'created_at', 'updated_at', 'deleted_at'
        update_form = add_datetime_fields_to_form(form, self.object)
        
        # Menonaktifkan setiap field dalam form
        for field in update_form.fields.values():
            field.disabled = True
        
        context['form'] = update_form

        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('product_list')},
            {'name': 'Detail', 'url': None}  # No URL for the last breadcrumb item
        ]

        # Menggunakan fungsi pembantu untuk mendapatkan HTML tombol
        context['button_delete'] = get_delete_restore_button(self.object)
        
        return context
    
class SoftDeleteProduct(View):
    def post(self, request, pk):
        item = get_object_or_404(Product, pk=pk)

        if item.deleted_at is None:
            item.soft_delete()  # Soft delete the item
        else:
            item.restore()
        messages.success(request, 'The item has been successfully deleted.')

        return redirect('product_list')


class ListWarehouseProduct(ListView):
    model = WarehouseProduct
    template_name = 'core/pages/inventory/assign_warehouse/list.html'
    context_object_name = 'list_item'
    ordering = ['name']

    def dispatch(self, request, *args, **kwargs):
        warehouse_uuid = self.kwargs['wh']

        # Check if the warehouse has been deleted
        if self.model.objects.filter(warehouse=warehouse_uuid, warehouse__deleted_at__isnull=False).exists():
            # Redirect to the DashboardView
            return redirect(reverse('dashboard_view'))  # Replace with actual URL pattern name if different

        # Proceed with the usual dispatch if the condition is not met
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Mendapatkan nilai warehouse_uuid dari kwargs
        warehouse_uuid = self.kwargs['wh']

        # Mendapatkan parameter 'status' dari query string, default 'published'
        status = self.request.GET.get('status', 'published')

        # Menggunakan fungsi pembantu get_queryset_by_status untuk mendapatkan queryset berdasarkan status
        queryset = get_queryset_by_status(self.model, status)

        # Menambahkan filter untuk warehouse_uuid
        return queryset.filter(warehouse=warehouse_uuid, product__deleted_at__isnull=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        warehouse_uuid = self.kwargs['wh']
        # Mendapatkan warehouse berdasarkan UUID
        warehouse = get_object_or_404(Warehouse, id=warehouse_uuid)
        # model_name_separated = get_separated_model_name(self.model.__name__)
    
        context['fields'] = {
            'warehouse': 'Warehouse',
            'product': 'Product',
        }

        context['title'] = f'Assign Product'
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': 'Assign Product', 'url': reverse('warehouse_product_list', kwargs={'wh': warehouse_uuid})},
            {'name': 'List', 'url': None}  # No URL for the last breadcrumb item
        ]

        # Mengambil list_item dari context yang sudah disediakan oleh ListView
        for item in context['list_item']:
            context['class_color'] = 'table-danger' if item.deleted_at else ''
            
        # Menghitung jumlah product yang sudah dihapus (soft delete)
        deleted_count = self.model.objects.filter(warehouse=warehouse, deleted_at__isnull=False).count()
        context['deleted_count'] = deleted_count
        # Menghitung jumlah product yang tidak dihapus (soft delete)
        not_deleted_count = self.model.objects.filter(warehouse=warehouse, deleted_at__isnull=True).count()
        context['not_deleted_count'] = not_deleted_count
        # Menggunakan fungsi pembantu untuk mendapatkan status
        context['status'] = get_status(self.request)

        context['warehouse_id'] = warehouse.id
        return context

class QueryWarehouseProduct(TemplateView):
    template_name = 'core/pages/inventory/assign_warehouse/query.html'

    def dispatch(self, request, *args, **kwargs):
        warehouse_uuid = self.kwargs['wh']

        # Check if the warehouse has been deleted
        if WarehouseProduct.objects.filter(warehouse=warehouse_uuid, warehouse__deleted_at__isnull=False).exists():
            # Redirect to the DashboardView
            return redirect(reverse('dashboard_view'))  # Replace with actual URL pattern name if different

        # Proceed with the usual dispatch if the condition is not met
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        warehouse = get_object_or_404(Warehouse, pk=self.kwargs.get('wh'))
        context['form'] = WarehouseProductSearchForm

        search_term = self.request.GET.get('q')

        if search_term:
            # Perform the search query
            product_query = Product.objects.filter(
                Q(name__icontains=search_term) | Q(sku__icontains=search_term),
                deleted_at__isnull=True
            )
            
            # Check if there are results
            if product_query.exists():
                context['list_item'] = product_query
            else:
                # Use the messages framework to display a "no results" message
                messages.error(self.request, 'No products found matching your search.')

        context['fields'] = {
            'sku': 'Product No.',
            'name': 'Product Name',
            'category': 'Category',
            'product_type': 'Type',
            'uom': 'UOM',
        }

        context['title'] = f'Assign Product'
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': 'Assign Product', 'url': reverse('warehouse_product_list', kwargs={'wh': warehouse.id})},
            {'name': 'Register', 'url': reverse('warehouse_product_query', kwargs={'wh': warehouse.id})},
            {'name': f'{warehouse}', 'url': None}
        ]

        context['subtitle'] = 'Register'
        context['warehouse_id'] = warehouse.id
        return context
    
class CreateWarehouseProduct(TemplateView):
    template_name = 'core/pages/inventory/assign_warehouse/create.html'

    def dispatch(self, request, *args, **kwargs):
        warehouse_uuid = self.kwargs['wh']

        # Check if the warehouse has been deleted
        if WarehouseProduct.objects.filter(warehouse=warehouse_uuid, warehouse__deleted_at__isnull=False).exists():
            # Redirect to the DashboardView
            return redirect(reverse('dashboard_view'))  # Replace with actual URL pattern name if different

        # Proceed with the usual dispatch if the condition is not met
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Fetch the product instance based on the pk in the URL
        product = get_object_or_404(Product, pk=self.kwargs.get('prd'))
        # Get the warehouse instance from the URL parameters ('wh')
        warehouse = get_object_or_404(Warehouse, pk=self.kwargs.get('wh'))

        status = WarehouseProduct.objects.filter(product=product, warehouse=warehouse)
        # Initialize the form and pass the product instance to it
        form = WarehouseProductForm(product_instance=product.id, warehouse_instance=warehouse.id)
        context['form'] = form
        context['title'] = 'Assign Product'
        context['breadcrumb'] = [
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': 'Assign Product', 'url': reverse('warehouse_product_list', kwargs={'wh': warehouse.id})},
            {'name': 'Register', 'url': reverse('warehouse_product_query', kwargs={'wh': warehouse.id})},
            {'name': f'{warehouse}', 'url': None},
            {'name': f'{product}', 'url': None}
        ]
        context['subtitle'] = 'Register'
        context['fields'] = {
            'Status': 'Registered' if status.exists() else '--',
            'Warehouse': f'{warehouse}' if status.exists() else '--',
            'Registered Date': status.first().created_at.strftime('%Y-%m-%d %H:%M:%S') if status.exists() and status.first().created_at else '--',
            'Product No': product.sku,
            'Product Name': product.name,
            'Category': product.category,
            'Type': product.product_type,
            'UOM': product.uom,
        }

        if not status.exists():
            context['button_submit'] = f'<button type="button" class="btn btn-success" id="confirm">Submit</button>'

        # context['dynamic_fields'] = dynamic_fields
        return context
    
    def post(self, request, *args, **kwargs):
        product_instance = get_object_or_404(Product, pk=self.kwargs.get('prd'))
        # Get the warehouse instance from the URL parameters ('wh')
        warehouse_instance = get_object_or_404(Warehouse, pk=self.kwargs.get('wh'))

        # Check if the combination of warehouse and product already exists in the database
        if WarehouseProduct.objects.filter(warehouse=warehouse_instance, product=product_instance).exists():
            messages.error(self.request, 'This product is already registered in this warehouse.')
            return redirect(self.request.META.get('HTTP_REFERER'))

        # Initialize the form with the POST data and product instance
        form = WarehouseProductForm(request.POST, product_instance=product_instance, warehouse_instance=warehouse_instance)

        if form.is_valid():
            # Save the form and create the WarehouseProduct
            form.save()
            messages.success(self.request, 'Operation was successful!')
            return redirect(self.request.META.get('HTTP_REFERER'))

        # Re-render the form with the error messages
        messages.error(self.request, 'Something wrong.')
        return self.render_to_response(self.get_context_data(form=form))
    
class DetailWarehouseProduct(DetailView):
    model = WarehouseProduct
    template_name = 'core/pages/inventory/assign_warehouse/detail.html'
    context_object_name = 'item'

    def dispatch(self, request, *args, **kwargs):
        warehouse_uuid = self.get_object().warehouse

        # Check if the warehouse has been deleted
        if self.model.objects.filter(warehouse=warehouse_uuid, warehouse__deleted_at__isnull=False).exists():
            # Redirect to the DashboardView
            return redirect(reverse('dashboard_view'))  # Replace with actual URL pattern name if different

        # Proceed with the usual dispatch if the condition is not met
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # model_name_separated = get_separated_model_name(self.model.__name__)
        
        # Fetch the product instance based on the pk in the URL
        warehouse_product = self.get_object()
        
        # Initialize the form and pass the product instance to it
        form = WarehouseProductForm(product_instance=warehouse_product.product, warehouse_instance=warehouse_product.warehouse)

        form.fields['warehouse'].widget = TextInput(attrs={'class': 'form-control'})
        form.fields['product'].widget = TextInput(attrs={'class': 'form-control'})
        
        # Menggunakan fungsi pembantu untuk menambahkan field 'created_at', 'updated_at', 'deleted_at'
        update_form = add_datetime_fields_to_form(form, self.object)

        # Menonaktifkan setiap field dalam form
        for field in update_form.fields.values():
            field.disabled = True
        
        context['form'] = update_form

        context['title'] = f'Assign Product'
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': 'Assign Product', 'url': reverse('warehouse_product_list', kwargs={'wh': warehouse_product.warehouse.id})},
            {'name': 'Detail', 'url': None}  # No URL for the last breadcrumb item
        ]

        # Menggunakan fungsi pembantu untuk mendapatkan HTML tombol
        context['button_delete'] = get_delete_restore_button(self.object)
        context['warehouse_id'] = warehouse_product.warehouse.id
        return context
    
class SoftWarehouseProduct(View):
    def post(self, request, pk):
        item = get_object_or_404(WarehouseProduct, pk=pk)

        # Check if 'deleted_at' is not null
        if item.warehouse.deleted_at is not None:
            messages.error(request, 'There were errors in your form submission.')
            return redirect(reverse('dashboard_view'))  # Replace with actual URL pattern name if different

        if item.deleted_at is None:
            item.soft_delete()  # Soft delete the item
        else:
            item.restore()
        messages.success(request, 'The item has been successfully deleted.')

        return redirect('warehouse_product_list', wh=item.warehouse.id)
    
class CreateStockAdjustment(CreateView):
    template_name = 'core/pages/inventory/stock_adjustment/create.html'
    model = StockAdjustment
    form_class = StockAdjustmentForm
    success_message = "Stock adjustment successfully made."

    def get_context_data(self, **kwargs):
        # Get the context data from ListView (for the book list)
        context = super().get_context_data(**kwargs)
        warehouse_uuid = self.kwargs['wh']
        model_name_separated = get_separated_model_name(self.model.__name__)
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': reverse('dashboard_view')},
            {'name': f'{model_name_separated}', 'url': reverse('stock_adjustment_create', kwargs={'wh': warehouse_uuid})},
            {'name': 'Register', 'url': None}  # No URL for the last breadcrumb item
        ]
        
        context['subtitle'] = 'Register'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response

    def get_success_url(self):
        return reverse_lazy('stock_adjustment_list')