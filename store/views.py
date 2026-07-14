import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Category, Product, Order, OrderItem, Governorate, StoreSetting, Coupon
from .cart import Cart
from .forms import UserRegisterForm, ProductForm, CouponForm, GovernorateForm, OrderStatusForm

def home(request):
    # Fetch 4 categories and latest 8 products
    categories = Category.objects.all()[:4]
    latest_products = Product.objects.filter(is_active=True)[:8]
    return render(request, 'store/home.html', {
        'categories': categories,
        'latest_products': latest_products
    })

def shop(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True)

    # Search filter
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    # Category filter
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Sorting
    sort_by = request.GET.get('sort', 'latest')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    return render(request, 'store/shop.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'search_query': search_query,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'sort_by': sort_by
    })

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, is_active=True)
    # Recommend 4 related products from the same category
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products
    })

def cart_detail(request):
    cart = Cart(request)
    governorates = Governorate.objects.all()
    settings = StoreSetting.get_settings()
    
    # Read from session
    governorate_id = request.session.get('governorate_id')
    selected_gov = Governorate.objects.filter(id=governorate_id).first() if governorate_id else None
    
    coupon_id = request.session.get('coupon_id')
    selected_coupon = Coupon.objects.filter(id=coupon_id, active=True).first() if coupon_id else None
    
    subtotal = cart.get_total_price()
    
    # Calculate shipping
    free_shipping = False
    if settings and subtotal >= settings.free_shipping_threshold:
        free_shipping = True
        shipping_cost = 0
    elif selected_gov:
        shipping_cost = selected_gov.shipping_cost
    else:
        shipping_cost = 0
        
    # Calculate discount
    discount_amount = 0
    if selected_coupon:
        discount_amount = subtotal * selected_coupon.discount / 100
        
    total_price = subtotal - discount_amount + shipping_cost
    
    if request.method == 'POST':
        # Checkout logic
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()

        if not (first_name and last_name and email and phone and address and city and selected_gov):
            messages.error(request, 'يرجى ملء جميع حقول الطلب والشحن وتحديد المحافظة.')
            return redirect('store:cart_detail')
            
        if len(cart) == 0:
            messages.error(request, 'سلتك فارغة، يرجى إضافة بعض المنتجات أولاً.')
            return redirect('store:shop')

        # Create Order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            governorate=selected_gov,
            city=city,
            address=address,
            shipping_cost=shipping_cost,
            coupon=selected_coupon,
            discount_amount=discount_amount,
            total_price=total_price
        )

        # Create OrderItems
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )
            # Update product stock
            product = item['product']
            product.stock -= item['quantity']
            if product.stock < 0:
                product.stock = 0
            product.save()

        # Clear cart session and variables
        cart.clear()
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
        if 'governorate_id' in request.session:
            del request.session['governorate_id']
        
        messages.success(request, f'تم تسجيل طلبك بنجاح! رقم الطلب هو #{order.id}. شحنتك ستصلك قريباً والدفع عند الاستلام بعد معاينة القطع.')
        return redirect('store:home')

    return render(request, 'store/cart.html', {
        'cart': cart,
        'governorates': governorates,
        'selected_gov': selected_gov,
        'selected_coupon': selected_coupon,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'discount_amount': discount_amount,
        'total_price': total_price,
        'free_shipping_threshold': settings.free_shipping_threshold if settings else 500,
        'free_shipping': free_shipping
    })

def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').strip().upper()
        coupon = Coupon.objects.filter(code=code, active=True).first()
        if coupon:
            request.session['coupon_id'] = coupon.id
            messages.success(request, f'تم تطبيق كود الخصم "{code}" بنجاح! تم خصم {coupon.discount}%')
        else:
            messages.error(request, 'كود الخصم غير صالح أو منتهي الصلاحية.')
    return redirect('store:cart_detail')

def set_shipping_gov(request):
    if request.method == 'POST':
        gov_id = request.POST.get('governorate_id')
        if gov_id:
            request.session['governorate_id'] = int(gov_id)
            messages.success(request, 'تم تحديث المحافظة وحساب تكلفة الشحن.')
    return redirect('store:cart_detail')

@require_POST
def cart_add_api(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
    except (ValueError, json.JSONDecodeError):
        quantity = 1

    if quantity <= 0:
        return JsonResponse({'success': False, 'message': 'الكمية غير صالحة'})
        
    if product.stock < quantity:
        return JsonResponse({'success': False, 'message': f'المخزون المتوفر غير كافٍ. المتوفر: {product.stock} قطع'})

    cart.add(product=product, quantity=quantity)
    return JsonResponse({
        'success': True,
        'message': f'تم إضافة {product.name} إلى السلة بنجاح!'
    })

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f'تم إزالة {product.name} من السلة.')
    return redirect('store:cart_detail')

@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > product.stock:
        messages.error(request, f'المخزون المتوفر غير كافٍ لمنتج {product.name}. المتوفر: {product.stock} قطع.')
    elif quantity <= 0:
        cart.remove(product)
    else:
        cart.add(product=product, quantity=quantity, override_quantity=True)
        messages.success(request, 'تم تحديث كمية المنتج في السلة.')
        
    return redirect('store:cart_detail')

def cart_count_api(request):
    cart = Cart(request)
    return JsonResponse({'count': len(cart)})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('store:dashboard')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f'مرحباً بك يا {user.first_name}! تم إنشاء حسابك بنجاح.')
            return redirect('store:dashboard')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = UserRegisterForm()
    return render(request, 'store/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('store:dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'مرحباً بعودتك، {user.first_name or user.username}!')
                if user.is_staff:
                    return redirect('store:shop')
                return redirect('store:dashboard')
        messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    messages.success(request, 'تم تسجيل خروجك بنجاح. نتمنى رؤيتك قريباً!')
    return redirect('store:home')

