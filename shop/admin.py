from django.contrib import admin
from .models import Category, Product, Review, Order, OrderItem

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'available')
    list_filter = ('available', 'created', 'updated')
    list_editable = ('price', 'stock', 'available')
    prepopulated_fields = {'slug': ('name',)}

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone_number', 'location', 
                   'status', 'created', 'updated', 'user')
    list_filter = ('status', 'created', 'updated')
    search_fields = ('first_name', 'last_name', 'phone_number', 'location')
    inlines = [OrderItemInline]

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review)
admin.site.register(Order, OrderAdmin)
