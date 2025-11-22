from rest_framework import viewsets, permissions, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Professor, Monografia, Banca
from .serializers import (
    ProfessorSerializer, 
    MonografiaSerializer, 
    BancaSerializer,
    MonografiaCRUDSerializer,
    BancaCRUDSerializer
)

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
    
class IsAdminOrReadOnly(permissions.BasePermission):
    """Apenas admin pode editar/deletar"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser

# ========== ENDPOINTS ESPECIAIS ==========
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def obter_token(request):
    """
    gerar/obter token de autenticação.
    
    POST /api/token/
    corpo: {"username": "seu_usuario", "password": "sua_senha"}
    
    resposta: {"token": "abc123..."}
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username e password são obrigatórios'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'error': 'Usuário não encontrado'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.check_password(password):
        return Response(
            {'error': 'Senha incorreta'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # cria ou obtém o token do usuário
    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user_id': user.id,
        'username': user.username
    })

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
    search_fields = ['titulo', 'orientador__user__first_name', 'orientador__user__last_name', 'palavras_chave']
    ordering_fields = ['titulo', 'criado_em']
    
# ========== VIEWSETS RESTRITOS (AUTENTICADOS) ==========
class MonografiaCRUDViewSet(viewsets.ModelViewSet):
    """
    API restrita de Monografias (CRUD completo).
    
    Requer autenticação por token!
    
    - GET /api/monografias-crud/ - Lista (apenas admin)
    - POST /api/monografias-crud/ - Criar nova
    - GET /api/monografias-crud/<id>/ - Detalhe
    - PUT /api/monografias-crud/<id>/ - Editar completo
    - PATCH /api/monografias-crud/<id>/ - Editar parcial
    - DELETE /api/monografias-crud/<id>/ - Deletar
    """
    queryset = Monografia.objects.all()
    serializer_class = MonografiaCRUDSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['titulo', 'orientador__user__first_name']
    ordering_fields = ['titulo', 'criado_em']

class BancaCRUDViewSet(viewsets.ModelViewSet):
    """
    API restrita de Bancas/Defesas (CRUD completo).
    
    requer autenticação por token
    
    - GET /api/bancas-crud/ - Lista (apenas admin)
    - POST /api/bancas-crud/ - Criar nova defesa
    - GET /api/bancas-crud/<id>/ - Detalhe
    - PUT /api/bancas-crud/<id>/ - Editar completo
    - PATCH /api/bancas-crud/<id>/ - Editar parcial (ex: adicionar nota)
    - DELETE /api/bancas-crud/<id>/ - Deletar
    """
    queryset = Banca.objects.all()
    serializer_class = BancaCRUDSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['monografia__titulo', 'status']
    ordering_fields = ['data', 'status']