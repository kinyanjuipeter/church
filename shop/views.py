from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import RedirectView

# Redirect views for legacy URLs
def product_list_redirect(request):
    return redirect('/', permanent=True)

def product_detail_redirect(request, id, slug):
    return redirect(f'/{id}/{slug}/', permanent=True) 

def cart_detail_redirect(request):
    return redirect('/cart/', permanent=True)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, Cart, CartItem, Category, Order, OrderItem
from django.views.decorators.http import require_POST

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    return render(request, 
                 'shop/product/list.html',
                 {'category': category,
                  'categories': categories,
                  'products': products})

def product_detail(request, id, slug):
    product = get_object_or_404(Product,
                                id=id,
                                slug=slug,
                                available=True)
    return render(request,
                 'shop/product/detail.html',
                 {'product': product})

def cart_detail(request):
    try:
        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            cart_context = {
                'items': cart.items.all(),
                'get_total_cost': cart.get_total_cost,
                'items_count': cart.items.count()
            }
        else:
            # Handle guest cart
            if 'cart' not in request.session:
                request.session['cart'] = []
            
            cart_items = []
            for item in request.session['cart']:
                try:
                    product = Product.objects.get(id=item['product_id'])
                    cart_items.append({
                        'product': product,
                        'quantity': item['quantity'],
                        'price': product.price,
                        'get_cost': lambda p=product, q=item['quantity']: p.price * q
                    })
                except Product.DoesNotExist:
                    continue
            
            cart_context = {
                'items': cart_items,
                'get_total_cost': lambda: sum(item['get_cost']() for item in cart_items),
                'items_count': len(cart_items)
            }
        
        return render(request, 'shop/cart/detail.html', {'cart': cart_context})
    except Exception as e:
        from django.http import HttpResponseServerError
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error loading cart: {str(e)}")
        return HttpResponseServerError("Error loading cart. Please try again.")
        # Handle guest cart from session
        if 'cart' not in request.session:
            request.session['cart'] = []
        
        # Create a Cart-like object for the template
        class GuestCart:
            def __init__(self, session_cart):
                self.items = []
                self.session_cart = session_cart
                
                for item in session_cart:
                    try:
                        product = Product.objects.get(id=item['product_id'])
                        self.items.append(GuestCartItem(product, item['quantity']))
                    except Product.DoesNotExist:
                        continue
            
            def get_total_cost(self):
                return sum(item.get_cost() for item in self.items)
            
            @property
            def items_count(self):
                return len(self.items)

        class GuestCartItem:
            def __init__(self, product, quantity):
                self.product = product
                self.quantity = quantity
                
            def get_cost(self):
                return self.product.price * self.quantity
            
            @property
            def price(self):
                return self.product.price

        guest_cart = GuestCart(request.session['cart'])
        return render(request, 'shop/cart/detail.html', {'cart': guest_cart})

def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'total_items': cart.get_total_items(),
                    'message': f"Added {quantity} {product.name} to cart"
                })
        else:
            # Handle guest cart in session
            if 'cart' not in request.session:
                request.session['cart'] = []
                
            # Find existing item or add new one
            cart = request.session['cart']
            item_exists = False
            for item in cart:
                if item['product_id'] == product.id:
                    item['quantity'] += quantity
                    item_exists = True
                    break
            
            if not item_exists:
                cart.append({
                    'product_id': product.id,
                    'quantity': quantity
                })
            
            request.session.modified = True
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'total_items': sum(item['quantity'] for item in cart),
                    'message': f"Added {quantity} {product.name} to cart"
                })
        
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages.success(request, f"Added {quantity} {product.name} to cart")
        return redirect('shop_cart:cart_detail')
        
    return redirect('shop_cart:product_detail', id=product.id, slug=product.slug)

def order_confirmation(request):
    order_id = request.session.get('last_order_id')
    if not order_id:
        messages.error(request, "No order found")
        return redirect('shop_cart:product_list')
    
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shop/order/confirmation.html', {'order': order})

