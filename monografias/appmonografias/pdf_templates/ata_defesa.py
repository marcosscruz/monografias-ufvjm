from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
from io import BytesIO

def gerar_ata_defesa(banca):
    """
    Gera um PDF com a ata de defesa
    """
    
    # Criar buffer em memória
    buffer = BytesIO()
    
    # Criar documento PDF (A4)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )
    
    # Lista de elementos do PDF
    elementos = []
    
    # ========== ESTILOS ==========
    estilos = getSampleStyleSheet()
    
    estilo_titulo = ParagraphStyle(
        'TituloCustom',
        parent=estilos['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    estilo_subtitulo = ParagraphStyle(
        'SubtituloCustom',
        parent=estilos['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    estilo_normal = ParagraphStyle(
        'NormalCustom',
        parent=estilos['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#000000'),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    estilo_campo = ParagraphStyle(
        'CampoCustom',
        parent=estilos['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#000000'),
        spaceAfter=4,
        fontName='Helvetica'
    )
    
    # ========== CABEÇALHO ==========
    elementos.append(Paragraph("UNIVERSIDADE FEDERAL DOS VALES DO JEQUITINHONHA E MUCURI", estilo_titulo))
    elementos.append(Paragraph("Curso de Sistemas de Informação", estilo_titulo))
    elementos.append(Spacer(1, 0.5*cm))
    
    elementos.append(Paragraph("ATA DE DEFESA DE MONOGRAFIA", estilo_titulo))
    elementos.append(Spacer(1, 0.5*cm))
    
    # ========== DADOS GERAIS ==========
    elementos.append(Paragraph("<b>1. DADOS DA DEFESA</b>", estilo_subtitulo))
    
    # Tabela com dados
    dados_gerais = [
        ['Data da Defesa:', banca.data.strftime('%d/%m/%Y')],
        ['Horário:', banca.horario.strftime('%H:%M')],
        ['Local:', banca.local],
    ]
    
    tabela_dados = Table(dados_gerais, colWidths=[3*cm, 10*cm])
    tabela_dados.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elementos.append(tabela_dados)
    elementos.append(Spacer(1, 0.3*cm))
    
    # ========== DADOS DA MONOGRAFIA ==========
    elementos.append(Paragraph("<b>2. DADOS DA MONOGRAFIA</b>", estilo_subtitulo))
    
    monografia = banca.monografia
    
    dados_mono = [
        ['Título:', monografia.titulo],
        ['Autor:', monografia.autor.user.get_full_name()],
        ['Matrícula:', monografia.autor.matricula],
        ['Orientador:', monografia.orientador.user.get_full_name()],
    ]
    
    if monografia.coorientador:
        dados_mono.append(['Coorientador:', monografia.coorientador.user.get_full_name()])
    
    tabela_mono = Table(dados_mono, colWidths=[3*cm, 10*cm])
    tabela_mono.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elementos.append(tabela_mono)
    elementos.append(Spacer(1, 0.3*cm))
    
    # ========== BANCA AVALIADORA ==========
    elementos.append(Paragraph("<b>3. BANCA AVALIADORA</b>", estilo_subtitulo))
    
    professores_list = []
    for i, prof in enumerate(banca.professores_avaliadores.all(), 1):
        professores_list.append([f'Professor {i}:', prof.user.get_full_name()])
    
    if professores_list:
        tabela_prof = Table(professores_list, colWidths=[3*cm, 10*cm])
        tabela_prof.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(tabela_prof)
    
    elementos.append(Spacer(1, 0.3*cm))
    
    # ========== RESULTADO ==========
    elementos.append(Paragraph("<b>4. RESULTADO DA DEFESA</b>", estilo_subtitulo))
    
    status_map = {
        'AGENDADA': 'Agendada',
        'REALIZADA': 'Realizada',
        'CANCELADA': 'Cancelada',
    }
    
    dados_resultado = [
        ['Status:', status_map.get(banca.status, banca.status)],
    ]
    
    if banca.nota_final is not None:
        dados_resultado.append(['Nota Final:', f'{banca.nota_final} (0-100)'])
        
        # Determina se passou ou não
        se_aprovada = "APROVADA" if banca.nota_final >= 60 else "REPROVADA"
        dados_resultado.append(['Situação:', se_aprovada])
    
    tabela_resultado = Table(dados_resultado, colWidths=[3*cm, 10*cm])
    tabela_resultado.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#E8F4F8')),
    ]))
    elementos.append(tabela_resultado)
    elementos.append(Spacer(1, 1*cm))
    
    # ========== ASSINATURAS ==========
    elementos.append(Paragraph("<b>5. ASSINATURAS</b>", estilo_subtitulo))
    elementos.append(Spacer(1, 0.5*cm))
    
    # Linha para assinaturas
    assinaturas = []
    for prof in banca.professores_avaliadores.all():
        assinaturas.append(prof.user.get_full_name())
    
    if len(assinaturas) >= 3:
        # 3 colunas
        tabela_asinatura = Table([assinaturas[:3]], colWidths=[4.33*cm, 4.33*cm, 4.34*cm])
    elif len(assinaturas) == 2:
        # 2 colunas
        tabela_asinatura = Table([assinaturas], colWidths=[6.5*cm, 6.5*cm])
    else:
        # 1 coluna
        tabela_asinatura = Table([assinaturas], colWidths=[13*cm])
    
    tabela_asinatura.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 30),
    ]))
    elementos.append(tabela_asinatura)
    
    # Linhas para assinatura
    linhas_asinatura = []
    for _ in assinaturas:
        linhas_asinatura.append('_' * 20)
    
    tabela_linhas = Table([linhas_asinatura], colWidths=[13/len(assinaturas)*cm for _ in assinaturas])
    tabela_linhas.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    elementos.append(tabela_linhas)
    
    elementos.append(Spacer(1, 0.2*cm))
    
    # Nomes dos professores
    nomes_prof = []
    for prof in banca.professores_avaliadores.all():
        nomes_prof.append(prof.user.get_full_name())
    
    tabela_nomes = Table([nomes_prof], colWidths=[13/len(nomes_prof)*cm for _ in nomes_prof])
    tabela_nomes.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
    ]))
    elementos.append(tabela_nomes)
    
    elementos.append(Spacer(1, 1*cm))
    
    # ========== RODAPÉ ==========
    data_atual = datetime.now().strftime('%d/%m/%Y às %H:%M')
    elementos.append(Paragraph(
        f"<i>Documento gerado automaticamente em {data_atual}</i>",
        ParagraphStyle(
            'RodapeCustom',
            parent=estilos['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )
    ))
    
    # ========== BUILD DO PDF ==========
    doc.build(elementos)
    
    buffer.seek(0)
    return buffer