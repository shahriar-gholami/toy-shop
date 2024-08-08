from urllib.parse import urlparse
from .models import Category, Store, Owner
from django.contrib.auth.models import AnonymousUser



def base_template_context(request):

	for key, value in request.session.items():
		print (f'{key}:{value}')

	user_info = {}
	if request.user.is_authenticated:
		user_info = {
			'username': request.user.phone_number,
		}
	
	categories = None
	
	current_path = request.path
	parsed_url = urlparse(current_path)
	path_segments = parsed_url.path.split('/')
	second_segment = path_segments[1] if len(path_segments) > 2 else None
	third_segment = path_segments[2] if len(path_segments) > 3 else None
	
	
	
	
	if second_segment != 'diopars'and second_segment != 'viracoders' and third_segment != None and 'admin' not in path_segments and second_segment!='blog' and not path_segments[-2].startswith('09') and third_segment != 'orders':
		
		# category_ordered_list 
		print(third_segment)
		print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')

		store = Store.objects.get(name=third_segment)
		if 'temp_cat' in request.session:
			if request.session['temp_cat']:
				temp_category = Category.objects.get(name = request.session['temp_cat'], store=store)

				if 'category' in path_segments and temp_category.slug not in path_segments:
					for key in list(request.session.keys()):
						# بررسی آیا کلید با الگوی مورد نظر شروع می‌شود
						if key.startswith('filter-'):
							# پاک کردن کلید مربوطه
							del request.session[key]
							
							request.session.modified = True
					del request.session['temp_cat']
					
				if 'products' not in path_segments:
					for key in list(request.session.keys()):
						# بررسی آیا کلید با الگوی مورد نظر شروع می‌شود
						if key.startswith('filter-'):
							# پاک کردن کلید مربوطه
							del request.session[key]
							
							request.session.modified = True
					del request.session['temp_cat']

				if path_segments[-2] == 'products':
					for key in list(request.session.keys()):
						# بررسی آیا کلید با الگوی مورد نظر شروع می‌شود
						if key.startswith('filter-'):
							# پاک کردن کلید مربوطه
							del request.session[key]
							
							request.session.modified = True
					del request.session['temp_cat']

		# for key, value in request.session.items():
		# 	print (f'{key}:{value}')


		top_categories = Category.objects.filter(store=store)
		app_name = path_segments[1]
		store_name = path_segments[2]
		if isinstance(request.user, AnonymousUser):
			from shop.models import Product
			from shop.models import Variety
			varieties = Variety.objects.filter(store=store)
			products_id_list = []
			i = 0
			for variety in varieties:
				products_id_list.append(str(variety.id))
			for key, value in request.session.items():
				if key in products_id_list:
					i = i+1
			cart_url = f'{app_name}:customer_authentication'
			account_url = f'{app_name}:customer_authentication'
			return {
					'current_path': current_path,
					'second_segment': second_segment,
					'store_name':third_segment,
					'top_categories':top_categories,
					'cart_url':cart_url,
					'cart_items_count':i,
					'account_url':account_url,
					'store':store,
				}
		else:
			from shop.models import Cart
			from shop.models import Customer
			top_categories = Category.objects.filter(store=store)
			customer, create = Customer.objects.get_or_create(phone_number=request.user.phone_number, store=store)
			cart, create = Cart.objects.get_or_create(customer=customer, store=store)
			cart_items_count = cart.items.all().count()
			cart_url = f'{app_name}:cart_view'
			owner = Owner.objects.filter(phone_number = request.user.phone_number, store=store).first()
			if owner != None:
				account_url = f'{app_name}:owner_dashboard'
			else:
				account_url = f'{app_name}:customer_dashboard'
			return {
					'user_info': user_info,
					'current_path': current_path,
					'second_segment': second_segment,
					'store_name':third_segment,
					'top_categories':top_categories,
					'cart_url':cart_url,
					'cart':cart,
					'cart_items_count':cart_items_count,
					'account_url':account_url,
					'store':store,
				}        
	return user_info

	

# def categories_hierarchy(request):
# 	current_path = request.path
# 	parsed_url = urlparse(current_path)
	# categories = None
	# path_segments = parsed_url.path.split('/')
	# second_segment = path_segments[1] if len(path_segments) > 2 else None
	# third_segment = path_segments[2] if len(path_segments) > 3 else None
	# if third_segment != None and 'admin' not in path_segments and 'shop' in path_segments and not path_segments[-2].startswith('09') and third_segment != 'orders':
	# 	print('OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
	# 	store = Store.objects.get(name=third_segment)
	# 	categories = Category.objects.filter(store=store)
	# 	category_tree = {}

	# 	# ایجاد یک دیکشنری بر اساس والدین و زیرمجموعه‌ها
	# 	for category in categories:
	# 		if category.parent_id is None:
	# 			category_tree[category] = {'children': []}

	# 	for category in categories:
	# 		if category.parent_id is not None:
	# 			parent = Category.objects.get(pk=category.parent_id)
	# 			category_tree[parent]['children'].append(category)

	# 	return {'category_tree': category_tree}