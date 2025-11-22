from django.contrib import admin
from .models import Aluno, Professor, HistoricoMonografia, HistoricoBanca

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('user', 'matricula')  # mostra o usuário e a matrícula

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('user', 'titulação', 'area_pesquisa')  # mostra o usuário e os campos

@admin.register(HistoricoMonografia)
class HistoricoMonografiaAdmin(admin.ModelAdmin):
    list_display = ('monografia', 'tipo_alteracao', 'usuario', 'data_alteracao')
    list_filter = ('tipo_alteracao', 'data_alteracao')
    search_fields = ('monografia__titulo', 'usuario__username')
    readonly_fields = ('data_alteracao',)

@admin.register(HistoricoBanca)
class HistoricoBancaAdmin(admin.ModelAdmin):
    list_display = ('banca', 'tipo_alteracao', 'usuario', 'data_alteracao')
    list_filter = ('tipo_alteracao', 'data_alteracao')
    search_fields = ('banca__monografia__titulo', 'usuario__username')
    readonly_fields = ('data_alteracao',)