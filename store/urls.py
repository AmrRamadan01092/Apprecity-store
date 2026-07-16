from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('shop/<slug:category_slug>/', views.shop, name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/api/add/<int:product_id>/', views.cart_add_api, name='cart_add_api'),
    path('cart/api/count/', views.cart_count_api, name='cart_count_api'),
    
    # Customer Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('cart/coupon/', views.apply_coupon, name='apply_coupon'),
    path('cart/shipping/', views.set_shipping_gov, name='set_shipping_gov'),
    
    # Frontend Admin Management URLs
    path('product/add/', views.add_product, name='add_product'),
    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('product/toggle-active/<int:product_id>/', views.toggle_product_active, name='toggle_product_active'),
    path('order/status/<int:order_id>/', views.edit_order_status, name='edit_order_status'),
    path('order/delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('user/delete/<int:user_id>/', views.delete_user_view, name='delete_user'),
    path('coupon/add/', views.add_coupon_view, name='add_coupon'),
    path('coupon/edit/<int:coupon_id>/', views.edit_coupon_view, name='edit_coupon'),
    path('coupon/delete/<int:coupon_id>/', views.delete_coupon_view, name='delete_coupon'),
    path('governorate/add/', views.add_governorate_view, name='add_governorate'),
    path('governorate/edit/<int:gov_id>/', views.edit_governorate_view, name='edit_governorate'),
    path('governorate/delete/<int:gov_id>/', views.delete_governorate_view, name='delete_governorate'),
    
    # Announcement management urls
    path('announcement/add/', views.add_announcement_view, name='add_announcement'),
    path('announcement/edit/<int:ann_id>/', views.edit_announcement_view, name='edit_announcement'),
    path('announcement/delete/<int:ann_id>/', views.delete_announcement_view, name='delete_announcement'),
    path('announcement/toggle-active/<int:ann_id>/', views.toggle_announcement_active, name='toggle_announcement_active'),
]
