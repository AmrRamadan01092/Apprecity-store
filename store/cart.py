from decimal import Decimal
from django.conf import settings
from .models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        active_price = product.discount_price if product.discount_price else product.price
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(active_price)
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
            
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        
        # Build cart items only for products that exist in the database
        cart = {}
        for product in products:
            pid = str(product.id)
            cart[pid] = self.cart[pid].copy()
            cart[pid]['product'] = product

        # Remove any deleted products from the session cart
        session_keys = list(self.cart.keys())
        for pid in session_keys:
            if pid not in cart:
                del self.cart[pid]
        self.save()

        for item in cart.values():
            db_product = item['product']
            active_price = db_product.discount_price if db_product.discount_price else db_product.price
            item['price'] = Decimal(active_price)
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(item['price'] * item['quantity'] for item in self)

    def clear(self):
        del self.session['cart']
        self.save()