@login_required(login_url='store:login')
def dashboard_view(request):
    if request.user.is_staff:
        from django.db.models import Sum
        from django.contrib.auth.models import User as DjangoUser
        
        total_customers = DjangoUser.objects.filter(is_staff=False).count()
        total_orders = Order.objects.count()
        total_sales = Order.objects.exclude(status='cancelled').aggregate(total=Sum('total_price'))['total'] or 0.00
        customers = DjangoUser.objects.filter(is_staff=False).order_by('-date_joined')
        all_orders = Order.objects.all().order_by('-created_at')
        all_coupons = Coupon.objects.all()
        all_govs = Governorate.objects.all()
        
        return render(request, 'store/dashboard.html', {
            'is_manager': True,
            'total_customers': total_customers,
            'total_orders': total_orders,
            'total_sales': total_sales,
            'customers': customers,
            'all_orders': all_orders,
            'all_coupons': all_coupons,
            'all_govs': all_govs
        })
        
    orders = request.user.orders.all()
    return render(request, 'store/dashboard.html', {
        'is_manager': False,
        'orders': orders
    })

@staff_member_required(login_url='store:login')
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'تم إضافة المنتج "{product.name}" بنجاح!')
            return redirect('store:shop')
        else:
            messages.error(request, 'حدث خطأ أثناء إضافة المنتج. يرجى مراجعة البيانات.')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})

@staff_member_required(login_url='store:login')
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_name = product.name
    product.delete()
    messages.success(request, f'تم حذف المنتج "{product_name}" نهائياً من المتجر.')
    return redirect('store:shop')

@staff_member_required(login_url='store:login')
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تعديل المنتج "{product.name}" بنجاح!')
            return redirect('store:product_detail', id=product.id, slug=product.slug)
        else:
            messages.error(request, 'خطأ، يرجى التحقق من المدخلات.')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/add_product.html', {
        'form': form,
        'is_edit': True,
        'product': product,
        'title': 'تعديل تفاصيل المنتج'
    })

@staff_member_required(login_url='store:login')
def edit_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث حالة الطلب #{order.id} بنجاح!')
        else:
            messages.error(request, 'حدث خطأ أثناء تحديث حالة الطلب.')
    return redirect('store:dashboard')

@staff_member_required(login_url='store:login')
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    messages.success(request, f'تم حذف الطلب #{order_id} نهائياً.')
    return redirect('store:dashboard')

@staff_member_required(login_url='store:login')
def delete_user_view(request, user_id):
    from django.contrib.auth.models import User as DjangoUser
    user_to_delete = get_object_or_404(DjangoUser, id=user_id)
    if user_to_delete.is_staff:
        messages.error(request, 'لا يمكن حذف حسابات المشرفين أو المديرين من هنا!')
    else:
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f'تم حذف حساب العميل @{username} نهائياً.')
    return redirect('store:dashboard')

@staff_member_required(login_url='store:login')
def add_coupon_view(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save()
            messages.success(request, f'تم إضافة كوبون الخصم "{coupon.code}" بنجاح!')
            return redirect('store:dashboard')
    else:
        form = CouponForm()
    return render(request, 'store/add_product.html', {
        'form': form,
        'title': 'إضافة كوبون خصم جديد',
        'is_coupon': True
    })

@staff_member_required(login_url='store:login')
def edit_coupon_view(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تعديل كوبون الخصم "{coupon.code}" بنجاح!')
            return redirect('store:dashboard')
    else:
        form = CouponForm(instance=coupon)
    return render(request, 'store/add_product.html', {
        'form': form,
        'title': 'تعديل كوبون الخصم',
        'is_coupon': True,
        'is_edit': True
    })

@staff_member_required(login_url='store:login')
def delete_coupon_view(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    code = coupon.code
    coupon.delete()
    messages.success(request, f'تم حذف كوبون الخصم "{code}" بنجاح.')
    return redirect('store:dashboard')

@staff_member_required(login_url='store:login')
def add_governorate_view(request):
    if request.method == 'POST':
        form = GovernorateForm(request.POST)
        if form.is_valid():
            gov = form.save()
            messages.success(request, f'تم إضافة محافظة "{gov.name}" بنجاح!')
            return redirect('store:dashboard')
    else:
        form = GovernorateForm()
    return render(request, 'store/add_product.html', {
        'form': form,
        'title': 'إضافة محافظة وتكلفة شحن جديدة',
        'is_gov': True
    })

@staff_member_required(login_url='store:login')
def edit_governorate_view(request, gov_id):
    gov = get_object_or_404(Governorate, id=gov_id)
    if request.method == 'POST':
        form = GovernorateForm(request.POST, instance=gov)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تعديل شحن محافظة "{gov.name}" بنجاح!')
            return redirect('store:dashboard')
    else:
        form = GovernorateForm(instance=gov)
    return render(request, 'store/add_product.html', {
        'form': form,
        'title': 'تعديل سعر شحن المحافظة',
        'is_gov': True,
        'is_edit': True
    })

@staff_member_required(login_url='store:login')
def delete_governorate_view(request, gov_id):
    gov = get_object_or_404(Governorate, id=gov_id)
    name = gov.name
    gov.delete()
    messages.success(request, f'تم حذف محافظة "{name}" وتكلفة شحنها بنجاح.')
    return redirect('store:dashboard')