def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
            messages.success(request, f"Removed {product.name} from cart")
        except CartItem.DoesNotExist:
            messages.error(request, "Item not in cart")
    else:
        # Handle guest cart in session
        if 'cart' in request.session:
            cart = request.session['cart']
            for i, item in enumerate(cart):
                if item['product_id'] == product.id:
                    if item['quantity'] > 1:
                        item['quantity'] -= 1
                    else:
                        cart.pop(i)
                    request.session.modified = True
                    messages.success(request, f"Removed {product.name} from cart")
                    break
            else:
                messages.error(request, "Item not in cart")
    
    return redirect('shop_cart:cart_detail')

import logging
logger = logging.getLogger(__name__)

@login_required
@require_POST
def create_order(request):
    """Handle order creation for authenticated users"""
    logger.info("Create order request received")
    try:
        logger.debug(f"User: {request.user}, Cart items: {request.user.cart.items.count()}")
        cart = get_object_or_404(Cart, user=request.user)
        if not cart.items.exists():
            messages.error(request, "Your cart is empty")
            return redirect('shop_cart:cart_detail')
            
        # Create order
        order = Order.objects.create(
            user=request.user,
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            email=request.user.email,
            phone_number=request.user.profile.phone_number if hasattr(request.user, 'profile') else '',
            address=request.user.profile.address if hasattr(request.user, 'profile') else '',
            postal_code=request.user.profile.postal_code if hasattr(request.user, 'profile') else '',
            city=request.user.profile.city if hasattr(request.user, 'profile') else '',
            location=request.user.profile.location if hasattr(request.user, 'profile') else '',
            status='pending'
        )
        
        # Add all cart items to order
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )
        
        # Clear the cart
        cart.items.all().delete()
        
        # Store order ID in session
        request.session['last_order_id'] = order.id
        
        messages.success(request, "Order placed successfully!")
        return redirect('shop_cart:order_confirmation')
        
    except Exception as e:
        messages.error(request, f"Error placing order: {str(e)}")
        return redirect('shop_cart:cart_detail')

def cart_update(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)
        
        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            try:
                cart_item = CartItem.objects.get(cart=cart, product=product)
                if quantity > 0:
                    cart_item.quantity = quantity
                    cart_item.save()
                    messages.success(request, "Cart updated")
                else:
                    cart_item.delete()
                    messages.success(request, "Item removed from cart")
            except CartItem.DoesNotExist:
                messages.error(request, "Item not in cart")
        else:
            # Handle guest cart in session
            if 'cart' in request.session:
                cart = request.session['cart']
                for item in cart:
                    if item['product_id'] == product.id:
                        if quantity > 0:
                            item['quantity'] = quantity
                            messages.success(request, "Cart updated")
                        else:
                            cart.remove(item)
                            messages.success(request, "Item removed from cart")
                        request.session.modified = True
                        break
                else:
                    messages.error(request, "Item not in cart")
            
    return redirect('shop_cart:cart_detail')

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

@require_POST
def guest_checkout(request):
    if not request.session.get('cart'):
        messages.error(request, "Your cart is empty")
        return redirect('shop_cart:cart_detail')
    
    try:
        required_fields = ['first_name', 'last_name', 'phone_number', 'location']
        
        # Validate required fields exist and are not empty
        for field in required_fields:
            if not request.POST.get(field):
                messages.error(request, f"Please provide your {field.replace('_', ' ')}")
                return redirect('shop_cart:cart_detail')
                
        # Get validated form data
        first_name = request.POST['first_name'].strip()
        last_name = request.POST['last_name'].strip()
        phone_number = request.POST['phone_number'].strip()
        location = request.POST['location'].strip()
        email = request.POST.get('email', '').strip()
        
        # Create order
        order = Order.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            location=location,
            address='Guest order',
            postal_code='00000',
            city='N/A',
            status='pending'
        )
        
        # Add order items
        for item in request.session['cart']:
            try:
                product = Product.objects.get(id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=item['quantity']
                )
            except Product.DoesNotExist:
                continue
        
        # Clear cart and store order ID in session for confirmation
        order_id = order.id
        del request.session['cart']
        request.session['last_order_id'] = order_id
        
        return redirect('shop_cart:order_confirmation')
        
    except Exception as e:
        messages.error(request, f"An error occurred while processing your order: {str(e)}")
        return redirect('shop_cart:cart_detail')
