from django.shortcuts import render, redirect, get_object_or_404
from random import randint
from django.core.files.base import ContentFile
from django import forms
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime
import re, os
import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from .utils import IsOwnerUserMixin, IsCustomerUserMixin
from django.http import HttpResponse
from django.views.generic import  DeleteView
from .forms import *
from django.views import View
from shop.models import *
import random
from accounts.models import User
from utils import send_otp_code
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib import messages
from django.apps import apps
from datetime import datetime
from khayyam import JalaliDatetime
from django.db.models import Q
from googletrans import Translator
import re



MERCHANT = Store.objects.all().first().merchant
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"
# CallbackURL = 'http://127.0.0.1:8000/shop//orders/verify/'

store_name = Store.objects.all().first().name
current_app_name = apps.get_containing_app_config(__name__).name


class IndexView(View):

	def get(self, request):
		current_page = request.path
		store = Store.objects.get(name=store_name)
		slides = Slide.objects.filter(store=store)
		small_banners = Banner.objects.filter(store=store, size='small')
		big_banners = Banner.objects.filter(store=store, size='big')
		posts = BlogPost.objects.filter(store=store)
		services = Services.objects.get(store=store)
		products = Product.objects.filter(store=store)
		to_products = f'{current_app_name}:product_detail'
		featured_categories = FeaturedCategories.objects.filter(store = store).first()
		return render(request, f'{current_app_name}/index_{store.template_index}.html', {'services':services,'posts':posts,'featured_categories':featured_categories,'to_products':to_products ,'products':products ,'store_name':store_name, 'slides':slides, 'small_banners':small_banners, 'big_banners':big_banners})

class OwnerView(View):

	form_class = OwnerForm
	template_name = 'shop/owner.html'

	def get(self, request):
		form = self.form_class()
		return render(request, self.template_name, {'form':form})

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		store = Store.objects.get(name=store_name)
		if form.is_valid():
			phone_number = form.cleaned_data['phone_number']
			if len(phone_number) != 11:
				return render(request, self.template_name, {'message':'شماره تماس صحیح نیست'})

			# 2. بررسی شروع با '09'
			if not phone_number.startswith('09'):
				return render(request, self.template_name, {'message':'شماره تماس صحیح نیست'})
			full_name = form.cleaned_data['full_name']
			owner = Owner.objects.filter(phone_number=phone_number, store=store).first()
			if owner != None:
				previous_codes = OtpCode.objects.filter(phone_number = phone_number)
				previous_codes.delete()
				random_code = random.randint(100000,999999)
				send_otp_code(phone_number,random_code)
				new_otp = OtpCode.objects.create(phone_number = phone_number, code = random_code) 
				return redirect('shop:verify-owner', phone_number)
			
			owner = Owner.objects.create(phone_number = phone_number, store=store, full_name=full_name)
			user, create = User.objects.get_or_create(phone_number = phone_number)
			user.full_name= full_name
			user.save()
			previous_codes = OtpCode.objects.filter(phone_number = phone_number)
			previous_codes.delete()
			random_code = random.randint(100000,999999)
			send_otp_code(phone_number,random_code)
			new_otp = OtpCode.objects.create(phone_number = phone_number, code = random_code) 
			return redirect('shop:verify-owner', phone_number=phone_number)
		message = 'ورودی نا معتبر'
		return render(request, self.template_name, {'message':message, 'form':form})

class VerifyOwnerView(View):
	form_class = VerifyOwnerForm
	template_name = f'{current_app_name}/verify_owner.html'

	def get(self, request, phone_number):
		form = self.form_class()
		return render(request, self.template_name, {'form':form})
	
	def post(self, request, phone_number, *args, **kwargs):
		form = AuthenticationCodeForm(request.POST)
		if form.is_valid():
			owner_phone = phone_number
			store = Store.objects.filter(name = store_name).first()
			owner = Owner.objects.filter(phone_number = owner_phone, store = store).first()
			user = User.objects.filter(phone_number = owner_phone).first()
			customer = Customer.objects.get_or_create(phone_number=phone_number, store = store)
			request.user = user
			last_sent_otp = OtpCode.objects.filter(phone_number = owner_phone).first()
			recieved_code = form.cleaned_data['code']
			if last_sent_otp.code == recieved_code:
				user.is_shopowner = True
				owner.save()
				user.save()
				login(request, user)
				if user.is_verified == True:
					return redirect(f'{current_app_name}:owner_dashboard')
				return redirect(f'{current_app_name}:owner_dashboard_tutorials')
			return render(request, self.template_name, {'form':form, 'message':'کد تایید اشتباه است.'})
		return render(request, self.template_name, {'form':form, 'message':'ورودی نامعتبر'})

class OwnerDashboardView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/owner-dashboard.html'

	def get(self, request):
		store = Store.objects.get(name=store_name)
		delivered_status = OrderStatus.objects.get(id=3)
		delivered_orders = Order.objects.filter(store=store, status=delivered_status)
		number_of_delivered_orders = delivered_orders.count()
		total_earn = 0
		for delivered_order in delivered_orders:
			total_earn = total_earn + delivered_order.total_price
		
		paid_status = OrderStatus.objects.get(id=1)
		paid_orders = Order.objects.filter(store=store, status=paid_status)
		number_of_waiting_orders = paid_orders.count()
		total_waiting_earn = 0
		for paid_order in paid_orders:
			total_waiting_earn = total_waiting_earn + paid_order.total_price

		customers = Customer.objects.filter(store=store)
		customers_number = customers.count()

		return render(request, self.template_name, {
													'store_name':store_name,
											  		'number_of_waiting_orders':number_of_waiting_orders,
											  		'number_of_paid_orders':number_of_delivered_orders,
													'total_waiting_earn':total_waiting_earn,
													'total_earn':total_earn,
													'customers_number':customers_number,
													'customers':customers,})

	def post(self, request, *args, **kwargs):
		pass

class OwnerDashboardCustomersView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/owner-dashboard-customers.html'

	def get(self, request):
		store = Store.objects.get(name=store_name)
		delivered_status = OrderStatus.objects.get(id=3)
		delivered_orders = Order.objects.filter(store=store, status=delivered_status)
		number_of_delivered_orders = delivered_orders.count()
		total_earn = 0
		for delivered_order in delivered_orders:
			total_earn = total_earn + delivered_order.total_price
		
		paid_status = OrderStatus.objects.get(id=1)
		paid_orders = Order.objects.filter(store=store, status=paid_status)
		number_of_waiting_orders = paid_orders.count()
		total_waiting_earn = 0
		for paid_order in paid_orders:
			total_waiting_earn = total_waiting_earn + paid_order.total_price

		customers = Customer.objects.filter(store=store)
		customers_number = customers.count()

		return render(request, self.template_name, {'store_name':store_name,
											  		'number_of_waiting_orders':number_of_waiting_orders,
											  		'number_of_paid_orders':number_of_delivered_orders,
													'total_waiting_earn':total_waiting_earn,
													'total_earn':total_earn,
													'customers_number':customers_number,
													'customers':customers,})

class OwnerDashboardOrdersView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/owner-dashboard-orders.html'

	def get(self, request):
		store = Store.objects.get(name=store_name)
		delivered_status = OrderStatus.objects.get(id=3)
		delivered_orders = Order.objects.filter(store=store, status=delivered_status)
		number_of_delivered_orders = delivered_orders.count()
		total_earn = 0
		for delivered_order in delivered_orders:
			total_earn = total_earn + delivered_order.total_price
		
		paid_status = OrderStatus.objects.get(id=1)
		paid_orders = Order.objects.filter(store=store, status=paid_status)
		number_of_waiting_orders = paid_orders.count()
		total_waiting_earn = 0
		for paid_order in paid_orders:
			total_waiting_earn = total_waiting_earn + paid_order.total_price

		customers = Customer.objects.filter(store=store)
		customers_number = customers.count()

		orders = Order.objects.filter(store=store)

		return render(request, self.template_name, {'store_name':store_name,
											  		'number_of_waiting_orders':number_of_waiting_orders,
											  		'number_of_paid_orders':number_of_delivered_orders,
													'total_waiting_earn':total_waiting_earn,
													'total_earn':total_earn,
													'customers_number':customers_number,
													'customers':customers,
													'orders':orders,})

class OwnerDashboardOrderDetailView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/order-detail-owner.html'
	
	def get(self, request, order_id):
		order = get_object_or_404(Order, id=order_id)
		store = Store.objects.get(name = store_name)
		return render(request, self.template_name, {'order':order, 'store_name':store_name})

class OwnerDashboardTutorialsView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/owner-dashboard-tutorials.html'
	
	def get(self, request):
		store = Store.objects.get(name = store_name)
		return render(request, self.template_name, {'store_name':store_name})

class OwnerDashboardProductsView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/owner-dashboard-products.html'

	def get(self, request):
		store = Store.objects.get(name=store_name)
		products = Product.objects.filter(store=store)
		return render(request, self.template_name, {'store_name':store_name,
											  		'products':products,
											  		})

class OwnerDashboardMessagesView(IsOwnerUserMixin, View):
	
	template_name = f'{current_app_name}/owner-dashboard-messages.html'

	def get(self, request):
		store = Store.objects.get(name = store_name)
		messages = ContactMessage.objects.filter(store = store)
		return render(request, self.template_name, {'messages':messages,'store':store,'store_name':store_name})
	
