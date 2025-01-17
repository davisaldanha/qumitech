"""
URL configuration for quimitech project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from filters import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('register_filter/', views.filter_create, name='register_filter'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('signup/', views.signup_user, name='signup'),
    path('filters/', views.filter_list, name='filter_list'),
    path('filters/<int:pk>/', views.filter_detail, name='filter_detail'),
    path('filters/edit/<int:pk>/', views.filter_edit, name='filter_edit'),
    path('filters/delete/<int:pk>/', views.filter_delete, name='filter_delete'),
    path('export_filter_pdf/<int:pk>/', views.export_filter_pdf, name='export_filter_pdf')
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)