from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('appmonografias.urls')),   # restante das rotas
    path('api/', include('appmonografias.urls_api')),  # Rotas da API
    path('accounts/', include('allauth.urls')),  # para as rotas login/logout do allauth
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)