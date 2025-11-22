from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    ProfessorPublicViewSet, 
    MonografiaPublicViewSet,
    MonografiaCRUDViewSet,
    BancaCRUDViewSet,
    obter_token,
)

# rota automática - gera as rotas padrão
router = DefaultRouter()

# rotas públicas
router.register(r'professores', ProfessorPublicViewSet, basename='professor-list')
router.register(r'monografias', MonografiaPublicViewSet, basename='monografia-list')

# rotas restritas (autenticadas)
router.register(r'monografias-crud', MonografiaCRUDViewSet, basename='monografia-crud')
router.register(r'bancas-crud', BancaCRUDViewSet, basename='banca-crud')

urlpatterns = [
    path('token/', obter_token, name='obter-token'),
    path('', include(router.urls)),
]