from .models import Warehouse
from django.urls import reverse

def navbar_context(request):
    list_inventory = []

    list_warehouse = Warehouse.objects.filter(deleted_at__isnull=True).order_by('name')

    if not list_warehouse:
        list_inventory.append(
            '<li><a href="#"><span class="sub-item">No Warehouses Available</span></a></li>'
        )
    else:
        # Loop through each warehouse and build the HTML structure
        for item in list_warehouse:
            warehouse_url = reverse("warehouse_product_query", kwargs={'wh': item.id})
            list_inventory.append(
                f'<li><a data-bs-toggle="collapse" href="#subnav{item.id}">'
                f'<span class="sub-item">{item.name}</span><span class="caret"></span></a>'
                f'<div class="collapse" id="subnav{item.id}"><ul class="nav nav-collapse subnav">'
                f'<li><a href="{warehouse_url}"><span class="sub-item">Assign Product to Warehouse</span></a></li>'
                f'<li><a href="{warehouse_url}"><span class="sub-item">Stock Adjustment</span></a></li>'
                f'</ul></div></li>'
            )
        
    # Join the list into a single string and return the context
    return {
        'list_inventory': ''.join(list_inventory),
    }