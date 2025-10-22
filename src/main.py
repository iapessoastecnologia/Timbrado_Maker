import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from api_process import gerar_pdf_timbrado

# ===========================================
# 🔹 1. Carregar variáveis do .env
# ===========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")  # .env está um nível acima de /src

load_dotenv(dotenv_path=ENV_PATH)

# ===========================================
# 🔹 2. Configurações vindas do .env
# ===========================================
APP_NAME = os.getenv("APP_NAME", "API Timbrar")
PORT = int(os.getenv("PORT", 55503))
TIMBRADO_PDF = os.getenv("TIMBRADO_PATH", os.path.join(BASE_DIR, "timbrado", "timbrado.pdf"))

# ===========================================
# 🔹 3. Inicializar aplicação FastAPI
# ===========================================
app = FastAPI(title=APP_NAME)


@app.get("/")
def home():
    """Verifica se a API está online."""
    return {
        "status": "✅ API de Timbragem ativa e funcionando!",
        "porta": PORT,
        "timbrado_pdf": TIMBRADO_PDF,
    }


@app.post("/timbrar")
async def timbrar_pdf(arquivo: UploadFile = File(...)):
    """
    Recebe um arquivo .txt, aplica o timbrado fixo e retorna o PDF pronto.
    """
    if not os.path.exists(TIMBRADO_PDF):
        return {"erro": "❌ Timbrado padrão não encontrado em /timbrado."}

    if not arquivo.filename.lower().endswith(".txt"):
        return {"erro": "❌ Apenas arquivos .txt são aceitos."}

    # Cria pasta temporária
    pasta_temp = tempfile.mkdtemp()
    caminho_txt = os.path.join(pasta_temp, arquivo.filename)

    with open(caminho_txt, "wb") as f:
        shutil.copyfileobj(arquivo.file, f)

    # Gera PDF timbrado
    pdf_gerado = gerar_pdf_timbrado(caminho_txt, TIMBRADO_PDF)

    # Retorna o PDF
    return FileResponse(
        pdf_gerado,
        media_type="application/pdf",
        filename=os.path.splitext(arquivo.filename)[0] + "_timbrado.pdf"
    )


# ===========================================
# 🔹 4. Execução direta (modo debug local)
# ===========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)

