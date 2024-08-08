from django.shortcuts import render, redirect
from django.views import View
from shop.models import BlogCategory, BlogPost, ContactMessage, Store
from manager.models import Subscription
from manager.forms import SubscriptionForm
from shop.forms import ContactUsForm
from django.http import HttpResponsePermanentRedirect
from shop.models import Domain

domains_list = ['elenorstyle.ir', 'test_domain_2']

# def domain_redirect(request):
#     domain = request.META['HTTP_HOST']
#     if domain == 'elenorstyle.ir':
#         return HttpResponsePermanentRedirect('https://elenorstyle.ir/shop/elenorstyle/')
#     elif domain == 'picosite.ir':
#         return HttpResponsePermanentRedirect('https://picosite.ir/home')





class IndexView(View):

	template_name = 'index.html'

	def get(self, request):	
		domain = request.META['HTTP_HOST']
		if domain == 'viracoders.ir':
			if request.path == '/':
				return redirect('viracoders:index')
		store = Store.objects.get(name = 'myshop')
		if domain in domains_list:
			selected_domain = Domain.objects.get(domain = domain)
			store_name = selected_domain.store.name
			if request.path == '/':
				return redirect('shop:index', store_name)
		posts = BlogPost.objects.filter(store = store)
		return render(request, self.template_name, {'posts':posts})
	
class DemoRedirectView(View):

	def get(self, request):
		return redirect('viracoders:demos')

class ProductListView(View):
		
	def get(self, request):

		domain = request.META['HTTP_HOST']
		if domain in domains_list:
			selected_domain = Domain.objects.get(domain = domain)
			store_name = selected_domain.store.name
			if request.path == '/products/':
				return redirect('shop:product_list', store_name)

class ProductDetailView(View):

	def get(self, request, product_slug, *args, **kwargs):
		domain = request.META['HTTP_HOST']
		if domain in domains_list:
			selected_domain = Domain.objects.get(domain = domain)
			store_name = selected_domain.store.name
			if request.path == f'/products/{product_slug}/':
				return redirect('shop:product_detail', store_name, product_slug)

class BlogView(View):

	template_name = 'blog.html'

	def get(self, request, *args, **kwargs):
		domain = request.META['HTTP_HOST']
		if domain == 'viracoders.ir':
			if request.path == '/blog/':
				return redirect('viracoders:blog')
		store = Store.objects.get(name='myshop')
		if domain in domains_list:
			selected_domain = Domain.objects.get(domain = domain)
			store_name = selected_domain.store.name
			if request.path == '/blog/':
				return redirect('shop:post_list', store_name)
		posts = BlogPost.objects.filter(store=store)
		return render(request, self.template_name, {
											  'posts':posts,
											  })
	
class BlogPostDetailView(View):

	template_name = 'blog-detail.html'

	def get(self, request, post_slug, *args, **kwargs):
		domain = request.META['HTTP_HOST']
		if domain == 'viracoders.ir':
			_, post_slug = request.path.split('/blog/', 1)
			if request.path == f'/blog/{post_slug}':
				return redirect('viracoders:post_detail', post_slug[:-1])
		if domain in domains_list:
			selected_domain = Domain.objects.get(domain = domain)
			store_name = selected_domain.store.name
			_, post_slug = request.path.split('/blog/', 1)
			if request.path == f'/blog/{post_slug}':
				return redirect('shop:post_detail', store_name, post_slug[:-1])
		
		post = BlogPost.objects.get(slug=post_slug)
		posts = BlogPost.objects.all()
		return render(request, self.template_name, {
											  'post':post,
											  'posts':posts,})

class ContactView(View):
	
	template_name = 'contact.html'

	def get(self, request):

		domain = request.META['HTTP_HOST']
		if domain in domains_list:
			selected_domain = Domain.objects.get(domain = domain)
			store_name = selected_domain.store.name
			if request.path == '/contact/':
				return redirect('shop:contact', store_name)
		return render(request, self.template_name)
class TemplatesView(View):
	
	template_name = 'demos.html'

	def get(self, request):

		domain = request.META['HTTP_HOST']
		if domain in domains_list:
			selected_domain = Domain.objects.get(domain = domain)
			store_name = selected_domain.store.name
			if request.path == '/demos/':
				return redirect('shop:demos', store_name)
		return render(request, self.template_name)

class AboutView(View):
	
	template_name = 'about.html'

	def get(self, request):
		domain = request.META['HTTP_HOST']
		if domain in domains_list:
			selected_domain = Domain.objects.get(domain = domain)
			store_name = selected_domain.store.name
			if request.path == '/about/':
				return redirect('shop:about', store_name)
		return render(request, self.template_name)

class PoliciesView(View):
	
	template_name = 'policies.html'

	def get(self, request):
		domain = request.META['HTTP_HOST']
		if domain == 'viracoders':
			if request.path == '/policies/':
				return redirect('viracoders:policies')
		
		return render(request, self.template_name)

class FaqView(View):
	
	template_name = 'faq.html'
	
	def get(self, request):

		domain = request.META['HTTP_HOST']
		if domain == 'viracoders':
			if request.path == '/faq/':
				return redirect('viracoders:faq')

		domain = request.META['HTTP_HOST']
		if domain in domains_list:
			selected_domain = Domain.objects.get(domain = domain)
			store_name = selected_domain.store.name
			if request.path == '/faq/':
				return redirect('shop:faq_list', store_name)
		return render(request, self.template_name)

class SubscribeView(View):

	def post(self, request, *args, **kwargs):
		form = SubscriptionForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			new_subscriber, create = Subscription.objects.get_or_create(email=email)
			print(request.path)
			return redirect('index')