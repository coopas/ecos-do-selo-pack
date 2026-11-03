"""Serializador SNBT mínimo (formato de texto NBT do Minecraft / FTB Quests)."""
import re

_PLAIN_KEY = re.compile(r"^[A-Za-z0-9_\-.+]+$")


class Long(int):
    """Inteiro serializado com sufixo L."""


class Byte(int):
    """Inteiro serializado com sufixo b."""


class Float(float):
    """Float serializado com sufixo f (NBT float; FTB lê pesos com getFloat)."""


def _str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _key(k: str) -> str:
    return k if _PLAIN_KEY.match(k) else _str(k)


def dumps(value, indent: int = 0) -> str:
    pad, inner = "\t" * indent, "\t" * (indent + 1)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, Long):
        return f"{int(value)}L"
    if isinstance(value, Byte):
        return f"{int(value)}b"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, Float):
        return f"{float(value)!r}f"
    if isinstance(value, float):
        return f"{value!r}d"
    if isinstance(value, str):
        return _str(value)
    if isinstance(value, dict):
        if not value:
            return "{ }"
        body = "\n".join(f"{inner}{_key(k)}: {dumps(value[k], indent + 1)}" for k in sorted(value))
        return "{\n" + body + "\n" + pad + "}"
    if isinstance(value, (list, tuple)):
        if not value:
            return "[ ]"
        body = "\n".join(f"{inner}{dumps(v, indent + 1)}" for v in value)
        return "[\n" + body + "\n" + pad + "]"
    raise TypeError(f"tipo não suportado em SNBT: {type(value)!r}")
