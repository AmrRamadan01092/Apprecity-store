from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Product, Governorate, StoreSetting, Coupon, Announcement

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

    def test_inactive_product_detail_page_returns_404_for_customer(self):
        self.product.is_active = False
        self.product.save()
        response = self.client.get(reverse('store:product_detail', args=[self.product.id, self.product.slug]))
        self.assertEqual(response.status_code, 404)

    def test_inactive_product_detail_page_returns_200_for_staff(self):
        # Create a staff user and login
        staff_user = User.objects.create_user(username='staffmember', password='password', is_staff=True)
        self.client.login(username='staffmember', password='password')
        self.product.is_active = False
        self.product.save()
        response = self.client.get(reverse('store:product_detail', args=[self.product.id, self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '⚠️ هذا المنتج غير نشط')

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

    def test_get_settings_returns_existing(self):
        StoreSetting.objects.all().delete()
        StoreSetting.objects.create(free_shipping_threshold=300.00)
        settings = StoreSetting.get_settings()
        self.assertEqual(settings.free_shipping_threshold, 300.00)

    def test_toggle_product_active(self):
        staff_user = User.objects.create_user(username='staffmember2', password='password', is_staff=True)
        self.client.login(username='staffmember2', password='password')
        self.assertTrue(self.product.is_active)
        
        response = self.client.get(reverse('store:toggle_product_active', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_active)
        
        response = self.client.get(reverse('store:toggle_product_active', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertTrue(self.product.is_active)


class ProductReviewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='سلاسل', slug='necklaces')
        self.product = Product.objects.create(
            category=self.category,
            name='سلسلة ذهب',
            slug='gold-necklace',
            price=1500.00,
            stock=5
        )

    def test_add_review_post(self):
        response = self.client.post(
            reverse('store:product_detail', args=[self.product.id, self.product.slug]),
            {
                'name': 'خالد أحمد',
                'rating': 5,
                'comment': 'سلسلة رائعة جداً والتوصيل سريع!'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.product.reviews.count(), 1)
        review = self.product.reviews.first()
        self.assertEqual(review.name, 'خالد أحمد')
        self.assertEqual(review.rating, 5)


class AnnouncementTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(username='admin_ann', password='password', is_staff=True)
        self.regular_user = User.objects.create_user(username='regular_ann', password='password', is_staff=False)
        self.announcement = Announcement.objects.create(text='إعلان تجريبي نشط', active=True)

    def test_announcement_context_processor(self):
        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('active_announcements', response.context)
        self.assertEqual(list(response.context['active_announcements']), [self.announcement])

    def test_add_announcement_view_staff(self):
        self.client.login(username='admin_ann', password='password')
        response = self.client.post(reverse('store:add_announcement'), {
            'text': 'إعلان جديد للمتجر',
            'active': True
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Announcement.objects.count(), 2)

    def test_add_announcement_view_regular_user_denied(self):
        self.client.login(username='regular_ann', password='password')
        response = self.client.post(reverse('store:add_announcement'), {
            'text': 'إعلان اختراق',
            'active': True
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Announcement.objects.count(), 1)

    def test_edit_announcement_view(self):
        self.client.login(username='admin_ann', password='password')
        response = self.client.post(reverse('store:edit_announcement', args=[self.announcement.id]), {
            'text': 'إعلان معدل بالكامل',
            'active': False
        })
        self.assertEqual(response.status_code, 302)
        self.announcement.refresh_from_db()
        self.assertEqual(self.announcement.text, 'إعلان معدل بالكامل')
        self.assertFalse(self.announcement.active)

    def test_delete_announcement_view(self):
        self.client.login(username='admin_ann', password='password')
        response = self.client.get(reverse('store:delete_announcement', args=[self.announcement.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Announcement.objects.count(), 0)

    def test_toggle_announcement_active(self):
        self.client.login(username='admin_ann', password='password')
        response = self.client.get(reverse('store:toggle_announcement_active', args=[self.announcement.id]))
        self.assertEqual(response.status_code, 302)
        self.announcement.refresh_from_db()
        self.assertFalse(self.announcement.active)
