from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('guilherme-leal/', include('guilherme_leal.urls')),
]
