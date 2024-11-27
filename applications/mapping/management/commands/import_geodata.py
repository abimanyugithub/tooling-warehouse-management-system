import json, os
from django.core.management.base import BaseCommand
from applications.mapping.models import Provinsi, KabupatenKota, Kecamatan, KelurahanDesa

class Command(BaseCommand):
    help = 'Import hierarchical geographical data from a JSON file into the database.'

    '''def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='The path to the JSON file containing the geographical data.')'''
        
    def handle(self, *args, **options):
        json_file_path = os.path.join(
            os.path.dirname(__file__),  # Directory of the current file
            'data_indonesia',  # Data directory
            'kodepos.extended.json' # JSON file name
        )
        
        self.stdout.write(self.style.NOTICE(f'Reading data from "{json_file_path}"...'))
        
        # Load data from JSON file
        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'File "{json_file_path}" not found.'))
            return
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR(f'Error decoding JSON from file "{json_file_path}".'))
            return

        self.stdout.write(self.style.NOTICE('Importing data into the database...'))

        # Populate the database
        for provinsi_name, provinsi_info in data.items():
            provinsi, created = Provinsi.objects.update_or_create(
                id_code=provinsi_info["ID"],
                defaults={'name': provinsi_name}
            )
            action = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f'{action} Provinsi: {provinsi_name} (ID: {provinsi_info["ID"]})'))
            
            for kabupaten_name, kabupaten_info in provinsi_info.get("Kabupaten/Kota", {}).items():
                kabupaten, created = KabupatenKota.objects.update_or_create(
                    id_code=kabupaten_info["ID"],
                    defaults={
                        'provinsi': provinsi,
                        'name': kabupaten_name,
                        'type': kabupaten_info["Type"]
                    }
                )
                action = 'Created' if created else 'Updated'
                self.stdout.write(self.style.SUCCESS(f'  {action} Kabupaten/Kota: {kabupaten_name} (ID: {kabupaten_info["ID"]})'))
                
                for kecamatan_name, kecamatan_info in kabupaten_info.get("Kecamatan", {}).items():
                    kecamatan, created = Kecamatan.objects.update_or_create(
                        id_code=kecamatan_info["ID"],
                        defaults={
                            'kabupaten_kota': kabupaten,
                            'name': kecamatan_name
                        }
                    )
                    action = 'Created' if created else 'Updated'
                    self.stdout.write(self.style.SUCCESS(f'    {action} Kecamatan: {kecamatan_name} (ID: {kecamatan_info["ID"]})'))
                    
                    for desa_name, desa_info in kecamatan_info.get("Kelurahan/Desa", {}).items():
                        kelurahan_desa, created = KelurahanDesa.objects.update_or_create(
                            id_code=desa_info["ID"],
                            defaults={
                                'kecamatan': kecamatan,
                                'name': desa_name,
                                'postal_code': desa_info["Kode Pos"]
                            }
                        )
                        action = 'Created' if created else 'Updated'
                        self.stdout.write(self.style.SUCCESS(f'      {action} Kelurahan/Desa: {desa_name} (ID: {desa_info["ID"]}, Postal Code: {desa_info["Kode Pos"]})'))

        self.stdout.write(self.style.SUCCESS('Data import completed successfully.'))