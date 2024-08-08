from django.contrib import admin
from .models import ContactMessage, PerfumeSlide, PerfumeBanner, ArtAndCultureSlide, ArtAndCultureBanner, CosmeticSlide, CosmeticBanner, GeneralSlide, GeneralBanner, ToysAndKidsSlide, ToysAndKidsBanner ,FashionProductImage, FashionProduct, FashionBanner, FashionSlide, FashionCategoryImage, Package, GeneralCategory, ToysAndKidsCategory, PerfumeCategory,GiftAndCelebrationCategory,  CosmeticCategory, ArtAndCultureCategory,  FashionCategory, OrderStatus, BankImage, Tag, Place, BankImage, Subscription


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'period_days', 'is_active')
    list_filter = ('is_active',)

@admin.register(FashionCategory)
class FashionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_sub', 'slug')
    list_filter = ('is_sub',)
    search_fields = ('name',)

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('latest_status',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name',]

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name']

@admin.register(BankImage)
class BankImageAdmin(admin.ModelAdmin):
    list_display = ('location', 'alt_name', 'image')
    search_fields = ['location__name', 'alt_name']
    filter_horizontal = ('tags',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email',)

class FashionCategoryImageAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'created', 'category')

admin.site.register(FashionCategoryImage, FashionCategoryImageAdmin)

class FashionSlideAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'custom_name', 'index', 'created')
    readonly_fields = ('custom_name',)  # در صورتی که custom_name را می‌خواهید در پنل ادمین نمایش دهید

admin.site.register(FashionSlide, FashionSlideAdmin)

class FashionBannerAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'custom_name', 'index', 'created')
    readonly_fields = ('custom_name',)  # در صورتی که custom_name را می‌خواهید در پنل ادمین نمایش دهید

admin.site.register(FashionBanner, FashionBannerAdmin)


@admin.register(FashionProduct)
class FashionProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'available', 'off_active']
    list_filter = ['category', 'tags', 'available', 'off_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(FashionProductImage)
class FashionProductImageAdmin(admin.ModelAdmin):
    list_display = ['alt_name', 'product', 'custom_name', 'created']
    search_fields = ['alt_name', 'custom_name']
    list_filter = ['product']




from .models import PerfumeCategory, PerfumeCategoryImage, PerfumeProduct, PerfumeProductImage

@admin.register(PerfumeCategory)
class PerfumeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_sub', 'slug')
    list_filter = ('is_sub',)
    search_fields = ('name',)

class PerfumeCategoryImageAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'created', 'category')

admin.site.register(PerfumeCategoryImage, PerfumeCategoryImageAdmin)

@admin.register(PerfumeProduct)
class PerfumeProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'available', 'off_active']
    list_filter = ['category', 'tags', 'available', 'off_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(PerfumeProductImage)
class PerfumeProductImageAdmin(admin.ModelAdmin):
    list_display = ['alt_name', 'product', 'custom_name', 'created']
    search_fields = ['alt_name', 'custom_name']
    list_filter = ['product']



from .models import ArtAndCultureCategory, ArtAndCultureCategoryImage, ArtAndCultureProduct, ArtAndCultureProductImage

@admin.register(ArtAndCultureCategory)
class ArtAndCultureCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_sub', 'slug')
    list_filter = ('is_sub',)
    search_fields = ('name',)

class ArtAndCultureCategoryImageAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'created', 'category')

admin.site.register(ArtAndCultureCategoryImage, ArtAndCultureCategoryImageAdmin)

@admin.register(ArtAndCultureProduct)
class ArtAndCultureProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'available', 'off_active']
    list_filter = ['category', 'tags', 'available', 'off_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ArtAndCultureProductImage)
class ArtAndCultureProductImageAdmin(admin.ModelAdmin):
    list_display = ['alt_name', 'product', 'custom_name', 'created']
    search_fields = ['alt_name', 'custom_name']
    list_filter = ['product']





from .models import CosmeticCategory, CosmeticCategoryImage, CosmeticProduct, CosmeticProductImage

@admin.register(CosmeticCategory)
class CosmeticCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_sub', 'slug')
    list_filter = ('is_sub',)
    search_fields = ('name',)

class CosmeticCategoryImageAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'created', 'category')

admin.site.register(CosmeticCategoryImage, CosmeticCategoryImageAdmin)

@admin.register(CosmeticProduct)
class CosmeticProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'available', 'off_active']
    list_filter = ['category', 'tags', 'available', 'off_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(CosmeticProductImage)
class CosmeticProductImageAdmin(admin.ModelAdmin):
    list_display = ['alt_name', 'product', 'custom_name', 'created']
    search_fields = ['alt_name', 'custom_name']
    list_filter = ['product']





from .models import GiftAndCelebrationCategory, GiftAndCelebrationCategoryImage, GiftAndCelebrationProduct, GiftAndCelebrationProductImage

@admin.register(GiftAndCelebrationCategory)
class GiftAndCelebrationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_sub', 'slug')
    list_filter = ('is_sub',)
    search_fields = ('name',)

class GiftAndCelebrationCategoryImageAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'created', 'category')

admin.site.register(GiftAndCelebrationCategoryImage, GiftAndCelebrationCategoryImageAdmin)

