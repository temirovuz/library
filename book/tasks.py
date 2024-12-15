from celery import shared_task
from .models import Rental
from django.utils import timezone

@shared_task
def calculate_penalties():

    now = timezone.now()
    rentals = Rental.objects.filter(status='ijara')
    for rental in rentals:
        rental.calculate_penalty()

@shared_task
def cancel_bron_if_not_collected():
    rentals = Rental.objects.filter(status='bron')

    for rental in rentals:
        rental.cancel_bron()
