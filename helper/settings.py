from __future__ import absolute_import, unicode_literals

from django.conf import settings

AWS_REGION = getattr(settings, 'EB_AWS_REGION', 'ap-south-1')  # type: str

AWS_ACCESS_KEY_ID = getattr(settings, 'EB_ACCESS_KEY_ID', '')  
AWS_SECRET_ACCESS_KEY = getattr(settings, 'EB_SECRET_ACCESS_KEY', '') 

ERROR_QUEUE = getattr(settings, 'ERROR_QUEUE', 'error.fifo') 
SERVICE_NAME = getattr(settings, 'SERVICE_NAME', '') 

ERROR_CODES = getattr(settings, 'ERROR_CODES', {})