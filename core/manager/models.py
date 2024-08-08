from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField


# Create your models here.

class Package(models.Model):
	name = models.CharField(max_length = 250)
	price = models.IntegerField()
	period_days = models.IntegerField()
	is_active = models.BooleanField(default = True)

	def __str__(self):
		return self.name
	
class Tag(models.Model):
	name = models.CharField(max_length=250)

class Place(models.Model):
	name = models.CharField(max_length = 250)
	
class FashionCategory(models.Model):
	parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='scategory', null=True, blank=True)
	is_sub = models.BooleanField(default=False)
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)

	def __str__(self):
		return self.name
	
	def get_image_url(self):
		image = FashionCategory.objects.filter(category=self).first()
		image_url = image.image.url
		return image_url

class OrderStatus(models.Model):
	latest_status = models.CharField(max_length = 250)

	def __str__(self):
		return self.latest_status

def bank_upload_path(instance, filename):
	image_name = instance.alt_name.replace(" ", "_")
	filename = f"{image_name}"
	return f"picosite/{filename}"

class BankImage(models.Model):
	alt_name = models.CharField(max_length=250, null=True, blank=True)
	image = models.ImageField()
	tags = models.ManyToManyField(Tag)
	location = models.ForeignKey(Place, on_delete = models.CASCADE)

	def __str__(self):
		return f'{self.location} - {self.alt_name}'

class Subscription(models.Model):
	email=models.EmailField()

def category_upload_path(instance, filename):
	category_name = instance.alt_name.replace(" ", "_")
	filename = f"manager/category/{category_name}_{filename}"
	return f"{filename}"

