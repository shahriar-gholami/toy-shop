from django.contrib.auth.mixins import UserPassesTestMixin
from urllib.parse import urlparse
from .models import Store, Owner, Customer

store_name ='فروشگاه اسباب بازی ایرانیان'

class IsOwnerUserMixin(UserPassesTestMixin):
	def test_func(self):
		if self.request.user.is_authenticated:
			current_path = self.request.path
			parsed_url = urlparse(current_path)
			path_segments = parsed_url.path.split('/')
			store_name = path_segments[2]
			store = Store.objects.get(id = 106)
			owner = Owner.objects.filter(phone_number = self.request.user.phone_number, store=store).first()
			if owner != None:
				return True
			return False
		return False
	
class IsCustomerUserMixin(UserPassesTestMixin):
	def test_func(self):
		if self.request.user.is_authenticated:
			current_path = self.request.path
			parsed_url = urlparse(current_path)
			path_segments = parsed_url.path.split('/')
			store_name = path_segments[2]
			store = Store.objects.get(name = store_name)
			customer = Customer.objects.filter(phone_number = self.request.user.phone_number, store=store).first()
			if customer != None:
				return True
			return False
		return False
