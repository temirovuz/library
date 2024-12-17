from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django settings.py faylini o'qish uchun
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')

# Celery-ni Django setting-laridan foydalanishga sozlash
app.config_from_object('django.conf:settings', namespace='CELERY')

# Har qanday avtomatik aniqlangan task-larni yuklash
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
