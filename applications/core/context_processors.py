from .models import Warehouse
from django.urls import reverse

def navbar_context(request):
    list_inventory = ''

    list_warehouse = Warehouse.objects.filter(active=True, deleted_at__isnull=True)

    for item in list_warehouse:
        list_inventory = (
            f'<li><a href="{reverse("inventory_wh_view")}?wh={item.id}"><span class="sub-item">{item.name}</span></a></li>'
        )
        
    return {
        'list_inventory': list_inventory,
    }