from django.test import TestCase
from django.urls import reverse
from .models import Category, Product, Governorate, StoreSetting, Coupon

class StoreTests(TestCase):
    def setUp(self):
        # Create a test category and product
        self.category = Category.objects.create(
            name='ساعات فاخرة',
            slug='watches',
            description='ساعات كلاسيكية'
        )
        self.product = Product.objects.create(
            category=self.category,
            name='ساعة ذهبية',
            slug='gold-watch',
            description='ساعة من الذهب الخالص عيار 18 قيراطاً',
            price=1250.00,
            stock=5,
            is_active=True
        )

    def test_category_and_product_creation(self):
        self.assertEqual(self.category.name, 'ساعات فاخرة')
        self.assertEqual(self.product.name, 'ساعة ذهبية')
        self.assertEqual(self.product.price, 1250.00)

    def test_home_page_status_code(self):
        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'APRICITY')

    def test_shop_page_status_code(self):
        response = self.client.get(reverse('store:shop'))
        self.assertEqual(response.status_code, 200)

    def test_product_detail_page_status_code(self):
        response = self.client.get(reverse('store:product_detail', args=[self.product.id, self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ساعة ذهبية')

    def test_cart_page_status_code(self):
        response = self.client.get(reverse('store:cart_detail'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_status_code(self):
        response = self.client.get(reverse('store:register'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_status_code(self):
        response = self.client.get(reverse('store:login'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_redirects_anonymous_user(self):
        response = self.client.get(reverse('store:dashboard'))
        self.assertEqual(response.status_code, 302) # Redirect to login

    def test_add_product_redirects_anonymous_user(self):
        response = self.client.get(reverse('store:add_product'))
        self.assertEqual(response.status_code, 302) # Redirect to login

    def test_governorate_model_creation(self):
        gov = Governorate.objects.create(name='الجيزة', shipping_cost=40.00)
        self.assertEqual(gov.name, 'الجيزة')
        self.assertEqual(gov.shipping_cost, 40.00)

    def test_coupon_model_creation(self):
        coupon = Coupon.objects.create(code='SALE10', discount=10, active=True)
        self.assertEqual(coupon.code, 'SALE10')
        self.assertEqual(coupon.discount, 10)
        self.assertTrue(coupon.active)

    def test_store_settings_singleton(self):
        settings = StoreSetting.get_settings()
        self.assertEqual(settings.free_shipping_threshold, 500.00)


