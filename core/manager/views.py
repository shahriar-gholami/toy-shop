from django.shortcuts import render, redirect
from django.views import View
from manager.models import ContactMessage
from manager.forms import ContactUsForm

# Create your views here.
class ContactView(View):
	
	template_name = 'contact.html'

	def post(self, request, *args, **kwargs):
		form = ContactUsForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			familly_name = form.cleaned_data['familly_name']
			email = form.cleaned_data['email']
			phone = form.cleaned_data['phone']
			subject = form.cleaned_data['subject']
			message_text = form.cleaned_data['message_text']

			new_message = ContactMessage.objects.create(
				name = name,
				familly_name=familly_name,
				email=email,
				phone=phone,
				subject=subject,
				message=message_text
			)
		return redirect('contact')