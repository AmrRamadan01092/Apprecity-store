from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Governorate(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم المحافظة")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="تكلفة الشحن (جنيه)")

    class Meta:
        verbose_name = "محافظة"
        verbose_name_plural = "المحافظات وتكاليف الشحن"

    def __str__(self):
        return f"{self.name} ({self.shipping_cost} ج.م)"


class StoreSetting(models.Model):
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=500.00, verbose_name="الحد الأدنى للشحن المجاني (جنيه)")

    class Meta:
        verbose_name = "إعدادات المتجر"
        verbose_name_plural = "إعدادات المتجر"

    def __str__(self):
        return "إعدادات المتجر الأساسية"

    @classmethod
    def get_settings(cls):
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create(free_shipping_threshold=500.00)
        return obj


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="كود الخصم")
    discount = models.PositiveIntegerField(verbose_name="نسبة الخصم %")
    active = models.BooleanField(default=True, verbose_name="نشط / متوفر للاستخدام")

    class Meta:
        verbose_name = "كوبون خصم"
        verbose_name_plural = "كوبونات الخصم"

    def __str__(self):
        return f"{self.code} (خصم {self.discount}%)"

class Category(models.Model):
    name = models.CharField(max_length=150, verbose_name="اسم القسم")
    slug = models.SlugField(max_length=150, unique=True, verbose_name="الرابط الفريد (Slug)")
    description = models.TextField(blank=True, verbose_name="وصف القسم")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="صورة القسم")

    class Meta:
        ordering = ('name',)
        verbose_name = "قسم"
        verbose_name_plural = "أقسام المنتجات"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_list_by_category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name="القسم")
    name = models.CharField(max_length=200, verbose_name="اسم المنتج")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="الرابط الفريد (Slug)")
    description = models.TextField(verbose_name="وصف المنتج")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر (جنيه مصري)")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="السعر بعد الخصم (اختياري)")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="صورة المنتج")
    stock = models.IntegerField(default=10, verbose_name="المخزون المتوفر")
    is_active = models.BooleanField(default=True, verbose_name="نشط/متوفر للبيع")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.id, self.slug])

    def get_average_rating(self):
        from django.db.models import Avg
        avg = self.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 1) if avg else 0

    def get_reviews_count(self):
        return self.reviews.count()

    def get_average_rating_range(self):
        avg = self.get_average_rating()
        return range(int(round(avg)))

    def get_average_rating_empty_range(self):
        avg = self.get_average_rating()
        return range(5 - int(round(avg)))


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'قيد الانتظار / معالجة الدفع'),
        ('processing', 'قيد التحضير'),
        ('shipped', 'تم الشحن'),
        ('delivered', 'تم التوصيل / مكتمل'),
        ('cancelled', 'ملغي'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name="المستخدم صاحب الطلب")
    first_name = models.CharField(max_length=100, verbose_name="الاسم الأول")
    last_name = models.CharField(max_length=100, verbose_name="اسم العائلة")
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    governorate = models.ForeignKey(Governorate, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المحافظة")
    city = models.CharField(max_length=100, verbose_name="المدينة / المنطقة")
    address = models.CharField(max_length=250, verbose_name="العنوان بالتفصيل")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="تكلفة شحن الطلب")
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="الكوبون المستخدم")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="مبلغ الخصم المطبق")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="حالة الطلب")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="إجمالي السعر")

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"

    def __str__(self):
        return f"الطلب رقم {self.id} - {self.first_name} {self.last_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="الطلب")
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE, verbose_name="المنتج")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر عند الشراء")
    quantity = models.PositiveIntegerField(default=1, verbose_name="الكمية")

    class Meta:
        verbose_name = "عنصر طلب"
        verbose_name_plural = "عناصر الطلبات"

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"


class Review(models.Model):
    RATING_CHOICES = (
        (1, '★☆☆☆☆ (1/5)'),
        (2, '★★☆☆☆ (2/5)'),
        (3, '★★★☆☆ (3/5)'),
        (4, '★★★★☆ (4/5)'),
        (5, '★★★★★ (5/5)'),
    )
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE, verbose_name="المنتج")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews', verbose_name="المستخدم")
    name = models.CharField(max_length=100, verbose_name="اسم العميل")
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, default=5, verbose_name="التقييم بالنجوم")
    comment = models.TextField(verbose_name="التعليق والملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "تقييم منتج"
        verbose_name_plural = "تقييمات المنتجات"

    def __str__(self):
        return f"تقييم {self.product.name} من {self.name} - {self.rating} نجوم"


class Announcement(models.Model):
    text = models.CharField(max_length=255, verbose_name="نص الإعلان")
    active = models.BooleanField(default=True, verbose_name="نشط / معروض")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "إعلان"
        verbose_name_plural = "إعلانات شريط الإعلانات"

    def __str__(self):
        return self.text
