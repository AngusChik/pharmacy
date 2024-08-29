import csv
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory.settings')
django.setup()

from app.models import Product, Category  # Replace 'inventory' with your actual app name

def import_products(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            category, created = Category.objects.get_or_create(name=row['Category'])
            Product.objects.create(
                name=row['name'],
                brand=row['brand'],
                item_number=row['item_number'],
                price=row['price'],
                barcode=row['barcode'],
                quantity_in_stock=row['quantity_in_stock'],
                category=category,
                unit_size=row['unit_size'],
                description=row['description'],
                discount=row.get('discount', '')  # Use .get() to avoid KeyError
            )
            
if __name__ == '__main__':
    csv_file_path = 'Sheet16.csv'
    import_products(csv_file_path)