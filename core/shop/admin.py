from django.contrib import admin
from.models import ProductRefClass, Announcement,Domain, Ticket, TicketReply, Brand, Customer, Services, Subscription, FeaturedCategories, CategoryImage, UploadedImages, BlogPost, BlogCategory, WithdrawRecord, Comment, Faq, Banner, Slide, StoreLogoImage, ContactMessage, OtpCode, Store, Owner, Delivery, Category, Variety, Product, Cart, OrderStatus, Order, Size, PriceRange, Coupon, Tag
# Register your models here.


@admin.register(ProductRefClass)
class ProductRefClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_coef')

class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'created')
    search_fields = ('phone_number',)

admin.site.register(OtpCode, OtpCodeAdmin)

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_owner_name', 'phone_number', 'shamsi_created_date', 'has_domain','domain_msg', 'has_payment_gw', 'gw_msg', 'has_notif')
    fields = ('name', 'is_active', 'active_days', 'address', 'country', 'city', 
              'about_description', 'instagram', 'telegram', 'linkedin', 'merchant', 
              'independent', 'phone_number', 'balance', 'email', 'Layout_body', 'layout_sticky', 
              'layout_container', 'color', 'meta_description', 'meta_keywords', 'meta_og_title', 
              'meta_og_description', 'meta_tc_title', 'meta_tc_description', 'has_domain', 'has_payment_gw',
              'policies', 'template_index', 'index_title', 'enamad_code')

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('store', 'phone_number', 'full_name')

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('store', 'name', 'price')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('subject','is_active', 'shamsi_created_date')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('store', 'parent', 'is_sub', 'name', 'slug')
    search_fields = ['store__name','name', 'slug']
    list_filter = ('store', 'is_sub', 'parent__store')  # اضافه کردن فیلتر بر اساس فروشگاه

@admin.register(Variety)
class VarietyAdmin(admin.ModelAdmin):
    list_display = ('store', 'name', 'product', 'stock',)
    search_fields = ['name', 'product__name', 'store__name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    @admin.display(boolean=True, description='Stock Alarm')
    def stock_alarm(self, obj):
        return obj.get_stock_alarm_status()
    @admin.display(description='Active Price')
    def active_price(self, obj):
        return obj.get_active_price()
    list_display = ('name', 'price','sales_price','ref_price','off_active', 'active_price','ref_class','stock_alarm_volume','stock_alarm', 'show_varieties')
    list_editable = ('ref_class','price','ref_price','stock_alarm_volume','off_active','sales_price')
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}  # تولید اتوماتیک اسلاگ از نام

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('store', 'customer')
    filter_horizontal = ('items',) 

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('latest_status',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('store', 'customer', 'total_price', 'status', 'created_date', 'used_coupon', 'status_updated_date')
    list_filter = ('store', 'status', 'used_coupon')
    search_fields = ['store__name', 'customer__full_name', 'status__latest_status']

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(PriceRange)
class PriceRangeAdmin(admin.ModelAdmin):
    list_display = ['min_value', 'max_value']

class CouponAdmin(admin.ModelAdmin):
    list_display = ['store', 'code', 'valid_from', 'valid_to', 'discount']
    list_filter = ['store', 'valid_from', 'valid_to']
    search_fields = ['code']

admin.site.register(Coupon, CouponAdmin)


class StoreLogoImageAdmin(admin.ModelAdmin):
    list_display = ('store', 'alt_name', 'custom_name', 'created')
    search_fields = ('store__name', 'alt_name', 'custom_name')
    list_filter = ('store', 'created')
    date_hierarchy = 'created'

admin.site.register(StoreLogoImage, StoreLogoImageAdmin)


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'familly_name', 'email', 'phone', 'subject', 'created')
    search_fields = ('name', 'familly_name', 'email', 'phone', 'subject')
    list_filter = ('subject',)

admin.site.register(ContactMessage, ContactMessageAdmin)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('store', 'name', 'slug', 'is_special')
    search_fields = ['name', 'slug']
    list_filter = ('store',)

@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ('store', 'index','alt_name', 'custom_name', 'image', 'created')
    search_fields = ['alt_name', 'custom_name']

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('store', 'alt_name', 'custom_name', 'index', 'created', 'source')
    search_fields = ['alt_name', 'custom_name', 'source']

@admin.register(Faq)
class FaqModelAdmin(admin.ModelAdmin):
    list_display = ('store', 'question', 'answer')
    search_fields = ['question', 'answer']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('store', 'sender', 'email', 'product', 'approved', 'created_date')
    search_fields = ['sender', 'email', 'product__name', 'created_date']
    list_filter = ('store', 'approved')

@admin.register(WithdrawRecord)
class WithdrawRecordAdmin(admin.ModelAdmin):
    list_display = ('store', 'sheba', 'amount', 'shamsi_created_date', 'is_paid')
    search_fields = ['store__name', 'sheba', 'amount', 'created_date']
    list_filter = ('store', 'is_paid')

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('store', 'name')
    search_fields = ['store__name', 'name']

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('store', 'title', 'category', 'created_date')
    search_fields = ['store__name', 'title', 'category__name', 'created_date']
    list_filter = ('store', 'category')

@admin.register(UploadedImages)
class UploadedImagesAdmin(admin.ModelAdmin):
    list_display = ('store', 'alt_name', 'image')
    search_fields = ['store__name', 'alt_name']

class CategoryImageAdmin(admin.ModelAdmin):
    list_display = ('store', 'category', 'alt_name', 'created')
    search_fields = ('store__name', 'category__name', 'alt_name')
    list_filter = ('store', 'category', 'created')
    date_hierarchy = 'created'

admin.site.register(CategoryImage, CategoryImageAdmin)

class FeaturedCategoriesAdmin(admin.ModelAdmin):
    list_display = ('store', 'display_categories')

    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])

    display_categories.short_description = 'Categories'

admin.site.register(FeaturedCategories, FeaturedCategoriesAdmin)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('store', 'email')

@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('store', 'delivery', 'originality', 'payments')

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'email', 'full_name', 'store', 'is_active', 'is_verified', 'city', 'zip_code', 'created_date', 'updated_date')
    search_fields = ['store__name', 'phone_number', 'full_name']

admin.site.register(Customer, CustomerAdmin)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('store', 'name')
    search_fields = ['store__name', 'name']

class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 0

class TicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'store', 'is_answered', 'is_closed', 'shamsi_created_date')
    inlines = [TicketReplyInline]

admin.site.register(Ticket, TicketAdmin)

class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'is_active', 'shamsi_created_date')  # Add 'shamsi_created_date' to the list_display

admin.site.register(Domain, DomainAdmin)














