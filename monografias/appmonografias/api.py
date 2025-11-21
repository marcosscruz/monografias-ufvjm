from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Professor, Monografia, Banca
from .serializers import ProfessorSerializer, MonografiaSerializer, BancaSerializer

# ========== PERMISSÕES ==========
class IsPublicRead(permissions.BasePermission):
    """
    permite acesso de leitura sem autenticação
    escerver requer autenticação
    """
    def has_permission(self, request, view):
        # se for GET, HEAD ou OPTIONS, permite sem autenticação
        if request.method in permissions.SAFE_METHODS:
            return True
        # do contrário, requer autenticação
        return request.user and request.user.is_authenticated


# ========== VIEWSETS ==========
class ProfessorPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API pública de Professores (leitura)
    
    - GET /api/professores/ - Lista todos os professores
    - GET /api/professores/<id>/ - Detalhe de um professor
    """
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'area_pesquisa']
    ordering_fields = ['user__first_name']

class MonografiaPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API pública de Monografias (leitura)
    
    - GET /api/monografias/ - Lista todas as monografias
    - GET /api/monografias/<id>/ - Detalhe de uma monografia
    
    filtros
    - ?search=titulo - Busca por título
    - ?search=orientador - Busca por nome do orientador
    """
    queryset = Monografia.objects.all()
    serializer_class = MonografiaSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['titulo', 'orientador__user__first_name', 
                     'orientador__user__last_name', 'palavras_chave']
    ordering_fields = ['titulo', 'criado_em']