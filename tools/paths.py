"""Caminhos centrais do projeto Ecos do Selo."""
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "pack"
BUILD = ROOT / "build"
CACHE = BUILD / "cache"
APPDATA = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
PRISM = APPDATA / "PrismLauncher"
JAVA17 = Path(os.environ.get("JAVA17", PRISM / "java" / "java-runtime-gamma" / "bin" / "java.exe"))
PACKWIZ = shutil.which("packwiz") or str(Path.home() / "go" / "bin" / "packwiz.exe")
