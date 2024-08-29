from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic.edit import FormView
from django.contrib import messages  # Import the messages module
from django.db.models import Sum
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.cache import cache
import time
from .forms import  EditProductForm, OrderDetailForm, BarcodeForm
from .models import Product, Category, Order, OrderDetail, Customer


#Django, pycorg, pgadmin4, 
# create edit product on the inventory View 

def home(request):
    return render(request, 'home.html')

class CreateOrderView(View):
    template_name = 'order_form.html'

    def get_order(self, request):
        order_id = request.session.get('order_id')

        # Check if there is an order in the session and if it exists in the database
        if order_id:
            try:
                order = Order.objects.get(order_id=order_id)
            except Order.DoesNotExist:
                # If the order doesn't exist, create a new one
                order = Order.objects.create(total_price=Decimal('0.00'))
                request.session['order_id'] = order.order_id
        else:
            # If no order_id is in the session, create a new order
            order = Order.objects.create(total_price=Decimal('0.00'))
            request.session['order_id'] = order.order_id

        return order

    def get(self, request, *args, **kwargs):
        order = self.get_order(request)
        form = BarcodeForm()
        order_details = order.details.all()

        # Calculate total prices
        total_price_before_tax = sum(detail.price for detail in order_details)
        total_price_after_tax = total_price_before_tax * Decimal('1.13')  # Apply 13% tax

        return render(request, self.template_name, {
            'order': order,
            'form': form,
            'order_details': order_details,
            'total_price_before_tax': total_price_before_tax,
            'total_price_after_tax': total_price_after_tax,
        })

    def post(self, request, *args, **kwargs):
        order = self.get_order(request)
        form = BarcodeForm(request.POST)
        
        if form.is_valid():
            barcode = form.cleaned_data['barcode']
            quantity = form.cleaned_data['quantity']

            # Attempt to find the product by barcode
            try:
                product = Product.objects.get(barcode=barcode)
            except Product.DoesNotExist:
                messages.error(request, f"No product found with the barcode '{barcode}'. Please check and try again.")
                return redirect('create_order')

            # Check if there is enough inventory
            if product.quantity_in_stock < quantity:
                messages.error(request, f"Not enough inventory for {product.name}. Only {product.quantity_in_stock} left in stock.")
                return redirect('create_order')

            price = product.price * quantity

            # Create or update the order detail
            order_detail, created = OrderDetail.objects.get_or_create(
                order=order,
                product=product,
                defaults={'quantity': quantity, 'price': price}
            )
            if not created:
                order_detail.quantity += quantity
                order_detail.price += price
                order_detail.save()

            # Update the order's total price
            order.total_price += price
            order.save()

            # Reduce the quantity in stock
            product.quantity_in_stock -= quantity
            product.save()

            return redirect('create_order')

        order_details = order.details.all()

        # Calculate total prices
        total_price_before_tax = sum(detail.price for detail in order_details)
        total_price_after_tax = total_price_before_tax * Decimal('1.13')  # Apply 13% tax

        return render(request, self.template_name, {
            'order': order,
            'form': form,
            'order_details': order_details,
            'total_price_before_tax': total_price_before_tax,
            'total_price_after_tax': total_price_after_tax,
        })

class SubmitOrderView(View):
    def post(self, request, *args, **kwargs):
        if 'order_id' in request.session:
            order = get_object_or_404(Order, order_id=request.session['order_id'])

            # Clear the session to start a new order
            del request.session['order_id']

            return redirect('order_success')  # Redirect to a success page
        return redirect('create_order')

class OrderSuccessView(View):
    template_name = 'order_success.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class CheckinProductView(View):
    template_name = 'checkin.html'

    def get(self, request):
        # Render the check-in page
        return render(request, self.template_name)

    def post(self, request):
        barcode = request.POST.get('barcode')
        quantity = int(request.POST.get('quantity'))

        if barcode:  # Ensure barcode is not empty
            try:
                product = Product.objects.get(barcode=barcode)
                product.quantity_in_stock += quantity  # Update the stock quantity
                product.save()
                
                # Redirect back to the check-in page with a success message
                return redirect('checkin')
            
            except Product.DoesNotExist:
                # If the product does not exist, redirect to the add new product page, passing the barcode
                return redirect('new_product')

        # If the barcode is empty or any other case, re-render the page
        return render(request, self.template_name)

class OrderView(View):
    template_name = 'order_view.html'

    def get(self, request):
        # Fetch all orders from the database
        orders = Order.objects.all()

        # Render the orders in the template
        return render(request, self.template_name, {
            'orders': orders,
        })

