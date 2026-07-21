import logging
import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fh = logging.FileHandler(LOG_DIR / f"{name}.log")
        fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(fh)
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        logger.addHandler(ch)
    return logger

def save_result(result, brief_text: str, filename: str = None) -> Path:
    if filename is None:
        filename = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = RESULTS_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({
            "brief": brief_text,
            "result": result.model_dump(mode='json')
        }, f, ensure_ascii=False, indent=2)
    print(f"💾 Результат сохранён в {filepath}")
    return filepath