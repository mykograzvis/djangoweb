from django.core.management.base import BaseCommand
from homepage.models import Product

class Command(BaseCommand):
    help = 'Delete all products from the Product model'

    def handle(self, *args, **options):
        # Delete all objects from the Product model
        Product.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All products deleted successfully'))
