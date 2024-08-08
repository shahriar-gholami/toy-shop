"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from . import views
from .sitemaps import StoreSitemap, ProductSitemap, CategorySitemap, BlogPostSitemap, ProductImageSitemap, CategoryImageSitemap
from django.views.generic import TemplateView

sitemaps = {
    'stores': StoreSitemap,
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'blog posts': BlogPostSitemap,
    'product images': ProductImageSitemap,
    'category images': CategoryImageSitemap,
}

from . import views

urlpatterns = [
    # path('', domain_redirect, name='domain_redirect'),
    path('',views.IndexView.as_view(),name='index'),
    path('subscribe',views.SubscribeView.as_view(),name='subscribe'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<str:product_slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('blog/', views.BlogView.as_view(), name='blog'),
    path('blog/<str:post_slug>/', views.BlogPostDetailView.as_view(), name='post_detail'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('templates/', views.TemplatesView.as_view(), name='templates'),
    path('policies/', views.PoliciesView.as_view(), name='rules_and_policies'),
    path('faq/', views.FaqView.as_view(), name='faq'),
    path('demos/', views.DemoRedirectView.as_view(), name='demos'),
    path('admin/', admin.site.urls),
    # path("api-auth/", include("rest_framework.urls")),
    path("accounts/", include("accounts.urls")),
    path("shop/", include("shop.urls")),
    path("manager/", include("manager.urls")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

# serving static and media for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
