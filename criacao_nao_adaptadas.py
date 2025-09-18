from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER
import tempfile
import io

# Estilo do texto nas etiquetas
paragraph_label_style = ParagraphStyle(
    'paragraph labels style', 
    fontSize=11,
    borderPadding=5,
    alignment=TA_CENTER
)

# Função para desenhar uma única etiqueta
def desenhar_etiqueta(c, x, y, largura, altura, tabela, logo, championship, stage):
    # Definir a cor da borda para branco
    c.setStrokeColorRGB(1, 1, 1)  # Branco
    
    # Desenho do retângulo da etiqueta
    c.rect(x, y, largura, altura)
    
    # Inserção do logo
    c.drawImage(logo, x + (1 * mm), y + altura - (14.9 * mm), width=(largura - (2 * mm)), height=(14.9 * mm))

# Texto da etiqueta
    p = Paragraph(f"""
        {championship} <br/>
        <b>{stage}</b> <br/>
        <b>ESCOLA: {tabela['NOME ESCOLA']}</b> <br/>
        <b>{tabela['ANO ESCOLAR']} PROVAS: {tabela['TOTAL']}</b>
    """, paragraph_label_style)
    
    # Ajuste do parágrafo dentro da etiqueta
    p.wrapOn(c, largura, altura - 60)
    p.drawOn(c, x, y + altura - 120)

    # Função principal para gerar o PDF com as etiquetas
def gerar_etiquetas(tabela, logo, championship, stage):
    buffer = io.BytesIO()
    largura_pagina, altura_pagina = A4
    largura_etiqueta = 99 * mm
    altura_etiqueta = 55 * mm  # Ajuste para altura exata
    margem_topo = 10 * mm
    margem_lateral = 5 * mm
    espaco_vertical = 3 * mm  # Espaço vertical entre as colunas
    
    # Configuração do PDF
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # Salvamento do logo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        tmpfile.write(logo.getbuffer())
        logo_path = tmpfile.name
    
    # Posições das colunas
    x_positions = [margem_lateral, largura_pagina / 2 + espaco_vertical / 2]
    y_position = altura_pagina - margem_topo - altura_etiqueta
    
    etiquetas_na_pagina = 0
    linha = 0
    etiqueta_positions = x_positions[0]
    
    # Loop  que executa para cada linha na tabela. Desenha a etiqueta na posicao 1 ou dois com base nos indices de x_position. Verifica se tem 10 etiquetas na pagina, se houver, finaliza a pagina e reseta as posicoes para comecar uma nova pagina.
    for index, row in tabela.iterrows():
        desenhar_etiqueta(c, etiqueta_positions, y_position, largura_etiqueta, altura_etiqueta, row, logo_path, championship, stage)
        etiquetas_na_pagina += 1
        if etiqueta_positions == x_positions[0]:
            etiqueta_positions = x_positions[1]
        elif etiqueta_positions == x_positions[1]:
            y_position = y_position - altura_etiqueta
            etiqueta_positions = x_positions[0]
        
        if etiquetas_na_pagina >= 10:
            c.showPage()
            y_position = altura_pagina - margem_topo - altura_etiqueta
            etiquetas_na_pagina = 0

    c.save()
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data