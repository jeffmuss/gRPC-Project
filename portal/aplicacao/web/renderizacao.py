from pathlib import Path

from fastapi.templating import Jinja2Templates


WEB_DIR = Path(__file__).resolve().parent
DIRECTORIO_MODELOS = WEB_DIR / "modelos"
DIRECTORIO_ESTATICOS = WEB_DIR / "estaticos"
modelos = Jinja2Templates(directory=DIRECTORIO_MODELOS)
