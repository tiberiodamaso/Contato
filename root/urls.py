from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('nois-tricota/', include('nois_tricota.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('bild/', include('bild.urls')),
]
