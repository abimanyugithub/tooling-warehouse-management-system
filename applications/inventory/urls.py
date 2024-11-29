from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard_view'),
    path('inventory/warehouse/create', views.CreateWarehouse.as_view(), name='warehouse_create'),
    path('inventory/warehouse/update/<uuid:pk>', views.UpdateWarehouse.as_view(), name='warehouse_update'),
    path('inventory/warehouse/list', views.ListWarehouse.as_view(), name='warehouse_list'),
    path('inventory/warehouse/detail/<uuid:pk>', views.DetailWarehouse.as_view(), name='warehouse_detail'),
    path('inventory/warehouse/delete/<uuid:pk>/', views.SoftDeleteWarehouse.as_view(), name='warehouse_delete'),

    # path('inventory/product/category/list', views.ViewProductCategory.as_view(), name='product_category_list'),
    path('inventory/product/category/list', views.ListProductCategory.as_view(), name='product_category_list'),
    path('inventory/product/category/create', views.CreateProductCategory.as_view(), name='product_category_create'),
    path('inventory/product/category/update/<uuid:pk>', views.UpdateProductCategory.as_view(), name='product_category_update'),
    path('inventory/product/category/detail/<uuid:pk>', views.DetailProductCategory.as_view(), name='product_category_detail'),

    path('inventory/product/uom/list', views.ListProductUOM.as_view(), name='product_uom_list'),
    path('inventory/product/uom/create', views.CreateProductUOM.as_view(), name='product_uom_create'),
    path('inventory/product/uom/update/<uuid:pk>', views.UpdateProductUOM.as_view(), name='product_uom_update'),
    path('inventory/product/uom/detail/<uuid:pk>', views.DetailProductUOM.as_view(), name='product_uom_detail'),

    path('kabupaten-kota/', views.get_kabupaten_kota, name='get_kabupaten_kota'),
    path('kecamatan/', views.get_kecamatan, name='get_kecamatan'),
    path('kelurahan-desa/', views.get_kelurahan_desa, name='get_kelurahan_desa'),
    
]