class FashionCategoryImage(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	image = models.ImageField(upload_to=category_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)
	category = models.ForeignKey(FashionCategory, on_delete=models.CASCADE)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.alt_name:
			self.custom_name = f"{self.category.name}"
		super().save(*args, **kwargs)

def slide_upload_path(instance, filename):
	slide_name = instance.alt_name.replace(" ", "_")
	timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
	filename = f"{slide_name}_{filename}"
	return f"manager/default_slides/{instance.index}/{filename}"

class FashionSlide(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	index = models.PositiveIntegerField(default=1)
	image = models.ImageField(upload_to=slide_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.custom_name:
			timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
			self.custom_name = f"{self.alt_name}_{timestamp}"
		super().save(*args, **kwargs)

def banner_upload_path(instance, filename):
	banner_name = instance.alt_name.replace(" ", "_")
	timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
	filename = f"{banner_name}_{filename}"
	return f"manager/default_banners/{instance.index}/{filename}"

class FashionBanner(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	index = models.PositiveIntegerField(default=1)
	image = models.ImageField(upload_to=banner_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.custom_name:
			timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
			self.custom_name = f"{self.alt_name}_{timestamp}"
		super().save(*args, **kwargs)

class FashionProduct(models.Model):
	category = models.ManyToManyField(FashionCategory, blank= True, related_name='products')
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)
	description = RichTextField(default = "insert the product's description")
	price = models.IntegerField()
	sales_price = models.IntegerField(null=True, blank=True)
	available = models.BooleanField(default=True)
	off_active = models.BooleanField(default=False)
	tags = models.ManyToManyField(Tag, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('name',)

	def get_main_image(self):
		images = FashionProductImage.objects.filter(product=self)
		main_image = images.first()
		if main_image == None:
			main_image_url = 'https://marketplace-bucket.storage.iran.liara.space/shop/default-product-image.png'
		else:
			main_image_url = main_image.image.url
		return main_image_url

	def get_gallery(self):
		images = FashionProductImage.objects.filter(product=self)
		main_image = images.first()
		gallery_images = images.exclude(pk=main_image.pk)
		return gallery_images

	def __str__(self):
		return f'manager demo product: {self.name}'
	
def image_upload_path(instance, filename):
	product_name = instance.product.name.replace(" ", "_")
	timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
	filename = f"{product_name}"
	return f"manager/demo_products/{filename}"

class FashionProductImage(models.Model):
	alt_name = models.CharField(max_length=250, null=True, blank=True)
	product = models.ForeignKey(FashionProduct, on_delete=models.CASCADE)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	image = models.ImageField(upload_to=image_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.custom_name:
			product_name = self.product.name.replace(" ", "_")
			timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
			self.custom_name = f"{product_name}_{timestamp}"
		super().save(*args, **kwargs)

class PerfumeCategory(models.Model):
	parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='scategory', null=True, blank=True)
	is_sub = models.BooleanField(default=False)
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)

	def __str__(self):
		return self.name
	
	def get_image_url(self):
		image = PerfumeCategory.objects.filter(category=self).first()
		image_url = image.image.url
		return image_url

class PerfumeCategoryImage(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	image = models.ImageField(upload_to=category_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)
	category = models.ForeignKey(PerfumeCategory, on_delete=models.CASCADE)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.alt_name:
			self.custom_name = f"{self.category.name}"
		super().save(*args, **kwargs)

class PerfumeProduct(models.Model):
	category = models.ManyToManyField(PerfumeCategory, blank= True, related_name='products')
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)
	description = RichTextField(default = "insert the product's description")
	price = models.IntegerField()
	sales_price = models.IntegerField(null=True, blank=True)
	available = models.BooleanField(default=True)
	off_active = models.BooleanField(default=False)
	tags = models.ManyToManyField(Tag, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('name',)

	def get_main_image(self):
		images = PerfumeProductImage.objects.filter(product=self)
		main_image = images.first()
		if main_image == None:
			main_image_url = 'https://marketplace-bucket.storage.iran.liara.space/shop/default-product-image.png'
		else:
			main_image_url = main_image.image.url
		return main_image_url

	def get_gallery(self):
		images = PerfumeProductImage.objects.filter(product=self)
		main_image = images.first()
		gallery_images = images.exclude(pk=main_image.pk)
		return gallery_images

	def __str__(self):
		return f'manager demo product: {self.name}'

class PerfumeProductImage(models.Model):
	alt_name = models.CharField(max_length=250, null=True, blank=True)
	product = models.ForeignKey(PerfumeProduct, on_delete=models.CASCADE)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	image = models.ImageField(upload_to=image_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.custom_name:
			product_name = self.product.name.replace(" ", "_")
			timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
			self.custom_name = f"{product_name}_{timestamp}"
		super().save(*args, **kwargs)

class PerfumeSlide(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	index = models.PositiveIntegerField(default=1)
	image = models.ImageField(upload_to=slide_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

class PerfumeBanner(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	index = models.PositiveIntegerField(default=1)
	image = models.ImageField(upload_to=banner_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.custom_name:
			timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
			self.custom_name = f"{self.alt_name}_{timestamp}"
		super().save(*args, **kwargs)

class ArtAndCultureCategory(models.Model):
	parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='scategory', null=True, blank=True)
	is_sub = models.BooleanField(default=False)
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)

	def __str__(self):
		return self.name
	
	def get_image_url(self):
		image = ArtAndCultureCategory.objects.filter(category=self).first()
		image_url = image.image.url
		return image_url

class ArtAndCultureCategoryImage(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	image = models.ImageField(upload_to=category_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)
	category = models.ForeignKey(ArtAndCultureCategory, on_delete=models.CASCADE)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.alt_name:
			self.custom_name = f"{self.category.name}"
		super().save(*args, **kwargs)

class ArtAndCultureProduct(models.Model):
	category = models.ManyToManyField(ArtAndCultureCategory, blank= True, related_name='products')
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)
	description = RichTextField(default = "insert the product's description")
	price = models.IntegerField()
	sales_price = models.IntegerField(null=True, blank=True)
	available = models.BooleanField(default=True)
	off_active = models.BooleanField(default=False)
	tags = models.ManyToManyField(Tag, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('name',)

	def get_main_image(self):
		images = ArtAndCultureProductImage.objects.filter(product=self)
		main_image = images.first()
		if main_image == None:
			main_image_url = 'https://marketplace-bucket.storage.iran.liara.space/shop/default-product-image.png'
		else:
			main_image_url = main_image.image.url
		return main_image_url

	def get_gallery(self):
		images = ArtAndCultureProductImage.objects.filter(product=self)
		main_image = images.first()
		gallery_images = images.exclude(pk=main_image.pk)
		return gallery_images

	def __str__(self):
		return f'manager demo product: {self.name}'

class ArtAndCultureProductImage(models.Model):
	alt_name = models.CharField(max_length=250, null=True, blank=True)
	product = models.ForeignKey(ArtAndCultureProduct, on_delete=models.CASCADE)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	image = models.ImageField(upload_to=image_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.custom_name:
			product_name = self.product.name.replace(" ", "_")
			timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
			self.custom_name = f"{product_name}_{timestamp}"
		super().save(*args, **kwargs)

class ArtAndCultureSlide(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	index = models.PositiveIntegerField(default=1)
	image = models.ImageField(upload_to=slide_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

class ArtAndCultureBanner(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	index = models.PositiveIntegerField(default=1)
	image = models.ImageField(upload_to=banner_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.custom_name:
			timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
			self.custom_name = f"{self.alt_name}_{timestamp}"
		super().save(*args, **kwargs)

class CosmeticCategory(models.Model):
	parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='scategory', null=True, blank=True)
	is_sub = models.BooleanField(default=False)
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)

	def __str__(self):
		return self.name
	
	def get_image_url(self):
		image = CosmeticCategory.objects.filter(category=self).first()
		image_url = image.image.url
		return image_url

class CosmeticCategoryImage(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	image = models.ImageField(upload_to=category_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)
	category = models.ForeignKey(CosmeticCategory, on_delete=models.CASCADE)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.alt_name:
			self.custom_name = f"{self.category.name}"
		super().save(*args, **kwargs)

class CosmeticProduct(models.Model):
	category = models.ManyToManyField(CosmeticCategory, blank= True, related_name='products')
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)
	description = RichTextField(default = "insert the product's description")
	price = models.IntegerField()
	sales_price = models.IntegerField(null=True, blank=True)
	available = models.BooleanField(default=True)
	off_active = models.BooleanField(default=False)
	tags = models.ManyToManyField(Tag, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('name',)

	def get_main_image(self):
		images = CosmeticProductImage.objects.filter(product=self)
		main_image = images.first()
		if main_image == None:
			main_image_url = 'https://marketplace-bucket.storage.iran.liara.space/shop/default-product-image.png'
		else:
			main_image_url = main_image.image.url
		return main_image_url

	def get_gallery(self):
		images = CosmeticProductImage.objects.filter(product=self)
		main_image = images.first()
		gallery_images = images.exclude(pk=main_image.pk)
		return gallery_images

	def __str__(self):
		return f'manager demo product: {self.name}'

class CosmeticProductImage(models.Model):
	alt_name = models.CharField(max_length=250, null=True, blank=True)
	product = models.ForeignKey(CosmeticProduct, on_delete=models.CASCADE)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	image = models.ImageField(upload_to=image_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.custom_name:
			product_name = self.product.name.replace(" ", "_")
			timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
			self.custom_name = f"{product_name}_{timestamp}"
		super().save(*args, **kwargs)

class CosmeticSlide(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	index = models.PositiveIntegerField(default=1)
	image = models.ImageField(upload_to=slide_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

class CosmeticBanner(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	index = models.PositiveIntegerField(default=1)
	image = models.ImageField(upload_to=banner_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.custom_name:
			timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
			self.custom_name = f"{self.alt_name}_{timestamp}"
		super().save(*args, **kwargs)

class GiftAndCelebrationCategory(models.Model):
	parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='scategory', null=True, blank=True)
	is_sub = models.BooleanField(default=False)
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)

	def __str__(self):
		return self.name
	
	def get_image_url(self):
		image = GiftAndCelebrationCategory.objects.filter(category=self).first()
		image_url = image.image.url
		return image_url

class GiftAndCelebrationCategoryImage(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	image = models.ImageField(upload_to=category_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)
	category = models.ForeignKey(GiftAndCelebrationCategory, on_delete=models.CASCADE)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.alt_name:
			self.custom_name = f"{self.category.name}"
		super().save(*args, **kwargs)

class GiftAndCelebrationProduct(models.Model):
	category = models.ManyToManyField(GiftAndCelebrationCategory, blank= True, related_name='products')
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)
	description = RichTextField(default = "insert the product's description")
	price = models.IntegerField()
	sales_price = models.IntegerField(null=True, blank=True)
	available = models.BooleanField(default=True)
	off_active = models.BooleanField(default=False)
	tags = models.ManyToManyField(Tag, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('name',)

	def get_main_image(self):
		images = GiftAndCelebrationProductImage.objects.filter(product=self)
		main_image = images.first()
		if main_image == None:
			main_image_url = 'https://marketplace-bucket.storage.iran.liara.space/shop/default-product-image.png'
		else:
			main_image_url = main_image.image.url
		return main_image_url

	def get_gallery(self):
		images = GiftAndCelebrationProductImage.objects.filter(product=self)
		main_image = images.first()
		gallery_images = images.exclude(pk=main_image.pk)
		return gallery_images

	def __str__(self):
		return f'manager demo product: {self.name}'

class GiftAndCelebrationProductImage(models.Model):
	alt_name = models.CharField(max_length=250, null=True, blank=True)
	product = models.ForeignKey(GiftAndCelebrationProduct, on_delete=models.CASCADE)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	image = models.ImageField(upload_to=image_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.custom_name:
			product_name = self.product.name.replace(" ", "_")
			timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
			self.custom_name = f"{product_name}_{timestamp}"
		super().save(*args, **kwargs)

class GiftAndCelebrationSlide(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	index = models.PositiveIntegerField(default=1)
	image = models.ImageField(upload_to=slide_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

class GiftAndCelebrationBanner(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	index = models.PositiveIntegerField(default=1)
	image = models.ImageField(upload_to=banner_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.custom_name:
			timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
			self.custom_name = f"{self.alt_name}_{timestamp}"
		super().save(*args, **kwargs)

class ToysAndKidsCategory(models.Model):
	parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='scategory', null=True, blank=True)
	is_sub = models.BooleanField(default=False)
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)

	def __str__(self):
		return self.name
	
	def get_image_url(self):
		image = ToysAndKidsCategory.objects.filter(category=self).first()
		image_url = image.image.url
		return image_url

class ToysAndKidsCategoryImage(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	image = models.ImageField(upload_to=category_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)
	category = models.ForeignKey(ToysAndKidsCategory, on_delete=models.CASCADE)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.alt_name:
			self.custom_name = f"{self.category.name}"
		super().save(*args, **kwargs)

class ToysAndKidsProduct(models.Model):
	category = models.ManyToManyField(ToysAndKidsCategory, blank= True, related_name='products')
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)
	description = RichTextField(default = "insert the product's description")
	price = models.IntegerField()
	sales_price = models.IntegerField(null=True, blank=True)
	available = models.BooleanField(default=True)
	off_active = models.BooleanField(default=False)
	tags = models.ManyToManyField(Tag, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('name',)

	def get_main_image(self):
		images = ToysAndKidsProductImage.objects.filter(product=self)
		main_image = images.first()
		if main_image == None:
			main_image_url = 'https://marketplace-bucket.storage.iran.liara.space/shop/default-product-image.png'
		else:
			main_image_url = main_image.image.url
		return main_image_url

	def get_gallery(self):
		images = ToysAndKidsProductImage.objects.filter(product=self)
		main_image = images.first()
		gallery_images = images.exclude(pk=main_image.pk)
		return gallery_images

	def __str__(self):
		return f'manager demo product: {self.name}'

class ToysAndKidsProductImage(models.Model):
	alt_name = models.CharField(max_length=250, null=True, blank=True)
	product = models.ForeignKey(ToysAndKidsProduct, on_delete=models.CASCADE)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	image = models.ImageField(upload_to=image_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.custom_name:
			product_name = self.product.name.replace(" ", "_")
			timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
			self.custom_name = f"{product_name}_{timestamp}"
		super().save(*args, **kwargs)

class ToysAndKidsSlide(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	index = models.PositiveIntegerField(default=1)
	image = models.ImageField(upload_to=slide_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

class ToysAndKidsBanner(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	index = models.PositiveIntegerField(default=1)
	image = models.ImageField(upload_to=banner_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.custom_name:
			timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
			self.custom_name = f"{self.alt_name}_{timestamp}"
		super().save(*args, **kwargs)

class GeneralCategory(models.Model):
	parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='scategory', null=True, blank=True)
	is_sub = models.BooleanField(default=False)
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)

	def __str__(self):
		return self.name
	
	def get_image_url(self):
		image = GeneralCategory.objects.filter(category=self).first()
		image_url = image.image.url
		return image_url

class GeneralCategoryImage(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	image = models.ImageField(upload_to=category_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)
	category = models.ForeignKey(GeneralCategory, on_delete=models.CASCADE)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.alt_name:
			self.custom_name = f"{self.category.name}"
		super().save(*args, **kwargs)

class GeneralProduct(models.Model):
	category = models.ManyToManyField(GeneralCategory, blank= True, related_name='products')
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)
	description = RichTextField(default = "insert the product's description")
	price = models.IntegerField()
	sales_price = models.IntegerField(null=True, blank=True)
	available = models.BooleanField(default=True)
	off_active = models.BooleanField(default=False)
	tags = models.ManyToManyField(Tag, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('name',)

	def get_main_image(self):
		images = GeneralProductImage.objects.filter(product=self)
		main_image = images.first()
		if main_image == None:
			main_image_url = 'https://marketplace-bucket.storage.iran.liara.space/shop/default-product-image.png'
		else:
			main_image_url = main_image.image.url
		return main_image_url

	def get_gallery(self):
		images = GeneralProductImage.objects.filter(product=self)
		main_image = images.first()
		gallery_images = images.exclude(pk=main_image.pk)
		return gallery_images

	def __str__(self):
		return f'manager demo product: {self.name}'

class GeneralProductImage(models.Model):
	alt_name = models.CharField(max_length=250, null=True, blank=True)
	product = models.ForeignKey(GeneralProduct, on_delete=models.CASCADE)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	image = models.ImageField(upload_to=image_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.custom_name:
			product_name = self.product.name.replace(" ", "_")
			timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
			self.custom_name = f"{product_name}_{timestamp}"
		super().save(*args, **kwargs)

class GeneralSlide(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	index = models.PositiveIntegerField(default=1)
	image = models.ImageField(upload_to=slide_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

class GeneralBanner(models.Model):

	alt_name = models.CharField(max_length=250, null=True, blank=True)
	custom_name = models.CharField(max_length=250, blank=True, null=True)
	index = models.PositiveIntegerField(default=1)
	image = models.ImageField(upload_to=banner_upload_path, default='media/11.png')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created',)

	def save(self, *args, **kwargs):
		if not self.custom_name:
			timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
			self.custom_name = f"{self.alt_name}_{timestamp}"
		super().save(*args, **kwargs)

class ContactMessage(models.Model):
	name = models.CharField(max_length=250)
	familly_name = models.CharField(max_length=250)
	email = models.EmailField()
	phone = models.CharField(max_length=11)
	subject = models.CharField(max_length=250)
	message = RichTextField(default = "پیام خود را وارد نمایید.")
	created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
	is_answered = models.BooleanField(default = False)

	class Meta:
		ordering = ('created',)

	def __str__(self):
		return f'{self.name} - {self.familly_name} - {self.subject}'





