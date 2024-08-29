from django.contrib import admin
from django.urls import path
from app.views import InventoryView,EditProductView, AddProductView, CheckinProductView, LowStockView, CreateOrderView, LowStockView, OrderView,SubmitOrderView, OrderSuccessView
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('order/', CreateOrderView.as_view(), name='create_order'),
    path('order/submit/', SubmitOrderView.as_view(), name='submit_order'),
    path('order/success/', OrderSuccessView.as_view(), name='order_success'),  # Make sure to create this view
    path('checkin/', CheckinProductView.as_view(), name='checkin'),  # Updated to use the class-based view
    path('inventory/', InventoryView.as_view(), name='inventory_display'),
    path('low-stock/', LowStockView.as_view(), name='low_stock'),  # Low stock class-based view
    path('orders/', OrderView.as_view(), name='order_view'),  # List all orders
    path('product/edit/<int:product_id>/', EditProductView.as_view(), name='edit_product'),  # Edit product URL
    path('new-product/', AddProductView.as_view(), name='new_product'),  # Updated to use the class-based view
]
