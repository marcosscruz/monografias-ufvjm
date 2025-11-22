from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    ProfessorPublicViewSet, 
    MonografiaPublicViewSet,
    MonografiaCRUDViewSet,
    BancaCRUDViewSet,
    HistoricoMonografiaViewSet,
    HistoricoBancaViewSet,
    dashboard_graficos,
    obter_token
)

# Router automático
router = DefaultRouter()

# Endpoints PÚBLICOS
router.register(r'professores', ProfessorPublicViewSet, basename='professor-list')
router.register(r'monografias', MonografiaPublicViewSet, basename='monografia-list')

# Endpoints RESTRITOS (com autenticação)
router.register(r'monografias-crud', MonografiaCRUDViewSet, basename='monografia-crud')
router.register(r'bancas-crud', BancaCRUDViewSet, basename='banca-crud')

# Endpoints HISTÓRICO (com autenticação)
router.register(r'historico-monografias', HistoricoMonografiaViewSet, basename='historico-monografia')
router.register(r'historico-bancas', HistoricoBancaViewSet, basename='historico-banca')

urlpatterns = [
    path('token/', obter_token, name='obter-token'),
    path('dashboard-graficos/', dashboard_graficos, name='dashboard-graficos'),  # ← Adicione isto
    path('', include(router.urls)),
]