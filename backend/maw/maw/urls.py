"""maw URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.http import HttpResponse
from django.urls import path,re_path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


#import time 
#from WebApi import urls as web_api_urls

app_name= 'maw'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('Account.urls')),
    path('api/',include('Carrier.urls')),
    path('api/',include('Notification.urls')),
    path('api/',include('WebApi.urls')),
]

urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
urlpatterns+=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)

urlpatterns += [
    re_path(r'(?P<path>.*)',TemplateView.as_view(template_name='base.html')),
]