@admin.register(GiftAndCelebrationProduct)
class GiftAndCelebrationProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'available', 'off_active']
    list_filter = ['category', 'tags', 'available', 'off_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(GiftAndCelebrationProductImage)
class GiftAndCelebrationProductImageAdmin(admin.ModelAdmin):
    list_display = ['alt_name', 'product', 'custom_name', 'created']
    search_fields = ['alt_name', 'custom_name']
    list_filter = ['product']




from .models import ToysAndKidsCategory, ToysAndKidsCategoryImage, ToysAndKidsProduct, ToysAndKidsProductImage

@admin.register(ToysAndKidsCategory)
class ToysAndKidsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_sub', 'slug')
    list_filter = ('is_sub',)
    search_fields = ('name',)

class ToysAndKidsCategoryImageAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'created', 'category')

admin.site.register(ToysAndKidsCategoryImage, ToysAndKidsCategoryImageAdmin)

@admin.register(ToysAndKidsProduct)
class ToysAndKidsProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'available', 'off_active']
    list_filter = ['category', 'tags', 'available', 'off_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ToysAndKidsProductImage)
class ToysAndKidsProductImageAdmin(admin.ModelAdmin):
    list_display = ['alt_name', 'product', 'custom_name', 'created']
    search_fields = ['alt_name', 'custom_name']
    list_filter = ['product']





from .models import GeneralCategory, GeneralCategoryImage, GeneralProduct, GeneralProductImage

@admin.register(GeneralCategory)
class GeneralCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_sub', 'slug')
    list_filter = ('is_sub',)
    search_fields = ('name',)

class GeneralCategoryImageAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'created', 'category')

admin.site.register(GeneralCategoryImage, GeneralCategoryImageAdmin)

@admin.register(GeneralProduct)
class GeneralProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'available', 'off_active']
    list_filter = ['category', 'tags', 'available', 'off_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(GeneralProductImage)
class GeneralProductImageAdmin(admin.ModelAdmin):
    list_display = ['alt_name', 'product', 'custom_name', 'created']
    search_fields = ['alt_name', 'custom_name']
    list_filter = ['product']


class PerfumeSlideAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'custom_name', 'index', 'created')
    readonly_fields = ('custom_name',)  # در صورتی که custom_name را می‌خواهید در پنل ادمین نمایش دهید

admin.site.register(PerfumeSlide, PerfumeSlideAdmin)

class PerfumeBannerAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'custom_name', 'index', 'created')
    readonly_fields = ('custom_name',)  # در صورتی که custom_name را می‌خواهید در پنل ادمین نمایش دهید

admin.site.register(PerfumeBanner, PerfumeBannerAdmin)

class CosmeticSlideAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'custom_name', 'index', 'created')
    readonly_fields = ('custom_name',)  # در صورتی که custom_name را می‌خواهید در پنل ادمین نمایش دهید

admin.site.register(CosmeticSlide, CosmeticSlideAdmin)

class CosmeticBannerAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'custom_name', 'index', 'created')
    readonly_fields = ('custom_name',)  # در صورتی که custom_name را می‌خواهید در پنل ادمین نمایش دهید

admin.site.register(CosmeticBanner, CosmeticBannerAdmin)

class ArtAndCultureSlideAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'custom_name', 'index', 'created')
    readonly_fields = ('custom_name',)  # در صورتی که custom_name را می‌خواهید در پنل ادمین نمایش دهید

admin.site.register(ArtAndCultureSlide, ArtAndCultureSlideAdmin)

class ArtAndCultureBannerAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'custom_name', 'index', 'created')
    readonly_fields = ('custom_name',)  # در صورتی که custom_name را می‌خواهید در پنل ادمین نمایش دهید

admin.site.register(ArtAndCultureBanner, ArtAndCultureBannerAdmin)

class GeneralSlideAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'custom_name', 'index', 'created')
    readonly_fields = ('custom_name',)  # در صورتی که custom_name را می‌خواهید در پنل ادمین نمایش دهید

admin.site.register(GeneralSlide, GeneralSlideAdmin)

class GeneralBannerAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'custom_name', 'index', 'created')
    readonly_fields = ('custom_name',)  # در صورتی که custom_name را می‌خواهید در پنل ادمین نمایش دهید

admin.site.register(GeneralBanner, GeneralBannerAdmin)

class ToysAndKidsSlideAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'custom_name', 'index', 'created')
    readonly_fields = ('custom_name',)  # در صورتی که custom_name را می‌خواهید در پنل ادمین نمایش دهید

admin.site.register(ToysAndKidsSlide, ToysAndKidsSlideAdmin)

class ToysAndKidsBannerAdmin(admin.ModelAdmin):
    list_display = ('alt_name', 'custom_name', 'index', 'created')
    readonly_fields = ('custom_name',)  # در صورتی که custom_name را می‌خواهید در پنل ادمین نمایش دهید

admin.site.register(ToysAndKidsBanner, ToysAndKidsBannerAdmin)

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'familly_name', 'email', 'phone', 'subject', 'created')
    search_fields = ('name', 'familly_name', 'email', 'phone', 'subject')
    list_filter = ('subject',)

admin.site.register(ContactMessage, ContactMessageAdmin)
