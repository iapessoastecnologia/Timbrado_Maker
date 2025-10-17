import os, re, tempfile
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter

def gerar_pdf_timbrado(txt_path, timbrado_pdf):
    """Gera um PDF timbrado único a partir de um arquivo TXT"""
    pasta_temp = tempfile.mkdtemp()
    temp_pdf = os.path.join(pasta_temp, "conteudo.pdf")
    pdf_saida = os.path.join(
        pasta_temp,
        os.path.splitext(os.path.basename(txt_path))[0] + "_timbrado.pdf"
    )

    # === FONTES ===
    try:
        pdfmetrics.registerFont(TTFont("Montserrat", os.path.join("fonts", "Montserrat-Regular.ttf")))
        pdfmetrics.registerFont(TTFont("Montserrat-Bold", os.path.join("fonts", "Montserrat-Bold.ttf")))
        FONT_NORMAL, FONT_BOLD = "Montserrat", "Montserrat-Bold"
    except:
        FONT_NORMAL, FONT_BOLD = "Helvetica", "Helvetica-Bold"

    # === CRIA PDF DE TEXTO ===
    doc = SimpleDocTemplate(
        temp_pdf,
        pagesize=A4,
        leftMargin=3 * cm,
        rightMargin=2 * cm,
        topMargin=4 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    style_normal = ParagraphStyle(
        "normal",
        parent=styles["Normal"],
        fontName=FONT_NORMAL,
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
    )
    style_bold = ParagraphStyle(
        "bold",
        parent=style_normal,
        fontName=FONT_BOLD,
    )
    style_title = ParagraphStyle(
        "title",
        parent=style_bold,
        fontSize=13,
        spaceAfter=10,
    )

    elementos = []
    with open(txt_path, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            elementos.append(Spacer(1, 10))
            continue
        if linha.startswith("###"):
            texto = linha.replace("###", "").strip()
            elementos.append(Paragraph(texto, style_title))
            continue

        linha = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", linha)
        elementos.append(Paragraph(linha, style_normal))

    doc.build(elementos)

    # === MESCLA COM O TIMBRADO ===
    if not os.path.exists(timbrado_pdf):
        raise FileNotFoundError("Timbrado padrão não encontrado em /timbrado.")

    timbrado = PdfReader(timbrado_pdf).pages[0]
    texto_pdf = PdfReader(temp_pdf)
    writer = PdfWriter()

    for page in texto_pdf.pages:
        fundo = timbrado
        fundo.merge_page(page)
        writer.add_page(fundo)

    with open(pdf_saida, "wb") as f_out:
        writer.write(f_out)

    return pdf_saida
