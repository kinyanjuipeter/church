from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('shop_cart:product_list_by_category',
                       args=[self.slug])

class Product(models.Model):
    category = models.ForeignKey(Category, models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    brand = models.CharField(max_length=100, blank=True)
    
    def get_discount_percentage(self):
        if self.old_price and self.old_price > self.price:
            return round((1 - (self.price / self.old_price)) * 100)
        return 0
    
    class Meta:
        ordering = ['-created']
        
    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('shop_cart:product_detail',
                       args=[self.id, self.slug])

class Review(models.Model):
    product = models.ForeignKey(Product, models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created']
        
    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"

class Cart(models.Model):
    user = models.OneToOneField(User, models.CASCADE, related_name='cart')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"
        
    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())
        
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
        
    def get_cost(self):
        return self.product.price * self.quantity
        
    @property 
    def price(self):
        return self.product.price

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, default='0000000000')
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    location = models.CharField(max_length=100, default='Nairobi')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created']
        
    def __str__(self):
        return f"Order {self.id}"
        
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, models.CASCADE, related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return str(self.id)
        
    def get_cost(self):
        return self.price * self.quantity
