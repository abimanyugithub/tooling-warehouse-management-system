from django.urls import path
from . import views

urlpatterns = [
    path('kabupaten-kota/', views.get_kabupaten_kota, name='get_kabupaten_kota'),
    path('kecamatan/', views.get_kecamatan, name='get_kecamatan'),
    path('kelurahan-desa/', views.get_kelurahan_desa, name='get_kelurahan_desa'),

    path('', views.DashboardView.as_view(), name='dashboard_view'),

    # category
    path('core/warehouse/create/', views.CreateWarehouse.as_view(), name='warehouse_create'),
    path('core/warehouse/update/<uuid:pk>/', views.UpdateWarehouse.as_view(), name='warehouse_update'),
    path('core/warehouse/list/', views.ListWarehouse.as_view(), name='warehouse_list'),
    path('core/warehouse/detail/<uuid:pk>/', views.DetailWarehouse.as_view(), name='warehouse_detail'),
    path('core/warehouse/delete/<uuid:pk>/', views.SoftDeleteWarehouse.as_view(), name='warehouse_delete'),

    # path('core/product/category/list', views.ViewProductCategory.as_view(), name='product_category_list'),

    # category
    path('core/product/category/list/', views.ListProductCategory.as_view(), name='product_category_list'),
    path('core/product/category/create/', views.CreateProductCategory.as_view(), name='product_category_create'),
    path('core/product/category/update/<uuid:pk>/', views.UpdateProductCategory.as_view(), name='product_category_update'),
    path('core/product/category/detail/<uuid:pk>/', views.DetailProductCategory.as_view(), name='product_category_detail'),
    path('core/product/category/delete/<uuid:pk>/', views.SoftDeleteProductCategory.as_view(), name='product_category_delete'),

    # UOM
    path('core/product/uom/list/', views.ListProductUOM.as_view(), name='product_uom_list'),
    path('core/product/uom/create/', views.CreateProductUOM.as_view(), name='product_uom_create'),
    path('core/product/uom/update/<uuid:pk>/', views.UpdateProductUOM.as_view(), name='product_uom_update'),
    path('core/product/uom/detail/<uuid:pk>/', views.DetailProductUOM.as_view(), name='product_uom_detail'),
    path('core/product/uom/delete/<uuid:pk>/', views.SoftDeleteProductUOM.as_view(), name='product_uom_delete'),

    # type
    path('core/product/type/list/', views.ListProductType.as_view(), name='product_type_list'),
    path('core/product/type/create/', views.CreateProductType.as_view(), name='product_type_create'),
    path('core/product/type/detail/<uuid:pk>/', views.DetailProductType.as_view(), name='product_type_detail'),
    path('core/product/type/update/<uuid:pk>/', views.UpdateProductType.as_view(), name='product_type_update'),
    path('core/product/type/delete/<uuid:pk>/', views.SoftDeleteProductType.as_view(), name='product_type_delete'),

    # product
    path('core/product/list/', views.ListProduct.as_view(), name='product_list'),
    path('core/product/create/', views.CreateProduct.as_view(), name='product_create'),
    path('core/product/update/<uuid:pk>/', views.UpdateProduct.as_view(), name='product_update'),
    path('core/product/detail/<uuid:pk>/', views.DetailProduct.as_view(), name='product_detail'),
    path('core/product/delete/<uuid:pk>/', views.SoftDeleteProduct.as_view(), name='product_delete'),

    # assign product to warehouse
    path('inventory/warehouse-product/list/<uuid:wh>/', views.ListWarehouseProduct.as_view(), name='warehouse_product_list'),
    path('inventory/warehouse-product/<uuid:wh>/', views.QueryWarehouseProduct.as_view(), name='warehouse_product_query'),
    path('inventory/warehouse-product/create/<uuid:wh>/<uuid:prd>/', views.CreateWarehouseProduct.as_view(), name='warehouse_product_create'),
    path('inventory/warehouse-product/detail/<uuid:pk>/', views.DetailWarehouseProduct.as_view(), name='warehouse_product_detail'),
    path('inventory/warehouse-product/delete/<uuid:pk>/', views.SoftWarehouseProduct.as_view(), name='warehouse_product_delete'),
]