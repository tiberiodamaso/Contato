import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('core.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('cards/', include('cards.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('admin/', admin.site.urls),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if bool(int(os.environ.get('TOOLBAR', 1))):
  urlpatterns += [
    path('__debug__/', include('debug_toolbar.urls'))
  ]
