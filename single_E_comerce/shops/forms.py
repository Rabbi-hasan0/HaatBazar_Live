from django import forms
from .models import Shop, Coupon, ShopSocialMedia, ShopMedia, Events

class ShopSettingsForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = [
            'shop_name', 'shop_description', 'shop_logo', 'banner_image', 
            'theme_color', 'currency', 'timezone', 'invoice_prefix', 
            'email', 'phone', 'shop_address', 'trade_license'
        ]
        widgets = {
            field: forms.TextInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm'})
            for field in ['shop_name', 'invoice_prefix', 'email', 'phone', 'trade_license']
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shop_description'].widget = forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm'})
        self.fields['shop_address'].widget = forms.Textarea(attrs={'rows': 2, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm'})
        self.fields['theme_color'].widget = forms.TextInput(attrs={'type': 'color', 'class': 'h-10 w-20 rounded border border-gray-300 p-1'})

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_amount', 'is_percentage', 'valid_from', 'valid_to', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 text-sm'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 text-sm'}),
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 text-sm'}),
            'valid_to': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 text-sm'}),
            'is_percentage': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = [
            'title', 'description', 'discount_percentage', 
            'banner_desktop', 'banner_mobile', 'product', 
            'start_time', 'end_time', 'status', 'priority'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
    
class ShopSocialMediaForm(forms.ModelForm):
    class Meta:
        model = ShopSocialMedia
        fields = ['platform_name', 'profile_url', 'is_active']
        widgets = {
            'platform_name': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 text-sm',
                'placeholder': 'Like: Facebook, Instagram, YouTube'
            }),
            'profile_url': forms.URLInput(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 text-sm',
                'placeholder': 'https://facebook.com/yourshop'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'
            }),
        }
        
class ShopMediaForm(forms.ModelForm):
    class Meta:
        model = ShopMedia
        fields = ['title', 'file', 'media_type']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border-gray-200 bg-white px-3.5 py-2.5 text-sm font-medium text-slate-800 placeholder-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition duration-200',
                'placeholder': 'Like: Eid Campaign Banner, Side Widget'
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10'
            }),
            'media_type': forms.Select(choices=[('Banner', 'Banner'), ('Gallery', 'Gallery'), ('Logo', 'Logo')], attrs={
                'class': 'w-full rounded-xl border-slate-200 bg-white pl-3.5 pr-10 py-2.5 text-sm font-medium text-slate-800 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition duration-200 cursor-pointer block leading-normal'
            }),
        }