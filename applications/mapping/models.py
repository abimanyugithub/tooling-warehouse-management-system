from django.db import models

# Create your models here.
class Provinsi(models.Model):
    name = models.CharField(max_length=255, unique=True)
    id_code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class KabupatenKota(models.Model):
    provinsi = models.ForeignKey(Provinsi, on_delete=models.CASCADE, related_name='kabupaten_kota')
    name = models.CharField(max_length=255)
    id_code = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=50)  # e.g., 'Kabupaten' or 'Kota'

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Kecamatan(models.Model):
    kabupaten_kota = models.ForeignKey(KabupatenKota, on_delete=models.CASCADE, related_name='kecamatan')
    name = models.CharField(max_length=255)
    id_code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
    

class KelurahanDesa(models.Model):
    kecamatan = models.ForeignKey(Kecamatan, on_delete=models.CASCADE, related_name='kelurahan_desa')
    name = models.CharField(max_length=255)
    id_code = models.CharField(max_length=20, unique=True)
    postal_code = models.CharField(max_length=10)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
