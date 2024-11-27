from django import template
from urllib.parse import quote_plus
from django.db.models.fields.files import FieldFile
from django.utils.dateformat import format
import datetime, os
import base64

register = template.Library()

@register.filter
def get_field_value(obj, attr_name):
    """ Filter ini mengambil nilai dari field yang ditentukan dari sebuah instance model Django, dengan penanganan khusus untuk file fields & date. """
    value = getattr(obj, attr_name, None)
    if isinstance(value, FieldFile):
        return os.path.basename(value.name)
    if isinstance(value, datetime.datetime):
        return format(value, 'd/m/Y H:i')
    if isinstance(value, datetime.date):
        return value.strftime('%d-%b-%Y')
    return value