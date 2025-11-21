from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ProfessorPublicViewSet, MonografiaPublicViewSet

# rota automática - gera as rotas padrão
router = DefaultRouter()
router.register(r'professores', ProfessorPublicViewSet, basename='professor-list')
router.register(r'monografias', MonografiaPublicViewSet, basename='monografia-list')

urlpatterns = [
    path('', include(router.urls)),
]