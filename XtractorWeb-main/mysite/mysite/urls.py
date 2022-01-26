"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static

from uploadapp import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('books/upload/', views.upload_book, name='upload_book'),
    path('books/upload/rows', views.upload_book_rows, name='upload_book_rows'),
    path('books/upload/columns', views.upload_book_columns, name='upload_book_columns'),
    path('books/download', views.download_book, name='download_book'),
    path('export', views.export_csv, name='export_csv'),

    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
