from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView, UpdateView, DetailView, View
from .models import Warehouse, KabupatenKota, Kecamatan, KelurahanDesa, ProductCategory, ProductUOM, ProductType, Product
from .forms import WarehouseForm, ProductCategoryForm, ProductUOMForm, ProductTypeForm, ProductForm
import re
from django.contrib import messages

# Fungsi untuk memisahkan nama model
def get_separated_model_name(model_name):
    separated = re.findall('[A-Z][^A-Z]*', model_name)
    return ' '.join(separated)

# Create your views here.
class DashboardView(TemplateView):
    template_name = 'core/pages/index.html'

class ListWarehouse(ListView):
    model = Warehouse
    template_name = 'core/pages/warehouse/list.html'
    context_object_name = 'list_item'
    ordering = ['code']

    def get_queryset(self):
        return Warehouse.get_active()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name_separated = get_separated_model_name(self.model.__name__)
        context['fields'] = {
            'code': 'Warehouse Code',
            'name': 'Warehouse Name',
            'zone': 'Area',
            'phone_number': 'Phone Number',
            'email': 'Email Address',
            'manager': 'Manager'
        }
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'warehouse_list'},
            {'name': 'List', 'url': None}  # No URL for the last breadcrumb item
        ]

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
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'warehouse_list'},
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
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'warehouse_list'},
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
        # Initialize the form and add it to the context
        form = WarehouseForm(instance=self.object)
        # Menonaktifkan setiap field dalam form
        for field in form.fields.values():
            field.disabled = True
        
        context['form'] = form     
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'warehouse_list'},
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
        
        return context
    
class SoftDeleteWarehouse(View):
    def post(self, request, pk):
        item = get_object_or_404(Warehouse, pk=pk)
        item.soft_delete()  # Soft delete the item
        messages.success(request, 'The item has been successfully deleted.')

        return redirect('warehouse_list')
    
'''
class RestoreItemView(View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        item.restore()  # Restore the soft deleted item
        return redirect('trash_list')
'''
    
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

class ListProductCategory(ListView):
    model = ProductCategory
    template_name = 'core/pages/product/category/list.html'
    context_object_name = 'list_item'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        separated = re.findall('[A-Z][^A-Z]*', self.model.__name__)
        model_name_separated = ' '.join(separated)
        context['fields'] = {
            'name': 'Category Name',
            'description': 'Description',
        }

        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_category_list'},
            {'name': 'List', 'url': None}  # No URL for the last breadcrumb item
        ]

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
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_category_list'},
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

'''
class ViewProductCategory(CreateView, ListView):
    model = ProductCategory
    template_name = 'core/pages/product/category/list.html'
    context_object_name = 'list_item'  # Name for the list of books in the context
    form_class = ProductCategoryForm
    success_url = reverse_lazy('product_category_list')  

    def get_context_data(self, **kwargs):
        # Get the context data from ListView (for the book list)
        context = super().get_context_data(**kwargs)
        # Add the form to the context for the CreateView (form to add a new book)
        context['form'] = self.get_form()
        separated = re.findall('[A-Z][^A-Z]*', self.model.__name__)
        model_name_separated = ' '.join(separated)
        context['fields'] = {
            'name': 'Category Name',
            'description': 'Description',
        }

        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_category_list'},
            {'name': 'Register and List', 'url': None}  # No URL for the last breadcrumb item
        ]
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Operation was successful!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "There were errors in your form submission.")
        return HttpResponseRedirect(reverse('product_category_list'))
'''
    
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
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_category_list'},
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
        # Initialize the form and add it to the context
        form = ProductCategoryForm(instance=self.object)
        # Menonaktifkan setiap field dalam form
        for field in form.fields.values():
            field.disabled = True
        
        context['form'] = form
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_category_list'},
            {'name': 'Detail', 'url': None}  # No URL for the last breadcrumb item
        ]
        
        return context
    
class ListProductUOM(ListView):
    model = ProductUOM
    template_name = 'core/pages/product/uom/list.html'
    context_object_name = 'list_item'
    ordering = ['name']

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
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_uom_list'},
            {'name': 'List', 'url': None}  # No URL for the last breadcrumb item
        ]

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
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_uom_list'},
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
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_uom_list'},
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
        # Initialize the form and add it to the context
        form = ProductUOMForm(instance=self.object)
        # Menonaktifkan setiap field dalam form
        for field in form.fields.values():
            field.disabled = True
        
        context['form'] = form
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_uom_list'},
            {'name': 'Detail', 'url': None}  # No URL for the last breadcrumb item
        ]
        
        return context

class ListProductType(ListView):
    model = ProductType
    template_name = 'core/pages/product/type/list.html'
    context_object_name = 'list_item'
    ordering = ['name']

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
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_type_list'},
            {'name': 'List', 'url': None}  # No URL for the last breadcrumb item
        ]

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
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_type_list'},
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
        # Initialize the form and add it to the context
        form = ProductTypeForm(instance=self.object)
        # Menonaktifkan setiap field dalam form
        for field in form.fields.values():
            field.disabled = True
        
        context['form'] = form
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_type_list'},
            {'name': 'Detail', 'url': None}  # No URL for the last breadcrumb item
        ]
        
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
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_uom_list'},
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
    
class ListProduct(ListView):
    model = Product
    template_name = 'core/pages/product/list.html'
    context_object_name = 'list_item'
    ordering = ['name']
    paginate_by = 100

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
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_list'},
            {'name': 'List', 'url': None}  # No URL for the last breadcrumb item
        ]

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
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_list'},
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
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_list'},
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
        # Initialize the form and add it to the context
        form = ProductForm(instance=self.object)
        # Menonaktifkan setiap field dalam form
        for field in form.fields.values():
            field.disabled = True
        
        context['form'] = form
        context['title'] = model_name_separated
        context['breadcrumb'] = [
            {'name': 'Home', 'url': 'dashboard_view'},
            {'name': f'{model_name_separated}', 'url': 'product_list'},
            {'name': 'Detail', 'url': None}  # No URL for the last breadcrumb item
        ]
        
        return context