class AddProductView(View):
    template_name = 'new_product.html'

    def get(self, request):
        categories = Category.objects.all()
        return render(request, self.template_name, {'categories': categories})

    def post(self, request):
        name = request.POST['name']
        item_number = request.POST['item_number']
        brand = request.POST['brand']
        barcode = request.POST['barcode']
        price = request.POST['price']
        description = request.POST.get('description', '')
        category_id = request.POST['category']
        unit_size = request.POST['unit_size']
        quantity_in_stock = request.POST['quantity_in_stock']

        category = Category.objects.get(id=category_id)

        # Check if the product with the same barcode already exists
        if Product.objects.filter(barcode=barcode).exists():
            # If product exists, show an error message and redirect back to the form
            messages.error(request, 'A product with this barcode already exists.')
            return redirect('new_product')

        # Create a new product if it doesn't exist
        Product.objects.create(
            name=name, 
            barcode=barcode, 
            price=price, 
            description=description, 
            item_number=item_number,
            unit_size=unit_size,
            brand=brand,
            quantity_in_stock=quantity_in_stock,
            category=category
        )
        return redirect('checkin')

class InventoryView(View):
    template_name = 'inventory_display.html'

    def get(self, request):
        # Directly get the list of categories from the database for the dropdown menu
        categories = Category.objects.all()

        # Get the selected category ID from the request
        selected_category_id = request.GET.get('category_id')
        if selected_category_id:
            selected_category_id = int(selected_category_id)

        # Get the barcode search query from the request
        barcode_query = request.GET.get('barcode_query')

        # Fetch the products, with necessary filters applied
        products = Product.objects.all()

        # Add ordering to the query (e.g., by 'name' or 'id')
        products = products.order_by('name')  # You can change 'name' to any field that suits your needs

        # Filter by category if selected
        if selected_category_id:
            products = products.filter(category_id=selected_category_id)

        # Filter by barcode if query provided
        if barcode_query:
            products = products.filter(barcode__icontains=barcode_query)

        # Implement pagination with 80 items per page
        paginator = Paginator(products, 80)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Render the template with the context
        return render(request, self.template_name, {
            'page_obj': page_obj,
            'categories': categories,
            'selected_category_id': selected_category_id,
            'barcode_query': barcode_query,
        })


class EditProductView(View):
    template_name = 'edit_product.html'

    def get(self, request, product_id):
        product = get_object_or_404(Product, product_id=product_id)
        form = EditProductForm(instance=product)  # Pass the product instance to the form
        return render(request, self.template_name, {
            'form': form,
            'categories': Category.objects.all(),
        })

    def post(self, request, product_id):
        product = get_object_or_404(Product, product_id=product_id)
        form = EditProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()

            # Invalidate the cache after editing
            cache.delete('product_list')

            return redirect('inventory_display')
        return render(request, self.template_name, {
            'form': form,
            'categories': Category.objects.all(),
        })


class LowStockView(View):
    template_name = 'low_stock.html'
    threshold = 1  # Default threshold value for low stock

    def get(self, request):
        start_time = time.time()

        # Get the barcode and category filter values from the request
        barcode_query = request.GET.get('barcode_query')
        selected_category_id = request.GET.get('category_id')

        # Fetch products with quantity_in_stock less than the threshold
        low_stock_products = Product.objects.filter(quantity_in_stock__lt=self.threshold)

        query_time = time.time()
        print(f"Query Time: {query_time - start_time} seconds")

        categories = cache.get('categories')
        if not categories:
            categories = Category.objects.all()
            cache.set('categories', categories, 60 * 15)  # Cache for 15 minutes

        # Apply barcode filter if provided
        if barcode_query:
            low_stock_products = low_stock_products.filter(barcode__icontains=barcode_query)

        # Apply category filter if provided
        if selected_category_id:
            low_stock_products = low_stock_products.filter(category_id=selected_category_id)

        # Implement pagination
        paginator = Paginator(low_stock_products, 80)  # Show 100 products per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Render the template
        response = render(request, self.template_name, {
            'page_obj': page_obj,
            'categories': categories,
            'selected_category_id': selected_category_id,
            'barcode_query': barcode_query,
            'threshold': self.threshold,
        })


        return response

def get_filtered_products(category_id=None):
    """
    Returns a queryset of products filtered by the given category_id.
    If no category_id is provided, returns all products.
    """
    if category_id:
        return Product.objects.filter(category_id=category_id)
    return Product.objects.all()

