from django.contrib import admin
from .models import Category, Product, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_price', 'stock', 'featured', 'created_at')
    list_filter = ('category', 'featured', 'created_at')
    list_editable = ('price', 'discount_price', 'stock', 'featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'total_cost')

    def total_cost(self, instance):
        return f"₹{instance.total_cost:.2f}"
    total_cost.short_description = 'Line Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'email', 'phone', 'total_price', 'order_status', 'created_at')
    list_filter = ('order_status', 'created_at')
    list_editable = ('order_status',)
    search_fields = ('order_number', 'full_name', 'email', 'phone', 'address')
    readonly_fields = ('order_number', 'total_price', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'

    # Admin actions for quick bulk status changes
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']

    @admin.action(description="Mark selected orders as Processing")
    def mark_as_processing(self, request, queryset):
        queryset.update(order_status='Processing')

    @admin.action(description="Mark selected orders as Shipped")
    def mark_as_shipped(self, request, queryset):
        queryset.update(order_status='Shipped')

    @admin.action(description="Mark selected orders as Delivered")
    def mark_as_delivered(self, request, queryset):
        queryset.update(order_status='Delivered')

    @admin.action(description="Mark selected orders as Cancelled")
    def mark_as_cancelled(self, request, queryset):
        queryset.update(order_status='Cancelled')
