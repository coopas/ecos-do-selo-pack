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

# Ruído conhecido e inofensivo. Cada entrada precisa de comentário com o porquê.
IGNORE_PATTERNS: list[str] = []

_fatal = re.compile("|".join(FATAL_PATTERNS))
_ignore = re.compile("|".join(IGNORE_PATTERNS)) if IGNORE_PATTERNS else None


def scan(text: str) -> list[str]:
    problems = []
    for line in text.splitlines():
        if _fatal.search(line) and not (_ignore and _ignore.search(line)):
            line = line.strip()
            if line not in problems:
                problems.append(line)
    return problems
