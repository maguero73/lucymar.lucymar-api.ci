from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

VERSION = Path("version.txt").read_text().strip()


@router.get("/api/version")
def obtener_version():
    return {
        "version": VERSION
    }