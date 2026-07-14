from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Governorate, StoreSetting, Coupon

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'category']
    list_editable = ['price', 'discount_price', 'stock', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'phone', 'governorate', 'city', 'shipping_cost', 'discount_amount', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'governorate']
    list_editable = ['status']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'address']
    inlines = [OrderItemInline]


@admin.register(Governorate)
class GovernorateAdmin(admin.ModelAdmin):
    list_display = ['name', 'shipping_cost']
    list_editable = ['shipping_cost']


@admin.register(StoreSetting)
class StoreSettingAdmin(admin.ModelAdmin):
    list_display = ['free_shipping_threshold']
    
    # Restrict to single setting instance
    def has_add_permission(self, request):
        if self.model.objects.count() > 0:
            return False
        return super().has_add_permission(request)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount', 'active']
    list_editable = ['active']
    search_fields = ['code']