class AnswerMessageView(IsOwnerUserMixin, View):

	def get(self, request, message_id, status_id, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		message = ContactMessage.objects.get(id=message_id)
		if status_id == 1:
			message.is_answered = True
			message.save()
		else:
			message.is_answered = False
			message.save()
		
		return redirect(f'{current_app_name}:owner_dashboard_messages')

class OwnerLoginView(View):
	form_class = OwnerLoginForm
	template_name = f'{current_app_name}/owner-login.html'

	def get(self, request):
		form = self.form_class()
		return render(request, self.template_name, {'form':form})

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		if form.is_valid():
			phone_number = form.cleaned_data['phone_number']
			store = Store.objects.get(name = store_name)
			owner = Owner.objects.filter(phone_number=phone_number, store=store).first()
			if owner != None:
				previous_codes = OtpCode.objects.filter(phone_number = phone_number)
				previous_codes.delete()
				random_code = random.randint(100000,999999)
				send_otp_code(phone_number,random_code)
				new_otp = OtpCode.objects.create(phone_number = phone_number, code = random_code) 
				return redirect(f'{current_app_name}:verify-owner', phone_number=phone_number)
			message = "The phone number doesn't match the shop owner"
			return render(request, self.template_name, {'message':message, 'form':form})
		message = 'Invalid Input'
		return render(request, self.template_name, {'message':message, 'form':form})

class StoreUpdateView(IsOwnerUserMixin, View):

	form_class = StoreForm
	template_name = f'{current_app_name}/owner-dashboard-store-settings.html'

	def get(self, request):
		store = get_object_or_404(Store, name=store_name)
		form = StoreForm
		store_update_url = f'{current_app_name}:store_update'
		return render(request, self.template_name, {'form': form, 'store': store, 'store_update':store_update_url})

	def post(self, request):
		store = Store.objects.get(name=store_name)
		form = self.form_class(request.POST)
		if form.is_valid():
			store.email = form.cleaned_data['email']
			store.country = form.cleaned_data['country']
			store.city = form.cleaned_data['city']
			store.instagram = form.cleaned_data['instagram']
			store.address = form.cleaned_data['address']
			store.about_description = form.cleaned_data['about']
			store.phone_number = form.cleaned_data['phone_number']
			store.save()
			return redirect(f'{current_app_name}:owner_dashboard_store_update')
		
class IndexTitleUpdateView(View):

	def post(self, request, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		form = IndexTitleUpdateForm(request.POST)
		if form.is_valid():
			store.index_title = form.cleaned_data['index_title']
			store.save()
			return redirect(f'{current_app_name}:index', store_name)
		store = get_object_or_404(Store, name=store_name)
		form = StoreForm
		store_update_url = f'{current_app_name}:store_update'
		
		return render(request, self.template_name, {'form': form, 'store': store, 'store_update':store_update_url, 'wrong_input_message':'اطلاعات ورودی نا معتبر'})

class EnamadUpdateView(View):

	def post(self, request, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		form = EnamadUpdateForm(request.POST)
		if form.is_valid():
			store.enamad_code = form.cleaned_data['enamad']
			store.save()
			return redirect(f'{current_app_name}:index', store_name)
		store = get_object_or_404(Store, name=store_name)
		form = StoreForm
		store_update_url = f'{current_app_name}:store_update'
		
		return render(request, self.template_name, {'form': form, 'store': store, 'store_update':store_update_url, 'wrong_input_message':'اطلاعات ورودی نا معتبر'})
		
class MetaDataView(IsOwnerUserMixin, View):

	form_class = MetaForm
	template_name = f'{current_app_name}/owner-dashboard-meta.html'

	def get(self, request):
		store = get_object_or_404(Store, name=store_name)
		form = MetaForm
		return render(request, self.template_name, {'form': form, 'store': store})

	def post(self, request):
		store = Store.objects.get(name=store_name)
		form = self.form_class(request.POST)
		if form.is_valid():
			store.meta_description = form.cleaned_data['meta_description']
			store.meta_keywords = form.cleaned_data['meta_keywords']
			store.meta_og_title = form.cleaned_data['meta_og_title']
			store.meta_og_description = form.cleaned_data['meta_og_description']
			store.meta_tc_title = form.cleaned_data['meta_tc_title']
			store.meta_tc_description = form.cleaned_data['meta_tc_description']
			store.save()
			return redirect(f'{current_app_name}:owner_dashboard_meta')

class CustomerDashboardView(View):

	def get(self, request, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		if isinstance(request.user, AnonymousUser):
			return redirect(f'{current_app_name}:customer_authentication', store_name)
		customer = Customer.objects.get(phone_number = request.user.phone_number, store=store)
		orders = Order.objects.filter(store=store, customer=customer)
		num_of_orders = orders.count()
		paid_status = OrderStatus.objects.get(id=1)
		total = 0
		for order in orders:
			if order.status == paid_status:
				total = total + order.total_price
		favorites = customer.favorites.all()
		number_of_favs = favorites.count()
		return render(request, f'{current_app_name}/customer-dashboard_{store.template_index}.html', {
			'customer':customer,
			'orders':orders,
			'num_of_orders':num_of_orders,
			'total':total,
			'store_name':store_name,
			'store':store,
			'number_of_favs':number_of_favs,
		})

class CustomerDashboardOrdersView(IsCustomerUserMixin, View):

	def get(self, request):
		store = Store.objects.get(name=store_name)
		customer = Customer.objects.get(phone_number=request.user.phone_number, store=store)		
		paid_status = OrderStatus.objects.get(id=1)
		paid_orders = Order.objects.filter(store=store, customer=customer, status=paid_status)
		number_paid_orders = paid_orders.count()
		orders = Order.objects.filter(customer = customer, store = store)

		return render(request, f'{current_app_name}/customer-dashboard-orders_{store.template_index}.html', 
				{'store_name':store_name,
				'number_of_paid_orders':number_paid_orders,
				'paid_orders':paid_orders,
				'customer':customer,
				'orders':orders})

class CustomerDashboardOrderDatailView(IsCustomerUserMixin, View):
	
	def get(self, request, order_id):
		order = get_object_or_404(Order, id=order_id)
		store = Store.objects.get(name = store_name)
		return render(request, f'{current_app_name}/order-detail-customer_{store.template_index}.html',
				 {'order':order, 'store_name':store_name})

class CustomerDashboardFavoritesView(IsCustomerUserMixin, View):

	def get(self, request):
		store = Store.objects.get(name=store_name)
		customer = Customer.objects.get(phone_number=request.user.phone_number, store=store)
		
		products = customer.favorites.all()
		to_products = f'{current_app_name}:product_detail'
	

		return render(request, f'{current_app_name}/customer-dashboard-favorites_{store.template_index}.html',
				 {'store_name':store_name,
				'products':products,
				'to_products':to_products,
				'customer':customer,
				})

class CustomerDashboardInfoView(IsCustomerUserMixin, View):

	form_class = CustomerForm
	def get(self, request):
		store = get_object_or_404(Store, name=store_name)
		customer = Customer.objects.get(phone_number=request.user.phone_number, store=store)
		form = CustomerForm
		return render(request, f'{current_app_name}/customer-dashboard-info_{store.template_index}.html', 
				{'form': form, 'customer':customer})

	def post(self, request):
		store = Store.objects.get(name=store_name)
		customer = Customer.objects.get(phone_number=request.user.phone_number, store=store)
		form = self.form_class(request.POST)
		if form.is_valid():
			customer.full_name = form.cleaned_data['full_name']
			customer.email = form.cleaned_data['email']
			customer.city = form.cleaned_data['city']
			customer.zip_code = form.cleaned_data['zip_code']
			customer.address = form.cleaned_data['address']
			customer.save()
			return redirect(f'{current_app_name}:customer_dashboard_info')

class CustomerDashboardCommentsView(IsCustomerUserMixin, View):

	def get(self, request):
		store = get_object_or_404(Store, name=store_name)
		customer = Customer.objects.get(phone_number=request.user.phone_number, store=store)
		comments = Comment.objects.filter(sender=customer)
		return render(request, f'{current_app_name}/customer-dashboard-comments_{store.template_index}.html',
				 {'comments': comments, 'customer':customer})

class DeliveryListCreateView(IsOwnerUserMixin ,View):

	template_name = f'{current_app_name}/owner-dashboard-delivery.html'

	def get(self, request, *args, **kwargs):
		form = DeliveryForm
		store = Store.objects.get(name=store_name)
		delivery_methods = Delivery.objects.filter(store=store)
		create_delivery_url = f'{current_app_name}:owner_dashboard_delivery'
		edit_delivery_url = f'{current_app_name}:edit_delivery'
		return render(request, self.template_name, {'edit_delivery_url':edit_delivery_url,
													'create_delivery_url':create_delivery_url,
													'form': form, 
													'delivery_methods':delivery_methods,
													'store_name':store_name})

	def post(self, request, *args, **kwargs):
		form = DeliveryForm(request.POST)
		if form.is_valid():
			store = Store.objects.get(name=store_name)
			delivery = Delivery.objects.create(
				store = store,
				name = form.cleaned_data['name'],
				price = form.cleaned_data['price'],
			)
			delivery_methods = Delivery.objects.filter(store=store)
			create_delivery_url = f'{current_app_name}:delivery-list-and-create'
			edit_delivery_url = f'{current_app_name}:edit_delivery'
			return redirect(f'{current_app_name}:owner_dashboard_delivery')
		create_delivery_url = f'{current_app_name}:delivery-list-and-create'
		edit_delivery_url = f'{current_app_name}:edit_delivery'
		return render(request, self.template_name, {'edit_delivery_url':edit_delivery_url,
													'create_delivery_url':create_delivery_url,
													'form': form, 
													'delivery_methods':delivery_methods,
													'store_name':store_name})

class DeliveryEditView(IsOwnerUserMixin ,View):

	def post(self, request, pk, *args, **kwargs):
		delivery = get_object_or_404(Delivery, pk=pk)
		form = DeliveryForm(request.POST)
		if form.is_valid():
			delivery.price = form.cleaned_data['price']
			delivery.save()
			return redirect('shop:owner_dashboard_delivery', store_name) 
		store = Store.objects.filter(name = store_name).first()
		delivery_methods = Delivery.objects.filter(store=store)
		create_delivery_url = f'{current_app_name}:delivery-list-and-create'
		edit_delivery_url = f'{current_app_name}:edit_delivery'
		return render(request, self.template_name, {'edit_delivery_url':edit_delivery_url,
													'create_delivery_url':create_delivery_url,
													'form': form, 
													'delivery_methods':delivery_methods,
													'store_name':store_name})

class DeliveryDeleteView(IsOwnerUserMixin, View):
		
	def get(self, request, pk, *args, **kwargs):
		delivery = Delivery.objects.get(pk=pk)
		delivery.delete()
		return redirect(f'{current_app_name}:owner_dashboard_delivery')

class CategoryCreateView(IsOwnerUserMixin, View):

	def post(self, request):
		form = CategoryForm(request.POST)
		if form.is_valid():
			store = Store.objects.get(name=store_name)
			name = form.cleaned_data['name']
			parent_id = form.cleaned_data['parent']
			is_sub = form.cleaned_data['is_sub']
			# translator = Translator()
			# translation = translator.translate(name)
			# slug = re.sub(r'\s+', '-', translation.text)
			# slug = slug.lower()
			slug = name.lower().replace(' ','-')
			category = Category.objects.create(store=store,
											   name=name,
											   is_sub=is_sub,
											   slug=slug)
			if parent_id != []:
				parent = Category.objects.filter(id=int(parent_id[0])).first()
				if parent != None:
					category.parent = parent
					category.save()

			return redirect(f'{current_app_name}:owner_dashboard_categories') 	 
		return render(request, f'{current_app_name}/category_list.html', {'form': form})
	
class CategoryListView(IsOwnerUserMixin, View):

	template_name = 'shop/owner-dashboard-categories.html'

	def get(self, request):
		store = Store.objects.get(name=store_name)
		categories = Category.objects.filter(store = store)
		create_category_url = f'{current_app_name}:create_category'
		edit_category_url = f'{current_app_name}:edit_category'
		return render(request, self.template_name, {'create_category_url':create_category_url,
											  		'edit_category_url':edit_category_url,
													'categories':categories,
													'store_name':store_name})

class CategoryDetailView(IsOwnerUserMixin, View):

	template_name = 'shop/category_detail.html'

	def get(self, request, pk):
		store = Store.objects.get(name=store_name)
		category = Category.objects.get(store=store, pk=pk)

		return render(request, self.template_name, {'category':category})
	
class CategoryUpdateView(IsOwnerUserMixin, View):

	template_name = 'shop/editcategory.html'

	def get(self, request, pk):
		store = Store.objects.get(name = store_name)
		categories = Category.objects.filter(store=store)
		category = Category.objects.get(id=pk)

		return render(request, self.template_name, {'category':category, 'categories':categories})

	def post(self, request, pk, *args, **kwargs):
		category = Category.objects.filter(id=pk).first()
		form = CategoryForm(request.POST)
		if form.is_valid():
			category = Category.objects.get(id = pk)
			category.store = Store.objects.get(name=store_name)
			category.name = form.cleaned_data['name']
			parent_id = form.cleaned_data['parent']
			if parent_id != '0':
				category.parent = Category.objects.get(id=parent_id)
				category.is_sub = True
			slug = category.name.lower().replace(' ','-')
			category.slug = slug
			if parent_id != []:
				parent = Category.objects.filter(id=int(parent_id[0])).first()
				if parent != None:
					category.parent = parent
			category.save()
			return redirect('shop:owner_dashboard_categories') 	 
		return render(request, self.template_name, {'form': form})

class CategoryDeleteView(IsOwnerUserMixin, DeleteView):

	def get(self, request, pk, *args, **kwargs):
		category = Category.objects.get(pk=pk)
		category.delete()
		return redirect(f'{current_app_name}:owner_dashboard_categories') 

class UploadProductImagesView(IsOwnerUserMixin, View):

	form_class = ProductImageForm
	template_name = f'{current_app_name}/editproduct.html'

	def post(self, request, pk, *args, **kwargs):
		product = Product.objects.get(pk=pk)
		form = ProductImageForm(request.POST, request.FILES)
		images = ProductImage.objects.filter(product=product)
		if form.is_valid():
			alt_name = form.cleaned_data['alt_name']
			print(form.cleaned_data)
			if alt_name == None:
				alt_name = f'{product.name}'
			images = request.FILES.getlist('images')
			store = Store.objects.get(name=store_name)
			for image in images:
				ProductImage.objects.create(alt_name=alt_name, image=image, product=product, store=store)
				new_upload = UploadedImages.objects.create(
				store = store,
				image = image,
				alt_name = alt_name,
			)
			return redirect(f'{current_app_name}:product_update', product.id)
		return render(request, self.template_name, {'images':images, 'form': form, 'product':product, 'store_name':store_name})

class DeleteProductImageView(IsOwnerUserMixin, View):

	def get(self, request, product_id, image_id):
		product = Product.objects.get(id=product_id)
		image = ProductImage.objects.get(id = image_id)
		image.delete()		
		return redirect(f'{current_app_name}:product_update', product.id)

class CopyProductView(IsOwnerUserMixin, View):

	def get(self, request, product_id):
		store = Store.objects.get(name = store_name)
		product = Product.objects.get(id = product_id)
		new_product = Product.objects.create(
			name = product.name + 'copy',
			store = store,
			slug = product.slug + str(randint(999, 10000)),
			price = product.price,
			description = product.description,
			brand = product.brand,
			sales_price = product.sales_price,
			off_active = product.off_active,
			available = product.available, 
			features = product.features,
		)
		default_variety = Variety.objects.create(
				store = store,
				name = 'default variety',
				product = new_product, 
				stock = 2,
			)

		for category in product.category.all():
			new_product.category.add(category)
		for tag in product.tags.all():
			new_product.tags.add(tag)
		product.save()

		return redirect(f'{current_app_name}:owner_dashboard_products')

class ProductCreateView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/addproduct.html'

	def get(self, request):
		store = Store.objects.get(name=store_name)
		form = ProductForm
		categories = Category.objects.filter(store=store)
		product_update_url = f'{current_app_name}:product_update'
		add_variety_url = f'{current_app_name}:add_variety'
		update_variety_url = f'{current_app_name}:update_variety'
		image_delete_url = f'{current_app_name}:product_image_delete'
		delete_variety_url = f'{current_app_name}:delete_variety'
		return render(request, self.template_name, {'form': form, 
													'categories': categories, 
													'store_name':store_name, 
													'product_update_url':product_update_url,
													'add_variety_url':add_variety_url,
													'update_variety_url':update_variety_url,
													'image_delete_url':image_delete_url,
													'delete_variety_url':delete_variety_url})

	def post(self, request):
		form = ProductForm(request.POST)
		store = Store.objects.get(name = store_name)
		categories = Category.objects.filter(store=store)
		if form.is_valid():
			store = Store.objects.get(name=store_name)
			print(form.cleaned_data)
			name = form.cleaned_data['name']
			if not name:
				return render(request, self.template_name, {'form': form, 'categories':categories, 'name_message':'لطفا نام محصول را وارد نمایید.'})
			slug = name.lower().replace(' ','-')
			price = form.cleaned_data['price']
			if not price:
				price = 0
			description = form.cleaned_data['description']
			tags = form.cleaned_data['tags']
			brand = form.cleaned_data['brand']
			processed_tags = [line for line in tags.splitlines()]
			new_brand, create = Brand.objects.get_or_create(store=store, name=brand)			
			sales_price = form.cleaned_data['sales_price']
			sales_price = sales_price
			off_active = form.cleaned_data['off_active']
			if off_active == ['1']:
				off_active = True
			if off_active == ['0']:
				off_active = False
			features = form.cleaned_data['features'].replace('\r\n', '<br>')

			product = Product.objects.create(store = store,
											 name = name,
											 slug = slug,
											 price = price, 
											 brand = brand,
											 description = description,
											 sales_price =sales_price,
											 off_active = off_active, 
											 features = features,
											 )
			category = form.cleaned_data['category']
				
			for cat in category:
				if cat == '0':
					product_cat, create = Category.objects.get_or_create(name='دسته‌بندی نشده', is_sub=False, store=store,slug='uncategorized')
				else:
					product_cat = Category.objects.get(id = int(cat))
				product.category.add(product_cat)

			product.tags.clear()

			for tag in processed_tags:
				name = tag
				slug = tag.replace(' ','-')
				new_tag, create = Tag.objects.get_or_create(name=name, slug=slug,store=store)
				product.tags.add(new_tag)
			
			product.save()

			default_variety = Variety.objects.create(
				store = store,
				name = 'default variety',
				product = product, 
				stock = 2,
			)

			return redirect(f'{current_app_name}:product_update', product.id)
		return render(request, self.template_name, {'form': form, 'categories':categories})
	
class ProductMetaTagsUpdateView(IsOwnerUserMixin, View):

	def post(self, request, product_slug):
		form = MetaForm(request.POST)
		if form.is_valid():
			store = Store.objects.get(name = store_name)
			product = Product.objects.get(slug = product_slug, store = store)
			product.meta_description = form.cleaned_data['meta_description']
			product.meta_keywords = form.cleaned_data['meta_keywords']
			product.meta_og_title = form.cleaned_data['meta_og_title']
			product.meta_og_description = form.cleaned_data['meta_og_description']
			product.meta_tc_title = form.cleaned_data['meta_tc_title']
			product.meta_tc_description = form.cleaned_data['meta_tc_description']
			product.save()
			return redirect(f'{current_app_name}:product_update', product.id)

class ProductUpdateView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/editproduct.html'

	def get(self, request, product_id):
		store = Store.objects.get(name=store_name)
		product = Product.objects.get(id=product_id, store=store)
		form = ProductForm
		form2 = ProductImageForm
		form3 = MetaForm
		form4 = VarietyForm
		form5 = VarietyUpdateForm
		categories = Category.objects.filter(store=store)
		images = ProductImage.objects.filter(product=product)
		varieties = Variety.objects.filter(product=product)
		filters = Filter.objects.filter(store = store)
		filter_values = FilterValue.objects.filter(product = product)
		upload_img_url = f'{current_app_name}:product_image_upload'
		product_update_url = f'{current_app_name}:product_update'
		add_variety_url = f'{current_app_name}:add_variety'
		update_variety_url = f'{current_app_name}:update_variety'
		image_delete_url = f'{current_app_name}:product_image_delete'
		delete_variety_url = f'{current_app_name}:delete_variety'
		return render(request, self.template_name, {'form': form, 
													'categories': categories, 
													'store_name':store_name, 
													'product': product, 
													'images':images, 
													'varieties':varieties,
													'form2':form2,
													'form3':form3,
													'form4':form4,
													'form5':form5,
													'filter_values':filter_values,
													'upload_img_url':upload_img_url,
													'product_update_url':product_update_url,
													'add_variety_url':add_variety_url,
													'update_variety_url':update_variety_url,
													'image_delete_url':image_delete_url,
													'delete_variety_url':delete_variety_url,
													'filters':filters})

	def post(self, request, product_id, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		product = Product.objects.get(id = product_id)
		form = ProductForm(request.POST)
		categories = Category.objects.filter(store=store)
		if form.is_valid():
			name = form.cleaned_data['name']
			product.name = name
			price = form.cleaned_data['price']
			product.price = price
			sales_price = form.cleaned_data['sales_price']
			product.sales_price = sales_price
			off_active = form.cleaned_data['off_active']
			print(off_active)
			if off_active == '1':
				product.off_active = True
			if off_active == '0':
				product.off_active = False
			brand = form.cleaned_data['brand']
			new_brand, create = Brand.objects.get_or_create(name=brand, store=store)
			product.brand = brand
			category = form.cleaned_data['category']
			if category != None:
				product.category.clear()
				product.save()
				if category == '0':
					product_cat, create = Category.objects.get_or_create(name='دسته‌بندی نشده', is_sub=False, store=store,slug='uncategorized')
				else:
					product_cat = Category.objects.get(id = int(category))
				product.category.add(product_cat)
				product.save()
			description = form.cleaned_data['description']
			product.description = description
			features = form.cleaned_data['features']
			product.features = features.replace('\r\n', '<br>')
			tags = form.cleaned_data['tags']
			processed_tags = [line for line in tags.splitlines()]
			product.tags.clear()

			for tag in processed_tags:
				name = tag
				slug = tag.replace(' ','-')
				new_tag, create = Tag.objects.get_or_create(name=name, slug=slug,store=store)
				product.tags.add(new_tag)
			
			product.save()
			
			return redirect(f'{current_app_name}:product_update', product.id)
		else:
			categories = Category.objects.filter(store=store)
			images = ProductImage.objects.filter(product=product)
			varieties = Variety.objects.filter(product=product)
			form = ProductForm
			form2 = ProductImageForm
			form3 = MetaForm
			form4 = VarietyForm
			form5 = VarietyUpdateForm
			upload_img_url = f'{current_app_name}:product_image_upload'
			product_update_url = f'{current_app_name}:product_update'
			add_variety_url = f'{current_app_name}:add_variety'
			update_variety_url = f'{current_app_name}:update_variety'
			image_delete_url = f'{current_app_name}:product_image_delete'
			delete_variety_url = f'{current_app_name}:delete_variety'
			return render(request, self.template_name, {'form': form, 
														'categories': categories, 
														'store_name':store_name, 
														'product': product, 
														'images':images, 
														'form2':form2,
														'form3':form3,
														'form4':form4,
														'form5':form5,
														'varieties':varieties,
														'upload_img_url':upload_img_url,
														'product_update_url':product_update_url,
														'add_variety_url':add_variety_url,
														'update_variety_url':update_variety_url,
														'image_delete_url':image_delete_url,
														'delete_variety_url':delete_variety_url})

class ProductListView(View):

	def get(self, request):
		items_per_page = 12
		store = Store.objects.get(name=store_name)
		categories = Category.objects.filter(store=store)
		products = Product.objects.filter(store=store)
		paginator = Paginator(products, items_per_page)
		page = request.GET.get('page', 1)
		try:
			products = paginator.page(page)
		except PageNotAnInteger:
			products = paginator.page(1)
		except EmptyPage:
			products = paginator.page(paginator.num_pages)
		brands = Brand.objects.filter(store=store)
		products_urls = f'{current_app_name}:product_detail'
		sizes = Size.objects.all()
		price_ranges = PriceRange.objects.all()
		return render(request, f'{current_app_name}/product_list_{store.template_index}.html', 
				{'products': products, 
				'to_products':products_urls, 
				'store_name':store_name, 
				'categories':categories,
				'brands':brands,
				'sizes':sizes,
				'price_ranges':price_ranges})
	
	def post(self, request, *args, **kwargs):
		main_filters = {}
		filters = []
		product_cat = None
		price_range = None
		selected_brand = None
		form = FilterProductsForm(request.POST)
		if form.is_valid():
			print(form.cleaned_data)
			store = Store.objects.get(name=store_name)
			category = form.cleaned_data['category']
			if category != '':
				product_cat = Category.objects.filter(id = int(category)).first()
				if category != '0':
					products = Product.objects.filter(category = product_cat, store = store)
				else:
					products = Product.objects.filter(store=store)
				categories = []
				if product_cat:
					if product_cat.is_sub == True:
						categories = []
					else:
						categories = [cat for cat in Category.objects.all() if cat.parent == product_cat]
			
			brands = Brand.objects.filter(store=store)	
			brand = form.cleaned_data['brand']
			if brand != '':
				selected_brand = Brand.objects.filter(id = brand).first()
				if brand != '0':
					products = products.filter(brand = selected_brand.name)
					main_selected_brand = Brand.objects.filter(id = brand).first()
					brands = list(Brand.objects.filter(id = brand))
				else:
					products = products.filter(store=store)
					if category != '0':
						brands = product_cat.get_category_brands()
							
			filtered_products = []
			price_ranges = form.cleaned_data['price_range']
			if price_ranges != '0':
				for price in price_ranges:
					selected_price_range = PriceRange.objects.filter(id = int(form.cleaned_data['price_range'])).first()
			else:
				selected_price_range = None

			if selected_price_range != None:
				for product in products:
								if product.price<selected_price_range.max_value and product.price>=selected_price_range.min_value:
									filtered_products.append(product.id)
			
			if filtered_products != []:
				products = products.filter(id__in=filtered_products, store=store)

			if selected_price_range != None and filtered_products == []:
				products = []
			
			store = Store.objects.get(name=store_name)
			products_urls = f'{current_app_name}:product_detail'
			sizes = Size.objects.all()
			price_ranges = PriceRange.objects.all()
			# if brand != '0':
			# 	selected_brand = Brand.objects.get(id=brand)
			# else:
			# 	selected_brand = None

			my_forms = []
			if category != '0':
				selected_category = Category.objects.filter(id = int(category)).first()
				filters = Filter.objects.filter(store=store)
				for filter in filters:
					values = filter.value.all()
					class FeatureFilterForm(forms.Form):
						name = filter.name
						choices = tuple([(value.value, value.value) for value in values])
						فیلترها = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple)
					new_form = FeatureFilterForm
					my_forms.append(new_form)
				category = Category.objects.get(slug = selected_category.slug, store=store)
				filters = Filter.objects.filter(category=category, store=store)
			else:
				selected_category = None

			selected_values = []
			active_filters = []
			for key, value in request.session.items():
				if key.startswith('filter-'):
					
					filter_name = key.replace('filter-', '')
					selected_filter = Filter.objects.get(store = store, name = filter_name)
					for posi_value in selected_filter.value.all():
						if posi_value.value in value:
							new_active_filter = {'filter':selected_filter,'value':posi_value}
							active_filters.append(new_active_filter)
							selected_values.append(posi_value.id)

			paginator = Paginator(products, 12)
			page = request.GET.get('page', 1)
			try:
				products = paginator.page(page)
			except PageNotAnInteger:
				# اگر شماره صفحه یک عدد نیست
				products = paginator.page(1)
			except EmptyPage:
				# اگر شماره صفحه بیشتر از تعداد کل صفحات است
				products = paginator.page(paginator.num_pages)

			return render(request, f'{current_app_name}/product_list_{store.template_index}.html', 
				 {'products': products, 
				'brands':brands,
				'to_products':products_urls, 
				'store_name':store_name, 
				'categories':categories,
				'sizes':sizes,
				'price_ranges':price_ranges,
				'selected_brand':selected_brand,
				'selected_price_range':selected_price_range,
				'selected_category':selected_category,
				'filters':filters,
				'category':selected_category,
				'my_forms':my_forms,
				'active_filters':active_filters,
				'main_filters': main_filters,
				'main_selected_category' : product_cat,
				'main_selected_brand' : selected_brand,
				'main_selected_price_range' : selected_price_range})
					
		return render(request, f'{current_app_name}/product_list_{store.template_index}.html', {'store_name':store_name})

class FilterTagProducts(View):

	def get(self, request, tag_slug):
		items_per_page = 12
		store = Store.objects.get(name=store_name)
		categories = Category.objects.filter(store=store)
		products = Product.objects.filter(store=store, tags__slug=tag_slug)
		paginator = Paginator(products, items_per_page)
		page = request.GET.get('page', 1)
		try:
			products = paginator.page(page)
		except PageNotAnInteger:
			products = paginator.page(1)
		except EmptyPage:
			products = paginator.page(paginator.num_pages)
		brands = Brand.objects.filter(store=store)
		products_urls = f'{current_app_name}:product_detail'
		sizes = Size.objects.all()
		price_ranges = PriceRange.objects.all()
		return render(request, f'{current_app_name}/product_list_{store.template_index}.html', 
				{'products': products, 
				'to_products':products_urls, 
				'store_name':store_name, 
				'categories':categories,
				'brands':brands,
				'sizes':sizes,
				'price_ranges':price_ranges})

class FeaturedProductListView(View):

	def get(self, request, source):
		store = Store.objects.get(name=store_name)
		categories = Category.objects.filter(store=store)
		products = Product.objects.filter(store=store)
		paginator = Paginator(products, 12)
		page = request.GET.get('page', 1)
		try:
			products = paginator.page(page)
		except PageNotAnInteger:
			products = paginator.page(1)
		except EmptyPage:
			products = paginator.page(paginator.num_pages)
		products_urls = f'{current_app_name}:product_detail'
		sizes = Size.objects.all()
		price_ranges = PriceRange.objects.all()
		parts = source.split('-')

		if len(parts) == 2 and parts[1].isnumeric():
			type_label, obj_id = parts
			obj_id = int(obj_id)

			if type_label == 'tag':
				products = Product.objects.filter(tags__id=obj_id)
			elif type_label == 'category':
				products = Product.objects.filter(category__id=obj_id)
		items_per_page = 12
		paginator = Paginator(products, items_per_page)
		page = request.GET.get('page', 1)
		try:
			products = paginator.page(page)
		except PageNotAnInteger:
			products = paginator.page(1)
		except EmptyPage:
			products = paginator.page(paginator.num_pages)		
		return render(request, f'{current_app_name}/product_list_{store.template_index}.html',
				 {'products': products, 
				'to_products':products_urls, 
				'store_name':store_name, 
				'categories':categories,
				'sizes':sizes,
				'price_ranges':price_ranges})

class AddToFavoritesView(View):

	def get(self, request, product_id, ref, *args, **kwargs):
		if isinstance(request.user, AnonymousUser):
			return redirect(f'{current_app_name}:customer_authentication', store_name)
		store = Store.objects.get(name=store_name)
		product = Product.objects.get(id=product_id)
		phone = request.user.phone_number
		customer = Customer.objects.filter(phone_number=phone, store=store).first()
		if product in customer.favorites.all():
			customer.favorites.remove(product)
		else:
			customer.favorites.add(product)

		if ref == 'index':
			return redirect(f'{current_app_name}:index')
		if ref == 'products':
			return redirect(f'{current_app_name}:product_list')
		if ref == 'product_detail':
			return redirect(f'{current_app_name}:product_detail', product.slug)

		if ref == 'fav_list':
			return redirect(f'{current_app_name}:customer_dashboard_favorites')			

class CategoryProductsListView(View):

	def get(self, request, category_slug, *args, **kwargs):
		store = Store.objects.get(name = store_name)
		filters = Filter.objects.filter(store=store)
		my_forms = []
		for filter in filters:
			values = filter.value.all()
			class FeatureFilterForm(forms.Form):
				name = filter.name
				choices = tuple([(value.value, value.value) for value in values])
				فیلترها = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple)
			new_form = FeatureFilterForm
			my_forms.append(new_form)
		category = Category.objects.get(slug = category_slug, store=store)
		categories = []
		if category.is_sub == True:
			categories = []
		else:
			categories = [cat for cat in Category.objects.all() if cat.parent == category]
		filters = Filter.objects.filter(category=category, store=store)
		products = Product.objects.filter(store=store,category=category)
		selected_values = []
		active_filters = []
		for key, value in request.session.items():
			# بررسی آیا کلید با الگوی مورد نظر شروع می‌شود
			if key.startswith('filter-'):
				
				filter_name = key.replace('filter-', '')
				selected_filter = Filter.objects.get(store = store, name = filter_name)
				for posi_value in selected_filter.value.all():
					if posi_value.value in value:
						new_active_filter = {'filter':selected_filter,'value':posi_value}
						active_filters.append(new_active_filter)
						selected_values.append(posi_value.id)
		products = Product.get_filtered_products(Product ,selected_values)
		products = products.filter(store = store, category = category)
		products_urls = f'{current_app_name}:product_detail'
		sizes = Size.objects.all()
		price_ranges = PriceRange.objects.all()
		paginator = Paginator(products, 12)
		page = request.GET.get('page', 1)
		brands = category.get_category_brands()
		try:
			products = paginator.page(page)
		except PageNotAnInteger:
			products = paginator.page(1)
		except EmptyPage:
			products = paginator.page(paginator.num_pages)
		return render(request, f'{current_app_name}/product_list_{store.template_index}.html', 
				{'products': products, 
				'to_products':products_urls, 
				'store_name':store_name, 
				'categories':categories,
				'sizes':sizes,
				'price_ranges':price_ranges,
				'category':category,
				'filters':filters,
				'brands': brands,
				'my_forms':my_forms,
				'active_filters':active_filters,
				'main_selected_category': category
				})
		
class ProductDetailView(View):

	def get(self, request, product_slug ):
		store = Store.objects.get(name=store_name)
		product = Product.objects.filter(slug = product_slug, store=store).first()
		product.views = product.views + 1
		product.save()
		varieties = Variety.objects.filter(product=product)
		message = ''
		form = PurchaseForm()
		comments = Comment.objects.filter(product=product)
		services = Services.objects.filter(store=store)
		if isinstance(request.user, AnonymousUser):
			for key, value in request.session.items():
					if str(product.id)==key:
						message = f'شما در حال حاضر {value} عدد از این کالا را در سبد خرید خود دارید.'
		else:
			customer = Customer.objects.get(phone_number = request.user.phone_number, store=store)
			cart , create= Cart.objects.get_or_create(customer = customer, store = store)
			cart_item = cart.items.filter(variety__in = varieties, store=store).first()
			if cart_item != None:
				message = f'شما در حال حاضر {cart_item.quantity} عدد از این کالا را در سبد خرید خود دارید.'
		
		add_to_cart_url = f'{current_app_name}:add-to-cart'
		products = Product.objects.filter(store=store)
		return render(request, f'{current_app_name}/product_detail_{store.template_index}.html', 
				{'services':services,'products':products,'product': product,'comments':comments ,'varieties':varieties,'form':form, 'message':message, 'add_to_cart':add_to_cart_url, 'store_name':store_name})

class ProductDeleteView(IsOwnerUserMixin, View):
	
	def get(self, request, product_slug):
		store = Store.objects.get(name=store_name)
		product = Product.objects.filter(slug = product_slug, store=store).first()
		product.delete()
		return redirect(f'{current_app_name}:owner_dashboard_products')

class CreateUpdateVarietyView(IsOwnerUserMixin, View):
	
	def post(self, request, pk, *args, **kwargs):
		product = Product.objects.get(pk=pk)
		form=VarietyForm(request.POST)
		if form.is_valid():
			store = Store.objects.get(name=store_name)
			name = form.cleaned_data['name']
			stock = form.cleaned_data['stock']
			exist_variety = Variety.objects.filter(product=product, name=name, store=store).first()

			if exist_variety != None:
				exist_variety.delete()	
			new_variety = Variety.objects.create(name=name,stock=stock,product=product, store=store)
		return redirect(f'{current_app_name}:product_update',product.id)

class UpdateVarietyView(IsOwnerUserMixin, View):

	def post(self, request, product_id, variety_id, *args, **kwargs):
		product = Product.objects.get(pk=product_id)
		form=VarietyUpdateForm(request.POST)
		if form.is_valid():
			variety = Variety.objects.get(pk=variety_id)
			stock = form.cleaned_data['stock']
			variety.stock = stock
			variety.save()
			return redirect(f'{current_app_name}:product_update',product.id)

class DeleteVarietyView(IsOwnerUserMixin, View):

	def get(self, request, product_id, variety_id, *args, **kwargs):
		variety = Variety.objects.get(pk=variety_id)
		product = Product.objects.get(id = product_id)
		variety.delete()
		return redirect(f'{current_app_name}:product_update',product.id)

class CommentCreateView(IsCustomerUserMixin, View):

	def post(self, request, product_id):
		store = Store.objects.get(name=store_name)
		customer = Customer.objects.get(phone_number=request.user.phone_number, store= store)
		product = get_object_or_404(Product, id=product_id)
		form = CommentForm(request.POST)
		if form.is_valid():
			store = Store.objects.get(name=store_name)
			email = form.cleaned_data['email']
			body = form.cleaned_data['body']
			comment = Comment.objects.create(
				store=store,
				product=product,
				sender=customer,
				email=email,
				body=body,
			)
			comment.save()
			return redirect('shop:product_detail', product.slug)  # Redirect to the product detail page
		return redirect('shop:product_detail', product.slug)
	
class CommentApproveView(IsOwnerUserMixin, View):

	def get(self, request, comment_id, status_id, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		comment = Comment.objects.get(id=comment_id)
		product = comment.product
		
		if status_id == 1:
			comment.approved = True
			comment.save()
		else:
			comment.approved = False
			comment.save()
		
		return redirect(f'{current_app_name}:owner_dashboard_comments')
	
class OwnerDashboardCommentsView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/owner-dashboard-comments.html'

	def get(self, request, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		comments = Comment.objects.filter(store=store)
		return render(request, self.template_name, {'store_name':store_name, 'comments':comments})

class CartView(IsCustomerUserMixin, View):

	def get(self, request, cart_id):
		store = Store.objects.get(name=store_name)
		customer = Customer.objects.filter(phone_number=request.user.phone_number, store=store).first()
		cart = Cart.objects.filter(id=cart_id).first()
		form = PurchaseForm
		edit_cart_url = f"{current_app_name}:cart_item_update' cart_id=cart.pk item_id=item.pk "
		return render(request, f'{current_app_name}/cart_{store.template_index}.html',
				 {'form': form, 'cart': cart, 'edit_cart':edit_cart_url, 'store_name':store_name})

	def post(self, request, cart_id, *args, **kwargs):
		item_id = kwargs['item_id']
		store = Store.objects.get(name=store_name)
		form = CartEditForm(request.POST)
		cart = Cart.objects.filter(id=cart_id).first()
		cart_item = cart.items.filter(id=item_id).first()
		if form.is_valid():
			cart_item.quantity = form.cleaned_data['count']
			cart_item.save()
			cart.save
			return redirect(f'{current_app_name}:cart_view', cart_id)
		edit_cart_url = f"{current_app_name}:cart_item_update' cart_id=cart.pk item_id=item.pk "
		return render(request, f'{current_app_name}/cart_{store.template_index}.html',
				 {'cart': cart, 'message': 'Something is going wrong', 'edit_cart':edit_cart_url, 'store_name':store_name})

class AddToCartView(View):
	
	message =''

	def post(self, request, pk, *args, **kwargs):
		form = PurchaseForm(request.POST)
		store = Store.objects.get(name = store_name)
		if form.is_valid():
			replicate = False
			product = Product.objects.get(pk = pk)
			quantity = form.cleaned_data['count']
			size = form.cleaned_data['size']
			
			if size == '':
				default_variety = Variety.objects.filter(product=product, name = 'default variety').first()
				variety_id = default_variety.id
				variety = default_variety
			else:
				variety_id = int(form.cleaned_data['size'])
				variety = Variety.objects.get(id = variety_id)

			if size=='0':
				varieties = Variety.objects.filter(product=product)
				add_to_cart_url = f'{current_app_name}:add-to-cart'
				return render(request, f'{current_app_name}/product_detail_{store.template_index}.html', {'message':'لطفا تنوع مورد نظر خود را انتخاب نمایید.','product': product, 'varieties':varieties,'form':form, 'add_to_cart':add_to_cart_url, 'store_name':store_name})
			
			
			if quantity>variety.stock:
				varieties = Variety.objects.filter(product=product)
				add_to_cart_url = f'{current_app_name}:add-to-cart'
				return render(request,  f'{current_app_name}/product_detail_{store.template_index}.html', {'message':f'از این تنوع تنها {variety.stock} عدد در انبار موجود است.','product': product, 'varieties':varieties,'form':form, 'add_to_cart':add_to_cart_url, 'store_name':store_name})
			
			new_item = {'product': product, 'quantity': quantity}
			if isinstance(request.user, AnonymousUser):
		
				for key, value in request.session.items():
					if str(variety.id)==key:
						request.session[str(variety.id)] += quantity
						replicate = True
						break
					
				if replicate == False:
					request.session.update({variety.id: quantity})
			else:
				customer = Customer.objects.filter(phone_number = request.user.phone_number, store = store).first()
				cart, create = Cart.objects.get_or_create(customer = customer, store = store)
				if cart.items.filter(variety=variety, store = store).exists():
					cart_item = cart.items.get(variety=variety, store = store)
					cart_item.quantity = quantity
					cart_item.save()
				else:
					cart_item = CartItem.objects.create(variety=variety, quantity=quantity, store = store)
				
				cart.items.add(cart_item)

			return redirect(f'{current_app_name}:product_detail' ,product.slug)

class CustomerRegisterLoginView(View):
	
	template_name = f'{current_app_name}/register-customer.html'
	message = 'Please Insert Your Phone Number'

	def get(self, request):
		form = RequestNumberForm()
		return render(request, self.template_name, {'form': form, 'message':self.message})

	def post(self, request):
		form = RequestNumberForm(request.POST)
		store = Store.objects.get(name = store_name)
		if form.is_valid():
			phone_number = form.cleaned_data['phone_number']
			customer = Customer.objects.filter(phone_number=phone_number, store = store).first()
			authen_form = AuthenticationCodeForm()
			if customer != None:
				previous_codes = OtpCode.objects.filter(phone_number = phone_number)
				previous_codes.delete()
				random_code = random.randint(100000,999999)
				send_otp_code(phone_number,random_code)
				new_otp = OtpCode.objects.create(phone_number = phone_number, code = random_code) 
				return redirect(f'login/{phone_number}')
			customer = Customer.objects.create(phone_number = phone_number, store = store)
			user = User.objects.get_or_create(phone_number = phone_number)
			previous_codes = OtpCode.objects.filter(phone_number = phone_number)
			previous_codes.delete()
			random_code = random.randint(100000,999999)
			send_otp_code(phone_number,random_code)
			new_otp = OtpCode.objects.create(phone_number = phone_number, code = random_code) 
			return redirect(f'login/{phone_number}')
		message = 'Invalid Input'
		return render(request, self.template_name, {'message':message, 'form':form})

class CustomerloginView(View):
	template_name = f'{current_app_name}/login.html'

	def get(self, request, phone_number):
		form = AuthenticationCodeForm()
		return render(request, self.template_name, {'form':form})
	
	def post(self, request, phone_number, *args, **kwargs):
		form = AuthenticationCodeForm(request.POST)
		if form.is_valid():
			customer_phone = phone_number
			store = Store.objects.get(name=store_name)
			customer = Customer.objects.filter(phone_number = customer_phone, store = store).first()
			user = User.objects.filter(phone_number = customer_phone).first()
			request.user = user
			last_sent_otp = OtpCode.objects.filter(phone_number = customer_phone).first()
			recieved_code = form.cleaned_data['code']
			if last_sent_otp.code == recieved_code:
				customer.otp_token = form.cleaned_data['code']
				customer.save()
				login(request, user)
				cart, created = Cart.objects.get_or_create(customer = customer, store = store)
				varieties = Variety.objects.filter(store=store)
				varieties_id_list = []
				for variety in varieties:
					varieties_id_list.append(str(variety.id))
				for key, value in request.session.items():
					if key in varieties_id_list:
						variety = Variety.objects.filter(id = int(key)).first()
						if cart.items.filter(variety=variety).exists():
							cart_item = cart.items.get(variety=variety)
							cart_item.quantity = value
							cart_item.save()
						else:
							cart_item = CartItem.objects.create(variety=variety, quantity=value, store = store)
							cart.items.add(cart_item)
				for key in list(request.session.keys()):
					if key in varieties_id_list:
						del request.session[key]
				
				return redirect(f'{current_app_name}:index')
			return render(request, self.template_name, {'form':form, 'message':'wrong code'})
		return render(request, self.template_name, {'form':form, 'message':'Invalid Input'})

class CustomerOrdersView(IsCustomerUserMixin, View):

	def get(self, request):
		store = Store.objects.get(name = store_name)
		customer = Customer.objects.filter(phone_number=request.user.phone_number, store = store).first()
		orders = Order.objects.filter(customer=customer, store = store)
		return render(request, f'{current_app_name}/customer-dashboard-orders_{store.template_index}.html', {'orders':orders})
	
class CustomerFavoritesView(IsCustomerUserMixin, View):

	def get(self, request):
		fav_products = None
		store = Store.objects.get(name = store_name)
		customer = Customer.objects.filter(phone_number=request.user.phone_number, store = store).first()
		if customer != None:
			fav_products = customer.favorites.all()
			return render(request, f'{current_app_name}/customer_favorites_{store.template_index}.html', {'fav_products':fav_products, 'message':'Favorite Products'})
		return render(request, f'{current_app_name}/customer_favorites_{store.template_index}.html', {'fav_products':fav_products, 'message':'You should sign in first'})

class DeleteCartItemView(View):

	def  get(self, request, cart_id, item_id, *args, **kwargs):
		cart_item = CartItem.objects.get(id=item_id)
		cart_item.delete()
		return redirect(f'{current_app_name}:cart_view', cart_id)

class CreateOrderView(IsCustomerUserMixin, View):

	def get(self, request):
		message = ''
		store = Store.objects.get(name = store_name)
		customer = Customer.objects.filter(phone_number=request.user.phone_number, store = store).first()
		cart = Cart.objects.filter(customer=customer, store = store).first()
		if cart.items.all().first() != None:
			items = cart.items.all()
			total_price = 0
			order_status = OrderStatus.objects.get(pk=2)
			for item in items:
				price = item.variety.product.get_active_price()*item.quantity
				total_price += price
			order = Order.objects.create(customer=customer, total_price=total_price, status = order_status, store=store)
			order.items.set(items)
			cart.items.clear()
			return redirect(f'{current_app_name}:order_detail' , order.id)
		return render(request, f'{current_app_name}/empty-cart_{store.template_index}.html', {'store_name':store_name})

class OrderDetailView(IsCustomerUserMixin ,View):

	form_class = CouponApplyForm

	def get(self, request, order_id):
		order = Order.objects.get(id=order_id)
		store = Store.objects.get(name = store_name)
		order_detail_url = f"{current_app_name}:apply_coupon"
		delivery_methods = Delivery.objects.filter(store=store)
		form2 = DeliveryApplyForm
		return render(request, f'{current_app_name}/order_detail_{store.template_index}.html', {'form2':form2,'delivery_methods':delivery_methods ,'order':order, 'form':self.form_class, 'order_detail':order_detail_url, 'store_name':store_name})

class OrderWrongCouponView(IsCustomerUserMixin, View):

	form_class = CouponApplyForm

	def get(self, request, order_id,wrong_code):
		order = get_object_or_404(Order, id=order_id)
		store = Store.objects.get(name = store_name)
		order_detail_url = f"{current_app_name}:apply_coupon"
		delivery_methods = Delivery.objects.filter(store=store)
		form2 = DeliveryApplyForm
		message = 'کد وارد شده اشتباه و یا منقضی است.'
		return render(request, f'{current_app_name}/order_detail_{store.template_index}.html', {'form2':form2,'delivery_methods':delivery_methods ,'order':order, 'form':self.form_class, 'order_detail':order_detail_url, 'store_name':store_name,'message':message})

class CouponApplyView(IsCustomerUserMixin, View):

	form_class = CouponApplyForm
	current_datetime = datetime.now()
	def post(self, request, order_id, *args, **kwargs):
		form = self.form_class(request.POST)
		if form.is_valid():
			code = form.cleaned_data['code']
			store = Store.objects.get(name = store_name)
			coupon = Coupon.objects.filter(code__exact=code, store=store).first()
			if coupon == None:
				return redirect(f'{current_app_name}:order_detail', order_id, 'wrong_code')
			order = Order.objects.get(id=order_id)
			current_datetime = datetime.now()
			jalali_datetime  = JalaliDatetime(current_datetime)
			formatted_date = jalali_datetime.strftime('%Y/%m/%d')
			if jalali_datetime.year>=coupon.get_from_year() and jalali_datetime.year<=coupon.get_to_year():
				if jalali_datetime.month>=coupon.get_from_month() and jalali_datetime.month<=coupon.get_to_month():
					if jalali_datetime.day>=coupon.get_from_day() and jalali_datetime.day<=coupon.get_to_day():
						if order.used_coupon == True:
							return redirect(f'{current_app_name}:order_detail', order_id)
						else:
							order.total_price -= coupon.discount
							order.used_coupon = True
							order.save()
						return redirect(f'{current_app_name}:order_detail', order_id)
			wrong_code='wrong_code'
			return redirect(f'{current_app_name}:order_detail', order_id, wrong_code)
	
class DeliveryApplyView(IsCustomerUserMixin, View):

	def post(self, request, order_id, *args, **kwargs):
		form = DeliveryApplyForm(request.POST)
		if form.is_valid():
			delivery = form.cleaned_data['delivery']
			store = Store.objects.get(name = store_name)
			try:
				method = Delivery.objects.get(id=int(delivery), store=store)
			except Delivery.DoesNotExist:
				messages.error(request, 'this method does not exists', 'danger')
				return redirect(f'{current_app_name}:order_detail' ,order_id)
			order = Order.objects.get(id=order_id)
			order.delivery_method =  method
			order.save()
		return redirect(f'{current_app_name}:order_detail', order_id)

class CreateCouponView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/owner-dashboard-coupons.html'

	def get(self, request):
		form = CouponForm()
		return render(request, self.template_name, {'form': form})

	def post(self, request):
		form = CouponForm(request.POST)
		store = Store.objects.get(name = store_name)
		if form.is_valid():
			print(form.cleaned_data)
			return redirect(f'{current_app_name}:owner_dashboard_coupons')
		return render(request, self.template_name, {'form': form})

class CouponListView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/owner-dashboard-coupons.html'

	def get(self, request):
		store = Store.objects.get(name = store_name)
		coupons = Coupon.objects.filter(store = store)
		return render(request, self.template_name, {'coupons': coupons, 'store_name':store_name})
	
	def post(self, request):
		form = CouponForm(request.POST)
		store = Store.objects.get(name = store_name)
		if form.is_valid():
			code = form.cleaned_data['code']
			from_time = form.cleaned_data['from_time']
			to_time = form.cleaned_data['to_time']
			discount = form.cleaned_data['discount']
			new_coupon = Coupon.objects.create(store=store,
											code=code,
											valid_from=from_time,
											valid_to=to_time,
											discount=discount)
			current_datetime = datetime.now()


			return redirect(f'{current_app_name}:owner_dashboard_coupons')
		return render(request, self.template_name, {'form': form})

class DeleteCouponView(IsOwnerUserMixin, View):

	def get(self, request, coupon_id, *args, **kwargs):
		coupon = Coupon.objects.get(id=coupon_id)
		coupon.delete()
		return redirect(f'{current_app_name}:owner_dashboard_coupons', store_name)

class OrderListView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/order_list.html'

	def get(self, request, *args, **kwargs):
		store = Store.objects.get(name = store_name)
		orders = Order.objects.filter(store = store)
		order_process_url = f'{current_app_name}:update_order_status'
		return render(request, self.template_name, {'orders': orders, 'order_process':order_process_url, 'store_name':store_name})	

class OrderProcessView(IsOwnerUserMixin, View):

	def get(self, request, order_id, status_id):
		store = Store.objects.get(name=store_name)
		order = Order.objects.get(id=order_id)
		status = OrderStatus.objects.get(id=status_id)
		order.status = status
		order.save()
		return redirect(f'{current_app_name}:owner_dashboard_orders')

class CustomerListView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/customers_list.html'

	def get(self, request):
		store = Store.objects.get(name=store_name)
		customers = Customer.objects.filter(store = store)
		return render(request, self.template_name, {'customers':customers})

class AboutUsPageView(View):

	def get(self, request):
		store = Store.objects.get(name = store_name)
		logo = StoreLogoImage.objects.filter(store=store).first()
		return render(request, f'{current_app_name}/about_{store.template_index}.html', {'logo':logo,'description':store.about_description})

class ContactUsPageView(View):

	def get(self, request):
		store = Store.objects.get(name = store_name)
		return render(request, f'{current_app_name}/contact_{store.template_index}.html', {'store':store})

	def post(self, request, *args, **kwargs):
		form = ContactUsForm(request.POST)
		store = Store.objects.get(name = store_name)
		if form.is_valid():
			
			name = form.cleaned_data['name']
			familly_name = form.cleaned_data['familly_name']
			email = form.cleaned_data['email']
			phone = form.cleaned_data['phone']
			subject = form.cleaned_data['subject']
			message_text = form.cleaned_data['message_text']

			new_message = ContactMessage.objects.create(
				name = name,
				store=store,
				familly_name=familly_name,
				email=email,
				phone=phone,
				subject=subject,
				message=message_text
			)
			return render(request, f'{current_app_name}/contact_{store.template_index}.html', {'message':'پیام شما با موفقیت ارسال گردید.'})
		return render(request, f'{current_app_name}/contact_{store.template_index}.html', {'message':'مقادیر به درستی وارد نشده‌اند.'})

class ProductSearchView(View):

	def get(self, request, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		query = request.GET.get('q')
		if query:
			
			products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query), store=store).distinct()
		else:
			products = Product.objects.filter(store=store)

		products_urls = f'{current_app_name}:product_detail'
		sizes = Size.objects.all()
		price_ranges = PriceRange.objects.all()
		categories = Category.objects.filter(store=store)
		paginator = Paginator(products, 12)
		page = request.GET.get('page', 1)
		try:
			products = paginator.page(page)
		except PageNotAnInteger:
			products = paginator.page(1)
		except EmptyPage:
			products = paginator.page(paginator.num_pages)
		return render(request, f'{current_app_name}/product_list_{store.template_index}.html', {'products': products, 
													'query': query, 
													'to_products':products_urls, 
													'store_name':store_name, 
													'categories':categories,
													'sizes':sizes,
													'price_ranges':price_ranges})

class CreateSlideView(IsOwnerUserMixin, View):

	def post(self, request, index, *args, **kwargs):
		form = AddSlideForm(request.POST, request.FILES)
		store = Store.objects.get(name=store_name)
		slide, create= Slide.objects.get_or_create(store=store, index=index)
		if form.is_valid():
			
			source = form.cleaned_data['source']
			if source != '':
				slide.source = source

			slide.save()

			parts = source.split('-')
	
			if len(parts) == 2 and parts[1].isnumeric():
				type_label, obj_id = parts
				obj_id = int(obj_id)

				if type_label == 'tag':
					tag = Tag.objects.filter(store = store, id=obj_id).first()
				elif type_label == 'category':
					category = Category.objects.filter(store=store, id=obj_id).first()
			return redirect(f'{current_app_name}:owner_dashboard_edit_home')

class CreateBannerView(IsOwnerUserMixin, View):
	def post(self, request, index, *args, **kwargs):
		form = AddBannerForm(request.POST, request.FILES)
		store = Store.objects.get(name=store_name)
		if index == '1' or index == '2':
			size = 'small'
		else:
			size = 'big'
		banner, create= Banner.objects.get_or_create(store=store, index=index, size = size)
		if form.is_valid():

			alt_name = form.cleaned_data['alt_name']
			if alt_name != '':
				banner.alt_name = alt_name

			image = request.FILES.get('image')
			if image != None:
				banner.image=image
			
			source = form.cleaned_data['source']
			if source != '':
				banner.source = source

			banner.save()

			new_upload = UploadedImages.objects.create(
				store = store,
				image = image,
				alt_name = alt_name,
			)

			parts = source.split('-')
	
			if len(parts) == 2 and parts[1].isnumeric():
				type_label, obj_id = parts
				obj_id = int(obj_id)

				if type_label == 'tag':
					tag = Tag.objects.filter(store = store, id=obj_id).first()
				elif type_label == 'category':
					category = Category.objects.filter(store=store, id=obj_id).first()
			return redirect(f'{current_app_name}:owner_dashboard_edit_home')

class HomePageUpdateView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/owner-dashboard-edit-home.html'

	def get(self, request, *args, **kwargs):

		form = AddSlideForm
		store = Store.objects.get(name = store_name)
		slide1 = Slide.objects.filter(store=store, index=1).first()
		slide2 = Slide.objects.filter(store=store, index=2).first()
		slide3 = Slide.objects.filter(store=store, index=3).first()
		slide4 = Slide.objects.filter(store=store, index=4).first()

		banner1 = Banner.objects.filter(store=store, index=1).first()
		banner2 = Banner.objects.filter(store=store, index=2).first()
		banner3 = Banner.objects.filter(store=store, index=3).first()


		categories = Category.objects.filter(store=store)
		tags = Tag.objects.filter(store=store)

		featured_categories = FeaturedCategories.objects.filter(store=store).first()

		return render(request, self.template_name, {'form':form, 
											  		'featured_categories': featured_categories,
													'store_name':store_name,
													'slide1':slide1,
													'slide2':slide2,
													'slide3':slide3,
													'slide4':slide4,
													'categories':categories,
													'tags':tags,
													'banner1':banner1,
													'banner2':banner2,
													'banner3':banner3,})

class FaqView(View):

	def get(self, request, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		faqs = Faq.objects.filter(store=store)
		return render(request, f'{current_app_name}/faq_{store.template_index}.html', {'store_name':store_name, 'faqs':faqs})
	
class FaqCreateView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/owner-dashboard-faq.html'

	def get(self, request, *args, **kwargs):
		form = FaqForm
		store = Store.objects.get(name=store_name)
		faqs = Faq.objects.filter(store=store)
		return render(request, self.template_name, {'store_name':store_name, 'faqs':faqs})

	def post(self, request, *args, **kwargs):
		form = FaqForm(request.POST)
		store=Store.objects.get(name=store_name)
		if form.is_valid():
			question = form.cleaned_data['question']
			answer = form.cleaned_data['answer']
			new_faq = Faq.objects.create(store=store, question=question, answer=answer)
			return redirect(f'{current_app_name}:faq_create')

class FaqUpdateView(IsOwnerUserMixin, View):

	def post(self, request, faq_id, *args, **kwargs):
		form = FaqForm(request.POST)
		store=Store.objects.get(name=store_name)
		faq = Faq.objects.get(store=store, id=faq_id)
		if form.is_valid():
			question = form.cleaned_data['question']
			answer = form.cleaned_data['answer']
			faq.question = question
			faq.answer = answer
			faq.save()
			return redirect(f'{current_app_name}:faq_create')

class FaqDeleteView(IsOwnerUserMixin, View):

	def get(self, request, faq_id, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		faq = Faq.objects.get(store=store, id=faq_id)
		faq.delete()
		return redirect(f'{current_app_name}:faq_create')
	
class LogoUpdateView(IsOwnerUserMixin, View):

	def post(self, request, *args, **kwargs):
		form = LogoUpdateForm(request.POST, request.FILES)
		store = Store.objects.get(name=store_name)
		if form.is_valid():
			logo = request.FILES.get('logo')
			existing_logos = StoreLogoImage.objects.filter(store=store)
			existing_logos.delete()
			new_logo = StoreLogoImage.objects.create(store = store,
											image = logo,
											alt_name = f'{store_name} logo',
											custom_name = f'{store_name} logo',)
			new_upload = UploadedImages.objects.create(
				store = store,
				image = logo,
				alt_name = f'{store_name} logo'
			)
		return redirect(f'{current_app_name}:owner_dashboard_store_update')

class OrderPayView(IsCustomerUserMixin, View):
	
	def get(self, request, order_id):
		store = Store.objects.get(name = store_name)
		MERCHANT = 'ab11efee-695b-4070-a6ac-cb22fba2f2eb'
		if store.merchant != None:
			MERCHANT = store.merchant

		form = CheckoutForm
		order = Order.objects.get(id=order_id)
		if order.delivery_method == None:
			store = Store.objects.get(name = store_name)
			delivery_methods = Delivery.objects.filter(store=store)
			copun_form = CouponApplyForm
			form2 = DeliveryApplyForm
			return render(request, f'{current_app_name}/order_detail_{store.template_index}.html', {'form': copun_form ,'store':store, 'order':order, 'message2':'لطفا یک شیوه ارسال را انتخاب و اعمال نمایید', 'delivery_methods':delivery_methods, 'form2': form2})
		return render(request, f'{current_app_name}/checkout_{store.template_index}.html', {'store':store, 'order':order, 'form':form})

	def post(self, request, order_id, *args, **kwargs):

		form = CheckoutForm(request.POST)
		order = Order.objects.get(id=order_id)
		store = Store.objects.get(name = store_name)
		if form.is_valid():
			name_message = ''
			familly_name_message = ''
			phone_number_message = ''
			email_message = ''
			state_message = ''
			city_message = ''
			zip_code_message = ''
			address_message = ''
			print(form.cleaned_data)
			empty_field = False
			name = form.cleaned_data['name']
			if not name:
				name_message = 'فیلد نام نباید خالی باشد'
				empty_field = True
			familly_name = form.cleaned_data['familly_name']
			if not familly_name:
				familly_name_message = 'فیلد نام خانوادگی نباید خالی باشد'
				empty_field = True
			phone_number = form.cleaned_data['phone_number']
			if not phone_number:
				phone_number_message = 'فیلم شماره تماس نباید خالی باشد'
				empty_field = True
			email = form.cleaned_data['email']
			if not email:
				email_message = 'فیلد ایمیل نباید خالی باشد'
				empty_field = True
			state = form.cleaned_data['state']
			if not state:
				state_message = 'فیلد استان نباید خالی باشد'
				empty_field = True
			city = form.cleaned_data['city']
			if not city:
				city_message = 'فیلد شهر نباید خالی باشد'
				empty_field = True
			zip_code = form.cleaned_data['zip_code']
			if not zip_code:
				zip_code_message = 'فیلد کد پستی نباید خالی باشد'
				empty_field = True
			address = form.cleaned_data['address']
			if not address:
				address_message = 'فیلد آدرس نباید خالی باشد'
				empty_field = True
			if empty_field == True:
				return render(request, f'{current_app_name}/checkout_{store.template_index}.html', {
				'store':store, 
				'order':order, 
				'form':form,
				'name_message': name_message,
				'familly_name_message': familly_name_message,
				'phone_number_message': phone_number_message,
				'email_message': email_message,
				'state_message': state_message,
				'city_message': city_message,
				'zip_code_message': zip_code_message,
				'address_message': address_message}) 

			order.reciever_name = name
			order.reciever_familly_name = familly_name
			order.reciever_phone_number = phone_number
			order.reciever_email = email
			order.reciever_state = state
			order.reciever_city = city
			order.reciever_zip_code = zip_code
			order.reciever_address = address
			order.save()

		order = Order.objects.get(id=order_id)
		request.session['order_pay'] = {
			'order_id': order.id,
		}

		if order.get_final_payment() == 0:
			order.status = OrderStatus.objects.get(id=1)
			customer = order.customer
			customer.wallet_balance -= order.get_without_cashback_cost()
			customer.save()
			order.paid_by_wallet = order.get_without_cashback_cost()
			order.save()
			return redirect(f'{current_app_name}:customer_dashboard_order_detail', order.id)

		store = Store.objects.get(name = store_name)
		MERCHANT = 'ab11efee-695b-4070-a6ac-cb22fba2f2eb'
		if store.merchant != None:
			MERCHANT = store.merchant

		req_data = {
			"merchant_id": MERCHANT,
			"amount": order.get_final_payment()*10,
			"callback_url": f'https://picosite.ir/shop/{store_name}/orders/verify/',
			"description": description,
			"metadata": {"mobile": request.user.phone_number, "email": request.user.email}
		}
		req_header = {"accept": "application/json",
					"content-type": "application/json'"}
		req = requests.post(url=ZP_API_REQUEST, data=json.dumps(
			req_data), headers=req_header)
		authority = req.json()['data']['authority']
		if len(req.json()['errors']) == 0:
			return redirect(ZP_API_STARTPAY.format(authority=authority))
		else:
			e_code = req.json()['errors']['code']
			e_message = req.json()['errors']['message']
			return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")

class OrderVerifyView(LoginRequiredMixin, View):

	template_name = f'{current_app_name}/customer-payment-result.html'

	def get(self, request):
		paid_status = OrderStatus.objects.get(id=1)
		order_id = request.session['order_pay']['order_id']
		order = Order.objects.get(id=int(order_id))
		store = order.store
		store_name = order.store.name
		if store.merchant != None:
			MERCHANT = store.merchant
		t_status = request.GET.get('Status')
		t_authority = request.GET['Authority']
		if request.GET.get('Status') == 'OK':
			req_header = {"accept": "application/json",
						  "content-type": "application/json'"}
			req_data = {
				"merchant_id": MERCHANT,
				"amount": order.get_final_payment()*10,
				"authority": t_authority
			}
			req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
			if len(req.json()['errors']) == 0:
				t_status = req.json()['data']['code']
				if t_status == 100:
					order.status = paid_status
					customer = order.customer
					if order.get_final_payment() >= customer.wallet_balance:
						customer.wallet_balance = 0
						order.paid_by_wallet = customer.wallet_balance
						
					else:
						customer.wallet_balance -= order.get_final_payment()
						order.paid_by_wallet = order.get_final_payment()
					customer.save()
					
					order.save()
					
					return render(request, self.template_name, {'message':'پرداخت شما موفقیت آمیز بود. سفارش شما ثبت گردید و در حال پردازش است ', 'ref_id':req.json()['data']['ref_id'], 'store_name':store_name})
				elif t_status == 101:
					return render(request, self.template_name, {'message':str(req.json()['data']['message']), 'store_name':store_name})
				else:
					return render(request, self.template_name, {'message':'پرداخت ناموفق ', 'store_name':store_name})
			else:
				e_code = req.json()['errors']['code']
				e_message = req.json()['errors']['message']
				return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
		else:
			return render(request, self.template_name, {'message':'پرداخت ناموفق ', 'store_name':store_name})

class OwnerDashboardFinanceView(IsOwnerUserMixin, View):
	
	template_name = f'{current_app_name}/owner-dashboard-finance.html'

	def get(self, request, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		records = WithdrawRecord.objects.filter(store=store)
		balance = store.balance
		owner_name = store.get_owner_name
		form = WithdrawForm
		return render(request, self.template_name, {
			'store_name':store_name,
			'store':store,
			'balance':balance,
			'owner_name':owner_name,
			'form':form,
			'message':'',
			'records':records,
		})

	def post(self, request, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		balance = store.balance
		records = WithdrawRecord.objects.filter(store=store)
		owner_name = store.get_owner_name
		form = WithdrawForm(request.POST)
		if form.is_valid():
			sheba = form.cleaned_data['sheba_number']
			amount = form.cleaned_data['amount']
			if amount <=balance:
				new_withdraw = WithdrawRecord.objects.create(
					store=store,
					sheba=sheba,
					amount = amount,
				)
				store.balance -= amount
				store.save()
				return redirect(f'{current_app_name}:owner_dashboard_finance')
			return render(request, self.template_name, {
														'store_name':store_name,
														'store':store,
														'balance':balance,
														'owner_name':owner_name,
														'form':form,
														'message':'مبلغ وارد شده بیش از اعتبار فروشگاه است.',
														'records':records,
														}) 
		return render(request, self.template_name, {
														'store_name':store_name,
														'store':store,
														'balance':balance,
														'owner_name':owner_name,
														'form':form,
														'message':'لطفا مقادیر را کامل و به درستی وارد نمایید.',
														'records':records,
														}) 

class BlogPostCreateView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/add-blog-post.html'

	def get(self, request, *args, **kwargs):
		form = BlogPostCreateForm
		store = Store.objects.get(name = store_name)
		blog_categories = BlogCategory.objects.filter(store=store)
		return render(request, self.template_name, {
			'form':form,
			'store_name':store_name,
			'blog_categories':blog_categories,
			'store':store,
		})

	def post(self, request, *args, **kwargs):
		form = BlogPostCreateForm(request.POST) 
		store = Store.objects.get(name = store_name)
		if form.is_valid():
			title = form.cleaned_data['title']
			translator = Translator()
			translation = translator.translate(title)
			slug = re.sub(r'\s+', '-', translation.text)
			slug = slug.lower()
			body = form.cleaned_data['body']
			published = form.cleaned_data['published']
			cat_id = form.cleaned_data['category']
			category = BlogCategory.objects.get(id=cat_id)
			new_post = BlogPost.objects.create(
				title = title,
				slug = slug,
				body=body,
				published=published,
				store=store,
				category=category,
			)
			return redirect(f'{current_app_name}:edit_blog_post', new_post.slug)

class OwnerDashboardBlogView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/owner-dashboard-blog.html'

	def get(self, request, *args, **kwargs):
		store = Store.objects.get(name = store_name)
		posts = BlogPost.objects.filter(store=store)
		return render(request, self.template_name, {'store_name':store_name, 'store':store, 'posts':posts})

class BlogPostEditView(IsOwnerUserMixin, View):
	
	template_name = f'{current_app_name}/edit-blog-post.html'

	def get(self, request, post_slug, *args, **kwargs):
		form = BlogPostCreateForm
		meta_form = MetaForm
		post = BlogPost.objects.get(slug = post_slug)
		store = Store.objects.get(name = store_name)
		blog_categories = BlogCategory.objects.filter(store=store)
		return render(request, self.template_name, {
			'form':form,
			'store_name':store_name,
			'blog_categories':blog_categories,
			'store':store,
			'post':post,
			'meta_form':meta_form,
		})

	def post(self, request, post_slug, *args, **kwargs):
		form = BlogPostCreateForm(request.POST) 
		meta_form = MetaForm
		store = Store.objects.get(name = store_name)
		if form.is_valid():
			blog_categories = BlogCategory.objects.filter(store=store)
			post = BlogPost.objects.get(slug = post_slug, store = store)
			title = form.cleaned_data['title']
			translator = Translator()
			translation = translator.translate(title)
			slug = re.sub(r'\s+', '-', translation.text)
			slug = slug.lower()
			body = form.cleaned_data['body']
			published = form.cleaned_data['published']
			cat_id = form.cleaned_data['category']
			category = BlogCategory.objects.get(id=cat_id)
			post.title = title
			post.slug=slug
			post.body=body
			post.published=published
			post.category = category
			post.save()
			return redirect(f'{current_app_name}:edit_blog_post', post.slug)
		return render(request, self.template_name, {
			'form':form,
			'store_name':store_name,
			'blog_categories':blog_categories,
			'store':store,
			'post':post,
			'meta_form':meta_form,
		})
	
class PostMetaUpdateView(IsOwnerUserMixin, View):

	def post(self, request, post_slug):

		store = Store.objects.get(name = store_name)
		post = BlogPost.objects.get(slug = post_slug, store = store)
		form = MetaForm(request.POST)
		if form.is_valid():
			post.meta_description = form.cleaned_data['meta_description']
			post.meta_keywords = form.cleaned_data['meta_keywords']
			post.meta_og_title = form.cleaned_data['meta_og_title']
			post.meta_og_description = form.cleaned_data['meta_og_description']
			post.meta_tc_title = form.cleaned_data['meta_tc_title']
			post.meta_tc_description = form.cleaned_data['meta_tc_description']
			post.save()
			return redirect(f'{current_app_name}:edit_blog_post', post.slug)
		
class PostThumbnailUpdateView(IsOwnerUserMixin, View):

	def post(self, request, post_id, *args, **kwargs):
		form = PostThumbnailUpdateForm(request.POST, request.FILES)
		store = Store.objects.get(name=store_name)

		if form.is_valid():
			thumbnail = request.FILES.get('thumbnail')
			post = BlogPost.objects.get(id=post_id)
			existing_tumbnail = PostThumbnail.objects.filter(store=store, post=post)
			existing_tumbnail.delete()
			new_thumbnail = PostThumbnail.objects.create(store = store,
											post=post,
											image = thumbnail,
											alt_name = post.title,)
			new_upload = UploadedImages.objects.create(
				store = store,
				image = thumbnail,
				alt_name = post.title
			)
		return redirect(f'{current_app_name}:edit_blog_post', post.slug)

class BlogCategoryCreateView(IsOwnerUserMixin, View):
	
	def post(self, request, *args, **kwargs):
		form = BlogCategoryForm(request.POST)
		if form.is_valid():
			cat_name = form.cleaned_data['name']
			store = Store.objects.get(name = store_name)
			new_blog_category = BlogCategory.objects.create(store=store, name = cat_name)
			return redirect(f'{current_app_name}:owner_dashboard_blog_category')

class BlogCategoryEditView(IsOwnerUserMixin, View):

	def post(self, request, blog_category_id, *args, **kwargs):
		form = BlogCategoryForm(request.POST)
		if form.is_valid():
			blog_category = BlogCategory.objects.get(id=blog_category_id)
			blog_category.name = form.cleaned_data['name']
			blog_category.save()
			return redirect(f'{current_app_name}:owner_dashboard_blog_category') 

class BlogCategoryDeleteView(IsOwnerUserMixin, View):

	def get(self, request, blog_category_id, *args, **kwargs):
		blog_category = BlogCategory.objects.get(id=blog_category_id)
		blog_category.delete()
		return redirect(f'{current_app_name}:owner_dashboard_blog_category') 

class OwnerDashboardBlogCategoryView(IsOwnerUserMixin, View):
	
	template_name = f'{current_app_name}/owner-dashboard-blog-category.html'

	def get(self, request, *args, **kwargs):
		form = BlogCategoryForm
		store = Store.objects.get(name = store_name)
		blog_categories = BlogCategory.objects.filter(store=store)
		return render(request, self.template_name, {'store':store,
		'store_name':store_name,
		'blog_categories':blog_categories,
		'form':form})
	
class BlogView(View):

	def get(self, request, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		posts = BlogPost.objects.filter(store=store)
		products = Product.objects.filter(store=store)
		blog_categories = BlogCategory.objects.filter(store = store)
		return render(request, f'{current_app_name}/blog_{store.template_index}.html', {'store_name':store_name,
											  'store':store,
											  'posts':posts,
											  'products':products,
											  'blog_categories':blog_categories})
	
class BlogPostDetailView(View):

	def get(self, request, post_slug, *args, **kwargs):
		store = Store.objects.get(name = store_name)
		post = BlogPost.objects.get(slug = post_slug, store = store)
		posts = BlogPost.objects.filter(store=store)
		blog_categories = BlogCategory.objects.filter(store=store)
		return render(request, f'{current_app_name}/blog-detail_{store.template_index}.html', {'store':store,
											  'post':post,
											  'posts':posts,
											  'blog_categories':blog_categories})

class ImageBankView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/image-bank.html'

	def get(self, request, image_class, index, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		image_class = image_class
		uploaded_images = UploadedImages.objects.filter(store=store)
		# picosite_bank = BankImage.objects.all()
		form = ImageUploadForm
		return render(request, self.template_name, {'store_name':store_name,
											  'uploaded_images':uploaded_images,
											#   'picosite_bank':picosite_bank,
											  'image_class':image_class,
											  'index':index,
											  'form':form,})

	def post(self, request, image_class, index, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		form = ImageUploadForm(request.POST, request.FILES)
		uploaded_images = UploadedImages.objects.filter(store=store)
		# picosite_bank = BankImage.objects.all()
		if form.is_valid():
			image = request.FILES.get('image')
			new_image = UploadedImages.objects.create(image=image,store=store,alt_name=f'{store_name}-{image_class}-{index}')
			return redirect(f'{current_app_name}:image_bank', image_class, index)
		return render(request, self.template_name, {'store_name':store_name,
											  'uploaded_images':uploaded_images,
											#   'picosite_bank':picosite_bank,
											  'image_class':image_class,
											  'index':index,
											  'form':form,
											  'message':'در آپلود تصویر مشکلی ایجاد شده است. لطفا دوباره تلاش نمایید.'})
		
class ApplyFromImageBankView(IsOwnerUserMixin, View):

	def get(self, request, image_class, index, source, image_id, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		if source == 'uploaded_image':
			image = UploadedImages.objects.get(id=image_id).image
		# if source == 'picosite_image':
		# 	image = BankImage.objects.get(id=image_id).image
		if image_class == 'slide':
			slide = Slide.objects.get(index = index, store=store)
			slide.image = image
			slide.save()
			return redirect(f'{current_app_name}:owner_dashboard_edit_home')
		if image_class == 'banner':
			banner = Banner.objects.get(index=index, store=store)
			banner.image = image
			banner.save()
			return redirect(f'{current_app_name}:owner_dashboard_edit_home')
		if image_class == 'logo':
			logo = StoreLogoImage.objects.filter(store=store).first()
			logo.image = image
			logo.save()
			return redirect(f'{current_app_name}:owner_dashboard_edit_home')
		if image_class == 'category':
			category = Category.objects.filter(store=store, id=index).first()
			category_image, create = CategoryImage.objects.get_or_create(category=category, store=store)
			category_image.image = image
			category_image.save()
			return redirect(f'{current_app_name}:owner_dashboard_categories')

class DeleteCategoryImageView(IsOwnerUserMixin, View):

	def get(self, request, category_id, *args, **kwargs):
		store = Store.objects.get(name = store_name)
		category = Category.objects.get(id=category_id)
		image = CategoryImage.objects.get(category=category)
		image.delete()
		return redirect(f'{current_app_name}:owner_dashboard_categories')

class GetFeaturedCategories(IsOwnerUserMixin, View):
	
	def post(self, request, *args, **kwargs):
		form = HomeCategoryShowForm(request.POST)
		if form.is_valid():
			store = Store.objects.get(name=store_name)
			categories = form.cleaned_data['categories']
			store_featured_cats, created = FeaturedCategories.objects.get_or_create(store=store)

			# Clear existing categories
			store_featured_cats.categories.clear()

			# Add new categories
			store_featured_cats.categories.add(*categories)

		return redirect(f'{current_app_name}:owner_dashboard_edit_home')

class SubscribeView(IsCustomerUserMixin, View):

	def post(self, request, *args, **kwargs):
		form = SubscriptionForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			store = Store.objects.get(name = store_name)
			new_subscriber, create = Subscription.objects.get_or_create(store=store, email=email)
			return redirect(f'{current_app_name}:index')

class ChangeThemeLayoutView(IsOwnerUserMixin, View):

	def post(self, request, *args, **kwargs):
		store = Store.objects.get(name=store_name)
		form = ThemeForm(request.POST)
		if form.is_valid():
			color = form.cleaned_data['color']
			h = color.lstrip('#')
			RGB_color = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
			theme_color = f'{RGB_color[0]},{RGB_color[1]},{RGB_color[2]}'
			store.color = theme_color
			store.save()
			return redirect(f'{current_app_name}:owner_dashboard_edit_home')
		
class CreateTicketView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/owner-dashboard-create-ticket.html'

	def get(self, request):

		ticket_form = TicketForm
		store = Store.objects.get(name = store_name)
		return render(request, self.template_name, {'store_name':store_name, 'ticket_form':ticket_form})

	def post(self, request):

		ticket_form = TicketForm(request.POST)
		if ticket_form.is_valid():
			store = Store.objects.get(name = store_name)
			subject = ticket_form.cleaned_data['subject']
			body = ticket_form.cleaned_data['body']
			new_ticket = Ticket.objects.create(
				store=store,
				subject = subject,
				body=body
			)
			return redirect(f'{current_app_name}:owner_dashboard_ticket_list')
		return render(request, self.template_name, {'store_name':store_name, 'ticket_form':ticket_form, 'message': 'مقادیر وارد شده خالی یا  نامعتبر است'})

class TicketDetailAndReplyView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/owner-dashboard-ticket-detail.html'
	
	def get(self, request, ticket_id):

		form = TicketReplyForm
		ticket = Ticket.objects.get(id=ticket_id)
		replies = TicketReply.objects.filter(ticket = ticket)

		return render(request, self.template_name, {'ticket':ticket ,'form':form, 'store_name':store_name, 'replies':replies})


	def post(self, request, ticket_id):

		form = TicketReplyForm(request.POST)
		ticket = Ticket.objects.get(id = ticket_id)
		replies = TicketReply.objects.filter(ticket = ticket)
		if form.is_valid():
			store = Store.objects.get(name = store_name)
			body = form.cleaned_data['body']
			new_ticket_reply = TicketReply.objects.create(
				body=body,
				ticket = ticket
			)
			ticket.is_answered = False
			ticket.save()
			return redirect(f'{current_app_name}:owner_dashboard_ticket_list')
		return render(request, self.template_name, {'ticket':ticket ,'form':form, 'store_name':store_name, 'replies':replies, 'message':'مقادیر وارد شده خالی یا نامعتبر است'})

class TicketListView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/owner-dashboard-tickets.html'

	def get(self, request):
		store = Store.objects.get(name = store_name)
		tickets = Ticket.objects.filter(store = store)
		return render(request, self.template_name, {'store_name':store_name, 'tickets':tickets})

class CloseTicketView(IsOwnerUserMixin, View):

	def get(self, request, ticket_id):
		ticket = Ticket.objects.get(id=ticket_id)
		ticket.is_closed = True
		ticket.save()
		return redirect(f'{current_app_name}:owner_dashboard_ticket_list')

class EditPoliciesView(IsOwnerUserMixin, View):

	template_name = f'{current_app_name}/owner-dashboard-policies.html'

	def get(self, request):
		store = Store.objects.get(name = store_name)
		form = PoliciesForm
		return render(request, self.template_name, {'store_name':store_name, 'store':store, 'form':form})
	
	def post(self, request):
		store = Store.objects.get(name = store_name)
		form = PoliciesForm(request.POST)
		if form.is_valid():
			store.policies = form.cleaned_data['policies']
			store.save()
			return redirect(f'{current_app_name}:owner_dashboard_policies')
		
class PoliciesView(View):

	def get(self, request):
		store = Store.objects.get(name = store_name)
		return render(request, f'{current_app_name}/policies_{store.template_index}.html', {'store':store})
	
class FilterView(View):

	template_name = f'{current_app_name}/owner-dashboard-filters.html'

	def get(self, request):
		form = AddFilterForm
		store = Store.objects.get(name = store_name)
		categories = Category.objects.filter(store = store)
		filters = Filter.objects.filter(store = store)
		return render(request, self.template_name, {'store':store, 'store_name':store_name, 'filters':filters, 'form':form, 'categories':categories})

	def post(self, request, *args, **kwargs):
		form = AddFilterForm(request.POST)
		if form.is_valid():
			store = Store.objects.get(name = store_name)
			category = Category.objects.get(store = store, name=form.cleaned_data['category'])
			new_filter, create = Filter.objects.get_or_create(
				category = category,
				name = form.cleaned_data['name'],
				store = store
			)
			return redirect(f'{current_app_name}:owner_dashboard_filters')
		
class DeleteFilter(View):

	def get(self, request, filter_id):
		filter = Filter.objects.get(id = filter_id)
		for value in filter.value.all():
			value.delete()
		filter.delete()
		return redirect(f'{current_app_name}:owner_dashboard_filters')
	
class AsignFilterToProductView(View):

	def post(self, request, product_id, *args, **kwargs):
		form = AsignFilterToProductForm(request.POST)
		if form.is_valid():
			store = Store.objects.get(name = store_name)
			product = Product.objects.get(id = product_id)
			filter = Filter.objects.get(store = store , name = form.cleaned_data['filter'])
			new_filter_asign , create= FilterValue.objects.get_or_create(
				store = store, 
				value = form.cleaned_data['value'] 
			)
			new_filter_asign.product.add(product)
			filter.value.add(new_filter_asign)
			filter.save()
			return redirect(f'{current_app_name}:product_update', product.id)

class DeleteFilterValueView(View):

	def get(self, request, product_id ,filter_value_id):
		filter_value = FilterValue.objects.get(id = filter_value_id)
		product = Product.objects.get(id = product_id)
		filter_value.delete()
		return redirect(f'{current_app_name}:product_update', product.id)

form_classes = [type(f'FeatureFilterForm{i}', (FeatureFilterForm,), {}) for i in range(1, 4)]

class FeatureFilterView(View):
	def post( self , request, category_slug, form_name):
		store = Store.objects.get(name = store_name)
		category = Category.objects.get(store=store, slug = category_slug)
		filter = Filter.objects.filter(store=store, name = form_name).first()
		values = filter.value.all()
		class FeatureFilterForm(forms.Form):
			name = filter.name
			choices = tuple([(value.value, value.value) for value in values])
			فیلترها = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple)
		form = FeatureFilterForm(request.POST)
		if form.is_valid():
			products = Product.objects.filter(store=store,category=category)
			categories = Category.objects.filter(store=store)
			sizes = Size.objects.all()
			price_ranges  = PriceRange.objects.all()
			filters = Filter.objects.filter(store = store)
			request.session.modified = True
			request.session[f'filter-{filter.name}'] = form.cleaned_data['فیلترها']
			request.session['temp_cat'] = category.name
			request.session.modified = True
			my_forms = []
			for filter in filters:
				values = filter.value.all()
				class FeatureFilterForm(forms.Form):
					name = filter.name
					choices = tuple([(value.value, value.value) for value in values])
					فیلترها = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple)
				new_form = FeatureFilterForm
				my_forms.append(new_form)
			
			selected_values = []
			active_filters = []
			for key, value in request.session.items():
				# بررسی آیا کلید با الگوی مورد نظر شروع می‌شود
				if key.startswith('filter-'):
					
					filter_name = key.replace('filter-', '')
					selected_filter = Filter.objects.get(store = store, name = filter_name)
					for posi_value in selected_filter.value.all():
						if posi_value.value in value:
							new_active_filter = {'filter':selected_filter,'value':posi_value}
							active_filters.append(new_active_filter)
							selected_values.append(posi_value.id)
			products = Product.get_filtered_products(Product ,selected_values)

			return render(request, f'{current_app_name}/product_list_{store.template_index}.html', 
				{'products': products, 
				'store_name':store_name, 
				'categories':categories,
				'sizes':sizes,
				'price_ranges':price_ranges,
				'category':category,
				'filters':filters,
				'my_forms':my_forms,
				'active_filters':active_filters,
				})

class ClearActiveFilterValueView(View):

	def get(self, request, filter_id, value_id):
		active_filter = Filter.objects.get(id = filter_id)
		category = active_filter.category
		active_value = FilterValue.objects.get(id = value_id)
		for key, value in request.session.items():
			if active_filter.name in key and active_value.value in value:
				if len(value) == 1:
					del request.session[key]
				else:
					value.remove(active_value.value)
				request.session.modified = True

				return redirect(f'{current_app_name}:category_products', category.slug )

class OwnerDashboardAnnouncements(View):

	template_name = 'shop/owner-dashboard-announcements.html'

	def get(self, request):
		store = Store.objects.get(name = store_name)
		announcements = []
		store.has_notif = False
		store.save()
		
		for item in Announcement.objects.all():
			if store in item.store.all() and item.is_active == True:
				announcements.append(item)
		return render(request, self.template_name, {'store':store, 'store_name':store_name, 'announcements':announcements})

def format_features(features_list):
	output = ""
	for feature in features_list:
		title = feature['title']
		values = feature['values']
		values_str = ', '.join(values)  
		output += f"{title}: {values_str}<br>"
	return output

def download_and_save_images(image_urls, product_id):
	product = Product.objects.get(id=product_id)
	store = product.store
	
	for url in image_urls:
		response = requests.get(url)
		if response.status_code == 200:
			image_name = f'{product.name}-{store.name}'[0:249]
			timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
			image_filename = f"{timestamp}_{os.path.splitext(image_name)[0][:100]}{os.path.splitext(image_name)[1]}"
			
			image = ProductImage(
				store=store,
				product=product,
			)
			
			image.image.save(image_filename, ContentFile(response.content))
			image.save()

def download_and_save_main_image(image_url, product_id):
	product = Product.objects.get(id=product_id)
	store = product.store
	
	url = image_url
	response = requests.get(url)
	if response.status_code == 200:
		image_name = f'{product.name}'
		image_filename = f"{image_name}"
		image = ProductImage(
			store=store,
			product=product,
		)
		image.image.save(image_filename, ContentFile(response.content))
		image.save()

class AddProductFromDigikalaView(View):

	def post(self, request):

		form = AddingProductFromDigiForm(request.POST)
		if form.is_valid():
			category_list = request.POST.getlist('category')
			dkp_code = form.cleaned_data['dkp_code']
			numbers = dkp_code.split("-")
			numbers = [int(num) for num in numbers]
			for dkp_code in numbers:
				url = f'https://api.digikala.com/v2/product/{dkp_code}/'
				shop_name = f'{Store.objects.all().first().name}'
				try:
					response = requests.get(url)
					response.raise_for_status()
					item = response.json()['data']['product']
					brand = ''
					title = ''
					features= []
					description = ''
					price = 0
					tags = []
					images = []
					main_image = ''

					if item['specifications'][0] == [] or item['specifications'][0] == None:
						features = []
					else:
						features= item['specifications'][0]['attributes']
					brand = item['data_layer']['brand']
					title = item['title_fa']
					price = item['default_variant']['price']['selling_price']
					tags = [tag['name'] for tag in item['tags']]
					images = [image['url'][0].replace('?x-oss-process=image/resize,m_lfit,h_800,w_800/quality,q_90','').replace(' ','') for image in item['images']['list']]
					main_image = item['images']['main']['url'][0].replace('?x-oss-process=image/resize,m_lfit,h_800,w_800/quality,q_90',''),
					main_image = main_image[0]
					description = item['review']['description']
				except requests.exceptions.HTTPError as err:
					print(f'HTTP error occurred: {err}')
				except Exception as err:
					print(f'Other error occurred: {err}')

				store = Store.objects.all().first()
				if not description:
					description = '-'
				slug = title.replace(' ','-')
				description = description
				features = features
				brand = brand
				product_brand, create = Brand.objects.get_or_create(
					name = brand,
					store = store
				)
				price = price/10
				tags = tags
				new_product = Product.objects.create(
					name = title,
					store = store,
					slug = slug,
					description = description,
					features = format_features(features),
					brand = product_brand.name,
					price = price,
				)
				for category_id in category_list:
					if category_id == '0':
						category, create = Category.objects.get_or_create(store = store,
																			name = 'دسته‌بندی نشده',
																			slug = 'ungategorized')
					else:
						category = Category.objects.get(id = category_id)
					new_product.category.add(category)
					new_product.save()
					images = images
					download_and_save_main_image(main_image, new_product.id)
					download_and_save_images(images, new_product.id)
					default_variety = Variety.objects.create(
						store = store,
						name = 'default variety',
						product = new_product, 
						stock = 2,
					)
		return redirect('shop:product_list')				
					
class SpecialProductListView(View):

	def get(self, request, tag_name):
		tag = Tag.objects.filter(name=tag_name).first()
		products = tag.get_products()
		items_per_page = 12
		store = Store.objects.get(name=store_name)
		categories = Category.objects.filter(store=store)
		paginator = Paginator(products, items_per_page)
		page = request.GET.get('page', 1)
		try:
			products = paginator.page(page)
		except PageNotAnInteger:
			products = paginator.page(1)
		except EmptyPage:
			products = paginator.page(paginator.num_pages)
		brands = Brand.objects.filter(store=store)
		products_urls = f'{current_app_name}:product_detail'
		sizes = Size.objects.all()
		price_ranges = PriceRange.objects.all()
		return render(request, f'{current_app_name}/product_list_{store.template_index}.html', 
				{'products': products, 
				'to_products':products_urls, 
				'store_name':store_name, 
				'categories':categories,
				'brands':brands,
				'sizes':sizes,
				'price_ranges':price_ranges})
	
	def post(self, request, tag_name, *args, **kwargs):
		main_filters = {}
		filters = []
		product_cat = None
		price_range = None
		selected_brand = None
		tag = Tag.objects.filter(name=tag_name).first()
		products = tag.get_products()
		form = FilterProductsForm(request.POST)
		if form.is_valid():
			print(form.cleaned_data)
			store = Store.objects.get(name=store_name)
			category = form.cleaned_data['category']
			if category != '':
				product_cat = Category.objects.filter(id = int(category)).first()
				if category != '0':
					products = products.filter(category = product_cat, store = store)
				else:
					products = products.filter(store=store)
				
			brand = form.cleaned_data['brand']
			if brand != '':
				selected_brand = Brand.objects.filter(id = brand).first()
				if brand != '0':
					products = products.filter(brand = selected_brand.name)
				else:
					products = products.filter(store=store)
							
			filtered_products = []
			price_ranges = form.cleaned_data['price_range']
			if price_ranges != '0':
				for price in price_ranges:
					selected_price_range = PriceRange.objects.filter(id = int(form.cleaned_data['price_range'])).first()
			else:
				selected_price_range = None

			if selected_price_range != None:
				for product in products:
								if product.price<selected_price_range.max_value and product.price>=selected_price_range.min_value:
									filtered_products.append(product.id)
			
			if filtered_products != []:
				products = products.filter(id__in=filtered_products, store=store)

			if selected_price_range != None and filtered_products == []:
				products = []
			categories = Category.objects.filter(store=store)
			store = Store.objects.get(name=store_name)
			products_urls = f'{current_app_name}:product_detail'
			sizes = Size.objects.all()
			price_ranges = PriceRange.objects.all()
			brands = Brand.objects.filter(store=store)
			if brand != '0':
				selected_brand = Brand.objects.get(id=brand)
			else:
				selected_brand = None

			my_forms = []
			if category != '0':
				selected_category = Category.objects.filter(id = int(category)).first()
				filters = Filter.objects.filter(store=store)
				for filter in filters:
					values = filter.value.all()
					class FeatureFilterForm(forms.Form):
						name = filter.name
						choices = tuple([(value.value, value.value) for value in values])
						فیلترها = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple)
					new_form = FeatureFilterForm
					my_forms.append(new_form)
				category = Category.objects.get(slug = selected_category.slug, store=store)
				filters = Filter.objects.filter(category=category, store=store)
			else:
				selected_category = None

			selected_values = []
			active_filters = []
			for key, value in request.session.items():
				if key.startswith('filter-'):
					
					filter_name = key.replace('filter-', '')
					selected_filter = Filter.objects.get(store = store, name = filter_name)
					for posi_value in selected_filter.value.all():
						if posi_value.value in value:
							new_active_filter = {'filter':selected_filter,'value':posi_value}
							active_filters.append(new_active_filter)
							selected_values.append(posi_value.id)

			paginator = Paginator(products, 12)
			page = request.GET.get('page', 1)
			try:
				products = paginator.page(page)
			except PageNotAnInteger:
				# اگر شماره صفحه یک عدد نیست
				products = paginator.page(1)
			except EmptyPage:
				# اگر شماره صفحه بیشتر از تعداد کل صفحات است
				products = paginator.page(paginator.num_pages)

			return render(request, f'{current_app_name}/product_list_{store.template_index}.html', 
				 {'products': products, 
				'brands':brands,
				'to_products':products_urls, 
				'store_name':store_name, 
				'categories':categories,
				'sizes':sizes,
				'price_ranges':price_ranges,
				'selected_brand':selected_brand,
				'selected_price_range':selected_price_range,
				'selected_category':selected_category,
				'filters':filters,
				'category':selected_category,
				'my_forms':my_forms,
				'active_filters':active_filters,
				'main_filters': main_filters,
				'main_selected_category' : product_cat,
				'main_selected_brand' : selected_brand,
				'main_selected_price_range' : selected_price_range})
					
		return render(request, f'{current_app_name}/product_list_{store.template_index}.html', {'store_name':store_name})

class BrandProductListView(View):

	def get(self, request, brand_name):
		brand = Brand.objects.filter(name=brand_name).first()
		products = Product.objects.filter(brand=brand.name)
		items_per_page = 12
		store = Store.objects.get(name=store_name)
		categories = Category.objects.filter(store=store)
		paginator = Paginator(products, items_per_page)
		page = request.GET.get('page', 1)
		try:
			products = paginator.page(page)
		except PageNotAnInteger:
			products = paginator.page(1)
		except EmptyPage:
			products = paginator.page(paginator.num_pages)
		brands = Brand.objects.filter(store=store)
		products_urls = f'{current_app_name}:product_detail'
		sizes = Size.objects.all()
		price_ranges = PriceRange.objects.all()
		return render(request, f'{current_app_name}/product_list_{store.template_index}.html', 
				{'products': products, 
				'to_products':products_urls, 
				'store_name':store_name, 
				'categories':categories,
				'brands':brands,
				'sizes':sizes,
				'price_ranges':price_ranges})
	
	def post(self, request, brand_name, *args, **kwargs):
		main_filters = {}
		filters = []
		product_cat = None
		price_range = None
		
		brand = Brand.objects.filter(name=brand).first()
		products = Product.objects.filter(brand=brand.name)
		selected_brand = brand
		form = FilterProductsForm(request.POST)
		if form.is_valid():
			print(form.cleaned_data)
			store = Store.objects.get(name=store_name)
			category = form.cleaned_data['category']
			if category != '':
				product_cat = Category.objects.filter(id = int(category)).first()
				if category != '0':
					products = products.filter(category = product_cat, store = store)
				else:
					products = products.filter(store=store)
				
			brand = form.cleaned_data['brand']
			if brand != '':
				selected_brand = Brand.objects.filter(id = brand).first()
				if brand != '0':
					products = products.filter(brand = selected_brand.name)
				else:
					products = products.filter(store=store)
							
			filtered_products = []
			price_ranges = form.cleaned_data['price_range']
			if price_ranges != '0':
				for price in price_ranges:
					selected_price_range = PriceRange.objects.filter(id = int(form.cleaned_data['price_range'])).first()
			else:
				selected_price_range = None

			if selected_price_range != None:
				for product in products:
								if product.price<selected_price_range.max_value and product.price>=selected_price_range.min_value:
									filtered_products.append(product.id)
			
			if filtered_products != []:
				products = products.filter(id__in=filtered_products, store=store)

			if selected_price_range != None and filtered_products == []:
				products = []
			categories = Category.objects.filter(store=store)
			store = Store.objects.get(name=store_name)
			products_urls = f'{current_app_name}:product_detail'
			sizes = Size.objects.all()
			price_ranges = PriceRange.objects.all()
			brands = Brand.objects.filter(store=store)
			if brand != '0':
				selected_brand = Brand.objects.get(id=brand)
			else:
				selected_brand = None

			my_forms = []
			if category != '0':
				selected_category = Category.objects.filter(id = int(category)).first()
				filters = Filter.objects.filter(store=store)
				for filter in filters:
					values = filter.value.all()
					class FeatureFilterForm(forms.Form):
						name = filter.name
						choices = tuple([(value.value, value.value) for value in values])
						فیلترها = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple)
					new_form = FeatureFilterForm
					my_forms.append(new_form)
				category = Category.objects.get(slug = selected_category.slug, store=store)
				filters = Filter.objects.filter(category=category, store=store)
			else:
				selected_category = None

			selected_values = []
			active_filters = []
			for key, value in request.session.items():
				if key.startswith('filter-'):
					
					filter_name = key.replace('filter-', '')
					selected_filter = Filter.objects.get(store = store, name = filter_name)
					for posi_value in selected_filter.value.all():
						if posi_value.value in value:
							new_active_filter = {'filter':selected_filter,'value':posi_value}
							active_filters.append(new_active_filter)
							selected_values.append(posi_value.id)

			paginator = Paginator(products, 12)
			page = request.GET.get('page', 1)
			try:
				products = paginator.page(page)
			except PageNotAnInteger:
				# اگر شماره صفحه یک عدد نیست
				products = paginator.page(1)
			except EmptyPage:
				# اگر شماره صفحه بیشتر از تعداد کل صفحات است
				products = paginator.page(paginator.num_pages)

			return render(request, f'{current_app_name}/product_list_{store.template_index}.html', 
				 {'products': products, 
				'brands':brands,
				'to_products':products_urls, 
				'store_name':store_name, 
				'categories':categories,
				'sizes':sizes,
				'price_ranges':price_ranges,
				'selected_brand':selected_brand,
				'selected_price_range':selected_price_range,
				'selected_category':selected_category,
				'filters':filters,
				'category':selected_category,
				'my_forms':my_forms,
				'active_filters':active_filters,
				'main_filters': main_filters,
				'main_selected_category' : product_cat,
				'main_selected_brand' : selected_brand,
				'main_selected_price_range' : selected_price_range})
					
		return render(request, f'{current_app_name}/product_list_{store.template_index}.html', {'store_name':store_name})

class TagListCreateView(IsOwnerUserMixin ,View):

	template_name = f'{current_app_name}/owner-dashboard-tag.html'

	def get(self, request, *args, **kwargs):
		form = TagForm
		store = Store.objects.get(name=store_name)
		tags = Tag.objects.filter(store=store)
		create_tag_url = 'shop:owner_dashboard_tag'
		edit_tag_url = 'shop:edit_tag'
		return render(request, self.template_name, {'edit_tag_url':edit_tag_url,
													'create_tag_url':create_tag_url,
													'form': form, 
													'tags':tags,
													'store_name':store_name})

	def post(self, request, *args, **kwargs):
		form = TagForm(request.POST)
		if form.is_valid():
			store = Store.objects.get(name=store_name)
			tag = Tag.objects.create(
				store = store,
				name = form.cleaned_data['name'],
				slug = form.cleaned_data['slug'],
				is_special = form.cleaned_data['is_special']
			)
			tags = Tag.objects.filter(store=store)
			create_tag_url = f'{current_app_name}:tag-list-and-create'
			edit_tag_url = f'{current_app_name}:edit_tag'
			return redirect(f'{current_app_name}:owner_dashboard_tag')
		create_tag_url = f'{current_app_name}:tag-list-and-create'
		edit_tag_url = f'{current_app_name}:edit_tag'
		return render(request, self.template_name, {'edit_tag_url':edit_tag_url,
													'create_tag_url':create_tag_url,
													'form': form, 
													'tags':tags,
													'store_name':store_name})

class TagEditView(IsOwnerUserMixin ,View):

	def post(self, request, pk, *args, **kwargs):
		tag = get_object_or_404(Tag, pk=pk)
		form = TagForm(request.POST)
		if form.is_valid():
			tag.is_special = form.cleaned_data['is_special']
			tag.save()
			return redirect('shop:owner_dashboard_tag') 
		store = Store.objects.filter(name = store_name).first()
		tagss = Delivery.objects.filter(store=store)
		create_tag_url = f'{current_app_name}:tag-list-and-create'
		edit_tag_url = f'{current_app_name}:edit_tag'
		return render(request, self.template_name, {'edit_tag_url':edit_tag_url,
													'create_tag_url':create_tag_url,
													'form': form, 
													'tag':tag,
													'store_name':store_name})

class TagDeleteView(IsOwnerUserMixin, View):
		
	def get(self, request, pk, *args, **kwargs):
		tag = Tag.objects.get(pk=pk)
		tag.delete()
		return redirect(f'{current_app_name}:owner_dashboard_tag')

class DeleteCategoryGroupView(View):

	def post(self, request, *args, **kwargs):
		form = CategorySelectForm(request.POST)
		selected_categories = request.POST.getlist('category_select')
		for id in selected_categories:
			category = Category.objects.get(id=id)
			category.delete()
		return redirect(f'{current_app_name}:owner_dashboard_categories' )

class SetMerchantCodeView(View):

	def post(self, request):

		store = Store.objects.get(name = store_name)
		form = MerchantCodeForm(request.POST)
		if form.is_valid():
			store.merchant = form.cleaned_data['merchant_code']
			store.save()
			return redirect('shop:owner_dashboard_store_update')
		return render(request, 'shop/owner-dashboard-store-settings.html',
		{
			'wrong_merchant_message': 'ورودی نا معتبر',
			'store': store
		})





