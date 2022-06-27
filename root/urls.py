from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('guilherme_leal/', include('guilherme_boff.urls')),
]
