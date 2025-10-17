from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from api_process import gerar_pdf_timbrado
import os, shutil, tempfile

app = FastAPI(title="API de Timbragem de PDFs")

# Caminho fixo do timbrado
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TIMBRADO_PDF = os.path.join(BASE_DIR, "timbrado", "timbrado.pdf")

@app.get("/")
def home():
    return {"status": "✅ API de Timbragem ativa e funcionando!"}


@app.post("/timbrar")
async def timbrar_pdf(arquivo: UploadFile = File(...)):
    """
    Recebe um arquivo .txt, aplica o timbrado fixo e retorna o PDF pronto.
    """
    if not os.path.exists(TIMBRADO_PDF):
        return {"erro": "❌ Timbrado padrão não encontrado em /timbrado."}

    # Garante que é .txt
    if not arquivo.filename.lower().endswith(".txt"):
        return {"erro": "❌ Apenas arquivos .txt são aceitos."}

    # Cria pasta temporária
    pasta_temp = tempfile.mkdtemp()
    caminho_txt = os.path.join(pasta_temp, arquivo.filename)

    with open(caminho_txt, "wb") as f:
        shutil.copyfileobj(arquivo.file, f)

    # Gera PDF timbrado
    pdf_gerado = gerar_pdf_timbrado(caminho_txt, TIMBRADO_PDF)

    # Retorna PDF diretamente
    return FileResponse(
        pdf_gerado,
        media_type="application/pdf",
        filename=os.path.splitext(arquivo.filename)[0] + "_timbrado.pdf"
    )
