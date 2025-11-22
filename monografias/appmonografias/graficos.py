import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .models import Monografia, Banca

class DashboardGraficos:
    """Classe para gerar gráficos do dashboard"""
    
    @staticmethod
    def get_monografias_por_ano():
        """
        Retorna monografias agrupadas por ano de criação.
        Gráfico de barras.
        """
        # Agrupa por ano
        monografias = Monografia.objects.extra(
            select={'ano': 'EXTRACT(year FROM criado_em)'}
        ).values('ano').annotate(total=Count('id')).order_by('ano')
        
        anos = [str(int(m['ano'])) for m in monografias if m['ano']]
        totais = [m['total'] for m in monografias if m['ano']]
        
        fig = go.Figure(data=[
            go.Bar(
                x=anos,
                y=totais,
                marker=dict(color='#1f77b4'),
                text=totais,
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Monografias: %{y}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title='Monografias por Ano',
            xaxis_title='Ano',
            yaxis_title='Quantidade',
            template='plotly_white',
            hovermode='x unified',
            height=400,
            showlegend=False
        )
        
        return fig.to_html(div_id='graph_ano')
    
    @staticmethod
    def get_monografias_por_area():
        """
        Retorna monografias agrupadas por área de pesquisa do orientador.
        Gráfico de pizza.
        """
        # Agrupa por área de pesquisa
        areas = Monografia.objects.values('orientador__area_pesquisa').annotate(
            total=Count('id')
        ).order_by('-total')
        
        area_nomes = [a['orientador__area_pesquisa'] for a in areas if a['orientador__area_pesquisa']]
        area_totais = [a['total'] for a in areas if a['orientador__area_pesquisa']]
        
        fig = go.Figure(data=[
            go.Pie(
                labels=area_nomes,
                values=area_totais,
                hovertemplate='<b>%{label}</b><br>Monografias: %{value}<extra></extra>',
                textposition='inside',
                textinfo='label+percent'
            )
        ])
        
        fig.update_layout(
            title='Distribuição de Monografias por Área de Pesquisa',
            template='plotly_white',
            height=400,
        )
        
        return fig.to_html(div_id='graph_area')
    
    @staticmethod
    def get_status_defesas():
        """
        Retorna status das defesas/bancas.
        Gráfico de barras horizontal.
        """
        status_count = Banca.objects.values('status').annotate(
            total=Count('id')
        ).order_by('-total')
        
        status_map = {
            'AGENDADA': 'Agendada',
            'REALIZADA': 'Realizada',
            'CANCELADA': 'Cancelada',
        }
        
        status_labels = [status_map.get(s['status'], s['status']) for s in status_count]
        status_totais = [s['total'] for s in status_count]
        
        # Cores diferentes por status
        cores = {
            'Agendada': '#FFA500',
            'Realizada': '#28a745',
            'Cancelada': '#dc3545',
        }
        cores_list = [cores.get(label, '#808080') for label in status_labels]
        
        fig = go.Figure(data=[
            go.Bar(
                x=status_totais,
                y=status_labels,
                orientation='h',
                marker=dict(color=cores_list),
                text=status_totais,
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>Quantidade: %{x}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title='Status das Defesas',
            xaxis_title='Quantidade',
            yaxis_title='Status',
            template='plotly_white',
            height=350,
            showlegend=False,
            margin=dict(l=150)
        )
        
        return fig.to_html(div_id='graph_status')
    
    @staticmethod
    def get_notas_defesas():
        """
        Retorna distribuição de notas das defesas.
        Histograma.
        """
        bancas = Banca.objects.filter(nota_final__isnull=False).values_list('nota_final', flat=True)
        
        if not bancas:
            # Retorna gráfico vazio se não houver notas
            fig = go.Figure()
            fig.add_annotation(text='Nenhuma nota registrada ainda')
            fig.update_layout(title='Distribuição de Notas (0-100)')
            return fig.to_html(div_id='graph_notas')
        
        fig = go.Figure(data=[
            go.Histogram(
                x=list(bancas),
                nbinsx=10,
                marker=dict(color='#17a2b8'),
                hovertemplate='Nota: %{x}<br>Frequência: %{y}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title='Distribuição de Notas das Defesas',
            xaxis_title='Nota (0-100)',
            yaxis_title='Frequência',
            template='plotly_white',
            height=400,
            showlegend=False
        )
        
        return fig.to_html(div_id='graph_notas')
    
    @staticmethod
    def get_defesas_proximas(dias=30):
        """
        Retorna defesas programadas para os próximos N dias.
        Timeline simples.
        """
        hoje = datetime.now().date()
        proxima_data = hoje + timedelta(days=dias)
        
        defesas = Banca.objects.filter(
            status='AGENDADA',
            data__gte=hoje,
            data__lte=proxima_data
        ).order_by('data')
        
        # Prepara dados
        datas = [b.data.strftime('%d/%m') for b in defesas]
        monografias = [b.monografia.titulo[:40] + '...' if len(b.monografia.titulo) > 40 else b.monografia.titulo for b in defesas]
        horarios = [b.horario.strftime('%H:%M') for b in defesas]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=datas,
            y=monografias,
            mode='markers+text',
            marker=dict(size=12, color='#1f77b4'),
            text=horarios,
            textposition='top center',
            hovertemplate='<b>%{y}</b><br>Data: %{x}<br>Hora: %{text}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'Defesas Agendadas (Próximos {dias} dias)',
            xaxis_title='Data',
            yaxis_title='Monografia',
            template='plotly_white',
            height=400,
            hovermode='closest',
            showlegend=False
        )
        
        return fig.to_html(div_id='graph_proximas')
    
    @staticmethod
    def get_estatisticas_resumo():
        """
        Retorna estatísticas resumidas em texto/números.
        """
        total_monografias = Monografia.objects.count()
        total_defesas = Banca.objects.count()
        defesas_agendadas = Banca.objects.filter(status='AGENDADA').count()
        defesas_realizadas = Banca.objects.filter(status='REALIZADA').count()
        
        # Calcula média de notas
        notas = list(Banca.objects.filter(nota_final__isnull=False).values_list('nota_final', flat=True))
        media_notas = sum(notas) / len(notas) if notas else 0
        
        # Professores orientadores
        total_professores = Monografia.objects.values('orientador').distinct().count()
        
        # Monografias este ano
        hoje = datetime.now()
        monografias_este_ano = Monografia.objects.filter(
            criado_em__year=hoje.year
        ).count()
        
        return {
            'total_monografias': total_monografias,
            'total_defesas': total_defesas,
            'defesas_agendadas': defesas_agendadas,
            'defesas_realizadas': defesas_realizadas,
            'media_notas': round(media_notas, 2),
            'total_professores': total_professores,
            'monografias_este_ano': monografias_este_ano,
        }
    
    @staticmethod
    def get_professores_mais_ativos():
        """
        Retorna professores com mais orientações.
        Gráfico de barras.
        """
        professores = Monografia.objects.values(
            'orientador__user__first_name',
            'orientador__user__last_name'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:10]  # Top 10
        
        nomes = [f"{p['orientador__user__first_name']} {p['orientador__user__last_name']}" for p in professores]
        totais = [p['total'] for p in professores]
        
        fig = go.Figure(data=[
            go.Bar(
                x=nomes,
                y=totais,
                marker=dict(color='#2ca02c'),
                text=totais,
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Orientações: %{y}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title='Top 10: Professores Mais Ativos',
            xaxis_title='Professor',
            yaxis_title='Número de Orientações',
            template='plotly_white',
            height=400,
            showlegend=False,
            xaxis_tickangle=-45
        )
        
        return fig.to_html(div_id='graph_professores')