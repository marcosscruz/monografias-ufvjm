from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_home_vue, name='api-home-vue'),
    # path('', views.home, name='home'),
        
    path('login/', views.api_login_vue, name='api-login-vue'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Monografias
    path('monografia/criar/', views.criar_monografia, name='criar_monografia'),
    path('monografia/listar/', views.listar_monografias, name='listar_monografias'),
    path('monografia/editar/<int:pk>/', views.editar_monografia, name='editar_monografia'),
    path('monografia/deletar/<int:pk>/', views.deletar_monografia, name='deletar_monografia'),

    # Alunos e Professores
    path('professor/criar/', views.criar_professor, name='criar_professor'),

    # Bancas (defesas)
    path('defesa/agendar/', views.agendar_defesa, name='agendar_defesa'),
    path('defesa/listar/', views.listar_defesas, name='listar_defesas'),
    path('defesa/gerenciar/<int:pk>/', views.gerenciar_defesa, name='gerenciar_defesa'),
    path('defesa/deletar/<int:pk>/', views.deletar_defesa, name='deletar_defesa'),
    
    # path('api-login-vue/', views.api_login_vue, name='api-login-vue'),
    # path('api-dashboard-vue/', views.api_dashboard_vue, name='api-dashboard-vue'),
]   
