from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Category, Coupon, Governorate, Order, Review, Announcement

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'description', 'price', 'discount_price', 'image', 'stock', 'is_active']
        labels = {
            'category': 'القسم الرئيسي',
            'name': 'اسم المنتج / القطعة',
            'slug': 'الرابط الفريد (Slug)',
            'description': 'وصف تفصيلي للمنتج',
            'price': 'السعر الأصلي (بالجنيه المصري)',
            'discount_price': 'السعر بعد الخصم (اختياري)',
            'image': 'صورة المنتج',
            'stock': 'الكمية المتوفرة في المخزن',
            'is_active': 'عرض للبيع فوراً (نشط)',
        }
        widgets = {
            'category': forms.Select(attrs={'class': 'form-input'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'مثال: ساعة كلاسيكية كحلي'}),
            'slug': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'مثال: classic-blue-watch'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'اكتب تفاصيل وميزات القطعة...'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '0.00'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '0.00'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-input'}),
            'stock': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label="الاسم الأول", widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=50, required=True, label="اسم العائلة", widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(required=True, label="البريد الإلكتروني", widget=forms.EmailInput(attrs={'class': 'form-input'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')
        labels = {
            'username': 'اسم المستخدم (لتسجيل الدخول)',
        }
        help_texts = {
            'username': 'مطلوب. 150 حرفًا أو أقل. الأحرف والأرقام وعلامات @/./+/-/_ فقط.',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-input'})


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount', 'active']
        labels = {
            'code': 'كود الخصم (كوبون)',
            'discount': 'نسبة الخصم %',
            'active': 'نشط ومتوفر للاستخدام',
        }
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'مثال: SAVE15'}),
            'discount': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 100}),
            'active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class GovernorateForm(forms.ModelForm):
    class Meta:
        model = Governorate
        fields = ['name', 'shipping_cost']
        labels = {
            'name': 'اسم المحافظة',
            'shipping_cost': 'تكلفة الشحن (جنيه مصري)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'مثال: القليوبية'}),
            'shipping_cost': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '0.00'}),
        }


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        labels = {
            'status': 'تعديل حالة الطلب',
        }
        widgets = {
            'status': forms.Select(attrs={'class': 'form-input'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'comment']
        labels = {
            'name': 'الاسم بالكامل / اللقب',
            'rating': 'التقييم بالنجوم',
            'comment': 'اكتب تعليقك ومراجعتك هنا',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'مثال: أحمد محمد'}),
            'rating': forms.Select(attrs={'class': 'form-input'}),
            'comment': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'شاركنا رأيك في جودة القطعة، التغليف، وسرعة التوصيل...'}),
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['text', 'active']
        labels = {
            'text': 'نص الإعلان',
            'active': 'تفعيل الإعلان (معروض في الشريط المتحرك)',
          }
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'مثال: خصم 10% بكود WELCOME10 | شحن مجاني للطلبات فوق 500 جنيه!'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
