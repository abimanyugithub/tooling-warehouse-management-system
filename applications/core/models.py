import uuid, random
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.forms import ValidationError
from applications.mapping.models import Provinsi, KabupatenKota, Kecamatan, KelurahanDesa
# from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone

# Create your models here.
class Warehouse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique identifier
    code = models.CharField(max_length=20, unique=True)  # unique=True memastikan bahwa tidak ada dua entri
    name = models.CharField(max_length=255) 
    zone = models.CharField(max_length=255)
    # capacity = models.PositiveIntegerField(blank=True, null=True) # Kapasitas maksimum warehouse
    capacity = models.IntegerField(validators=[MinValueValidator(1)], blank=True, null=True)
    manager = models.CharField(max_length=255, blank=True, null=True)  # Nama manajer gudang
    current_inventory = models.PositiveIntegerField(default=0)  # Jumlah inventaris saat ini
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # active = models.BooleanField(default=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True, verbose_name='Alamat Baris 1')
    address_line2 = models.CharField(max_length=255, blank=True, null=True, verbose_name='Alamat Baris 2')
    province = models.ForeignKey(Provinsi, on_delete=models.CASCADE, blank=True, null=True)
    regency = models.ForeignKey(KabupatenKota, on_delete=models.CASCADE, blank=True, null=True)
    district = models.ForeignKey(Kecamatan, on_delete=models.CASCADE, blank=True, null=True)
    village = models.ForeignKey(KelurahanDesa, on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True, verbose_name='Alamat Email')
    phone_number = models.CharField(max_length=15, blank=True, null=True, validators=[RegexValidator(r'^\+?1?\d{9,15}$', "Phone number must be entered in the format: '+6281234567890'. Up to 15 digits allowed.")])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True) # Tracks soft delete timestamp

    # phone_number = PhoneNumberField(blank=True)
    def __str__(self):
        return f"{self.code} ({self.name})"
    
    def soft_delete(self):
        self.deleted_at = timezone.now()  # Set waktu penghapusan
        self.save()

    def restore(self):
        self.deleted_at = None  # Menghapus waktu penghapusan
        self.save()
    
    class Meta:
        ordering = ['code']


class ProductCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique identifier
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True) # Tracks soft delete timestamp

    def __str__(self):
        return self.name
    
    def soft_delete(self):
        self.deleted_at = timezone.now()  # Set waktu penghapusan
        self.save()

    def restore(self):
        self.deleted_at = None  # Menghapus waktu penghapusan
        self.save()

    class Meta:
        ordering = ['name']


class ProductUOM(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10)  # For example, kg, l, m
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True) # Tracks soft delete timestamp

    def __str__(self):
        return f"{self.code} ({self.name})"
    
    def soft_delete(self):
        self.deleted_at = timezone.now()  # Set waktu penghapusan
        self.save()

    def restore(self):
        self.deleted_at = None  # Menghapus waktu penghapusan
        self.save()
    
    class Meta:
        ordering = ['code']
    
    
class ProductType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True) 
    code = models.CharField(max_length=10)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True) # Tracks soft delete timestamp

    def __str__(self):
        return f"{self.code} ({self.name})"
    
    def soft_delete(self):
        self.deleted_at = timezone.now()  # Set waktu penghapusan
        self.save()

    def restore(self):
        self.deleted_at = None  # Menghapus waktu penghapusan
        self.save()
    
    class Meta:
        ordering = ['code']
    
    
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique identifier
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    # price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    # suppliers = models.ManyToManyField(Supplier, related_name='products')  # Many-to-many relationship
    uom = models.ForeignKey(ProductUOM, on_delete=models.CASCADE)
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    sku = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE,)
    deleted_at = models.DateTimeField(null=True, blank=True) # Tracks soft delete timestamp

    '''def generate_sku(self):
        """Generate a random SKU string of length 10 (you can adjust this length)."""
        return ''.join(random.choices('0123456789', k=10))  # Menghasilkan angka acak

    def save(self, *args, **kwargs):
        if not self.sku:  # Jika SKU tidak diisi, maka akan digenerate
            self.sku = self.generate_sku()

        super(Product, self).save(*args, **kwargs)'''

    def __str__(self):
        return f"{self.sku} ({self.name})"
    
    def soft_delete(self):
        self.deleted_at = timezone.now()  # Set waktu penghapusan
        self.save()

    def restore(self):
        self.deleted_at = None  # Menghapus waktu penghapusan
        self.save()
    
    class Meta:
        ordering = ['sku']


class WarehouseProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True) # Tracks soft delete timestamp

    def soft_delete(self):
        self.deleted_at = timezone.now()  # Set waktu penghapusan
        self.save()

    def restore(self):
        self.deleted_at = None  # Menghapus waktu penghapusan
        self.save()


class WarehouseStockProduct(models.Model):
    warehouse = models.ForeignKey(Warehouse, related_name='stocks', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='stocks', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)  # Menyimpan jumlah stok untuk setiap produk di warehouse
    
    def __str__(self):
        return f"Stock for {self.product.name} at {self.warehouse.name} - {self.quantity} units"


class StockAdjustment(models.Model):
    ADJUSTMENT_CHOICES = (
        ('increase', 'Increase'),
        ('decrease', 'Decrease'),
    )
    
    warehouse = models.ForeignKey(Warehouse, related_name='adjustments', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='adjustments', on_delete=models.CASCADE)
    adjustment_type = models.CharField(max_length=10, choices=ADJUSTMENT_CHOICES)
    quantity = models.IntegerField()  # Jumlah perubahan stok (positif atau negatif)
    reason = models.TextField(null=True, blank=True)  # Alasan penyesuaian stok (misalnya pengembalian, kerusakan)
    created_at = models.DateTimeField(default=timezone.now)
    
    def save(self, *args, **kwargs):
        # Mengambil stok produk yang bersangkutan di warehouse yang sesuai
        stock = WarehouseStockProduct.objects.get(warehouse=self.warehouse, product=self.product)
        
        # Saat penyesuaian stok dilakukan, update stok terkait
        if self.adjustment_type == 'increase':
            stock.quantity += self.quantity
        elif self.adjustment_type == 'decrease':
            stock.quantity -= self.quantity
        
        # Pastikan jumlah stok tidak kurang dari 0
        stock.quantity = max(stock.quantity, 0)
        
        stock.save()  # Simpan stok yang telah diupdate
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.adjustment_type.capitalize()} {self.quantity} units of {self.product.name} in {self.warehouse.name} for {self.reason}"

