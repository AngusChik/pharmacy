from django.db import models

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Category(models.Model):
    id = models.AutoField(primary_key=True)  # Explicit primary key
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

#inventory
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)  # Explicit primary key
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)  # Renamed field
    item_number = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    barcode = models.CharField(max_length=30)
    quantity_in_stock = models.IntegerField(blank=True)  # Renamed field
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Changed from ForeignKey to CharField
    unit_size = models.CharField(max_length=50, blank=True)  # Unit Size field
    description = models.TextField(blank=True)  # Description field
    discount = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name
 
### Purchase -- update inventory 
class Order(models.Model): # the order
    order_id = models.AutoField(primary_key=True)  # Explicit primary key
    #customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE) #FK
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Ensure default is set to 0
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id}"

class OrderDetail(models.Model):
    od_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
        