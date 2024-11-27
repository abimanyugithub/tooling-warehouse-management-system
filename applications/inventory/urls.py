from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard_view'),
    path('inventory/warehouse/create', views.CreateWarehouse.as_view(), name='warehouse_create'),
    path('inventory/warehouse/update/<uuid:pk>', views.UpdateWarehouse.as_view(), name='warehouse_update'),
    path('inventory/warehouse/list', views.ListWarehouse.as_view(), name='warehouse_list'),
    path('inventory/warehouse/detail/<uuid:pk>', views.DetailWarehouse.as_view(), name='warehouse_detail'),

    path('kabupaten-kota/', views.get_kabupaten_kota, name='get_kabupaten_kota'),
    path('kecamatan/', views.get_kecamatan, name='get_kecamatan'),
    path('kelurahan-desa/', views.get_kelurahan_desa, name='get_kelurahan_desa'),
    
]