"""Procura erros graves em logs do Minecraft/Forge/KubeJS."""
import re

FATAL_PATTERNS = [
    r"for invalid dist",
    r"Missing or unsupported mandatory dependencies",
    r"Failed to create mod instance",
    r"/ERROR\] \[[^\]]*/LOADING\]",
    r"InvalidMixinException|MixinApplyError|Mixin apply .*failed",
    r"/ERROR\] \[KubeJS",
    r"Exception in server tick loop",
    r"Encountered an unexpected exception",
    r"---- Minecraft Crash Report ----",
    r"Failed to load datapacks, can't proceed with server load",
]

# RuÃ­do conhecido e inofensivo. Cada entrada precisa de comentÃ¡rio com o porquÃª.
IGNORE_PATTERNS: list[str] = []

_fatal = re.compile("|".join(FATAL_PATTERNS))
_ignore = re.compile("|".join(IGNORE_PATTERNS)) if IGNORE_PATTERNS else None


# O KubeJS (Rhino) inspeciona classes por reflexão e captura o erro de "invalid dist";
# o Forge loga o DISTXFORM imediatamente antes. O par é inofensivo; um DISTXFORM sozinho não é.
_RHINO_PROBE = "getDeclaredMethodsSafe"


def scan(text: str) -> list[str]:
    problems = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if _RHINO_PROBE in line:
            continue
        if "DISTXFORM" in line and i + 1 < len(lines) and _RHINO_PROBE in lines[i + 1]:
            continue
        if _fatal.search(line) and not (_ignore and _ignore.search(line)):
            line = line.strip()
            if line not in problems:
                problems.append(line)
    return problems
