from .models import Category, Cart

def categories(request):
    return {
        'categories': Category.objects.all()
    }

def cart(request):
    from .models import Product

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Convert items to list with all required data
        cart.items_list = []
        for item in cart.items.all().select_related('product'):
            cart.items_list.append({
                'product': item.product,
                'quantity': item.quantity,
                'price': item.product.price,
                'get_cost': item.product.price * item.quantity
            })
    else:
        # Create enhanced cart object for guests
        class GuestCart:
            def __init__(self, session):
                self.session = session
                self.items_list = []
                self._total_cost = 0
                
                for item in session.get('cart', []):
                    try:
                        product = Product.objects.get(id=item['product_id'], available=True)
                        if product:
                            item_data = {
                                'product': product,
                                'quantity': item['quantity'],
                                'price': product.price,
                                'get_cost': product.price * item['quantity']
                            }
                            self.items_list.append(item_data)
                            self._total_cost += item_data['get_cost']
                    except Product.DoesNotExist:
                        continue
            
            @property
            def items_count(self):
                return sum(item['quantity'] for item in self.items_list)
            
            def get_total_cost(self):
                return self._total_cost
        
        cart = GuestCart(request.session)
    
    return {
        'cart': cart
    }
