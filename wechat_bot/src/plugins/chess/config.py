from pathlib import Path
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    chess_engine_path: Path = Path("data/chess/stockfish.exe")
