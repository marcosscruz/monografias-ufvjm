from rest_framework import viewsets, permissions, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.http import FileResponse
from datetime import datetime
from .models import Professor, Monografia, Banca, HistoricoMonografia, HistoricoBanca
from .pdf_templates.ata_defesa import gerar_ata_defesa
from .graficos import DashboardGraficos
from .serializers import (
    ProfessorSerializer, 
    MonografiaSerializer, 
    BancaSerializer,
    MonografiaCRUDSerializer,
    BancaCRUDSerializer,
    HistoricoMonografiaSerializer,
    HistoricoBancaSerializer
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
    ordering_fields = ['user__first_name', 'titulação', 'id']
    ordering = ['user__first_name']  # ordenação padrão

class MonografiaPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API pública de Monografias (leitura)
    
    - GET /api/monografias/ - Lista todas as monografias
    - GET /api/monografias/<id>/ - Detalhe de uma monografia
    """
    queryset = Monografia.objects.all()
    serializer_class = MonografiaSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['titulo', 'orientador__user__first_name', 
                     'orientador__user__last_name', 'palavras_chave', 'resumo']
    ordering_fields = ['titulo', 'criado_em', 'atualizado_em', 'orientador__user__first_name']
    ordering = ['-criado_em'] # recentes primeiro
    
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
    ordering_fields = ['titulo', 'criado_em', 'atualizado_em']
    ordering = ['-criado_em']

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
    ordering_fields = ['data', 'status', 'criado_em']
    ordering = ['-data']
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def gerar_ata(self, request, pk=None):
        """
        GET /api/bancas-crud/<id>/gerar-ata/
        """
        try:
            banca = self.get_object()
            # Gera o PDF
            pdf_buffer = gerar_ata_defesa(banca)
            
            # Retorna como download
            response = FileResponse(
                pdf_buffer,
                as_attachment=True,
                filename=f'ata_defesa_{banca.id}_{banca.monografia.titulo[:30]}.pdf',
                content_type='application/pdf'
            )
            return response
            
        except Banca.DoesNotExist:
            return Response(
                {'error': 'Banca não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erro ao gerar PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
# ========== VIEWSETS PARA HISTÓRICO ==========
class HistoricoMonografiaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API de Histórico de Monografias (leitura).
    
    Requer autenticação por token
    """
    queryset = HistoricoMonografia.objects.all()
    serializer_class = HistoricoMonografiaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ['data_alteracao', 'tipo_alteracao']
    ordering = ['-data_alteracao']
    filterset_fields = ['monografia', 'tipo_alteracao', 'usuario']

class HistoricoBancaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API de Histórico de Bancas (leitura).
    
    Requer autenticação por token
    """
    queryset = HistoricoBanca.objects.all()
    serializer_class = HistoricoBancaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ['data_alteracao', 'tipo_alteracao']
    ordering = ['-data_alteracao']
    filterset_fields = ['banca', 'tipo_alteracao', 'usuario']
    
# ========== ENDPOINT DASHBOARD ==========
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_graficos(request):
    """
    Endpoint que retorna todos os gráficos do dashboard em JSON.
    Authorization: Token seu_token_aqui
    """
    try:
        graficos = DashboardGraficos()
        
        # Gera todos os gráficos
        dados = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'graficos': {
                'monografias_por_ano': graficos.get_monografias_por_ano(),
                'monografias_por_area': graficos.get_monografias_por_area(),
                'status_defesas': graficos.get_status_defesas(),
                'notas_defesas': graficos.get_notas_defesas(),
                'defesas_proximas': graficos.get_defesas_proximas(dias=30),
                'professores_mais_ativos': graficos.get_professores_mais_ativos(),
            },
            'estatisticas': graficos.get_estatisticas_resumo(),
        }
        
        return Response(dados)
        
    except Exception as e:
        return Response(
            {'error': f'Erro ao gerar dashboard: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )