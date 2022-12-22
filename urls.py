"""attempt2hometheater URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('get-current-movie/<movie_id>', views.get_current_movie, name='get-current-movie'),
    path('', views.index, name='index'),
    path('make-selection/<moviename>/', views.make_selection, name='make-selection'),
    path('selected/<movieid>', views.selected, name='selected'),
    path('admin/', admin.site.urls),
    path('admin-login/', views.admin_login, name='admin-login'),
    #path('poster-movieID/', views.poster_movieID, name='poster-movieID'),
    path('admin-accounts/', include("django.contrib.auth.urls")),
    path('accounts/', include('django.contrib.auth.urls')),
    #path('login/', views.login, name='login'),
]
