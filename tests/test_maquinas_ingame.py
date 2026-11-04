"""Provas em jogo dos blocos do ecosmaquinas (Tasks 4-7).

Padrão para acrescentar um teste: monte a área com comandos (`setblock` dentro de `forceload add 0 0`), rode
`kubejs custom_command ecos_<algo>_check` (definido em pack/kubejs/server_scripts/dev/maquinas_check.js), espere,
leia a linha `ECOS_<ALGO> chave=valor ...` do console com `_linha()`/`_campos()` e limpe a área.
As posições de cada bloco ficam em `ECOS_MAQ_POS` no script dev; as daqui têm de bater com as de lá.
"""
import re

import pytest

AREA = ["forceload add 0 0"]
FIM = ["forceload remove 0 0"]


def _esperar(segundos: int) -> list[str]:
    """Cada comando de console espera 2 s pela saída (boot_test.drain); `say` só serve de relógio."""
    return ["say ECOS_WAIT"] * max(1, (segundos + 1) // 2)


def _rodar(comandos: list[str]) -> list[str]:
    import boot_test
    problems = boot_test.server(dev=True, console=comandos)
    assert problems == [], problems
    return list(boot_test.LAST_CONSOLE)


def _linha(console: list[str], marca: str) -> str:
    linhas = [l for l in console if f"{marca} " in l and "=" in l]
    assert linhas, (marca, console[-20:])
    return linhas[-1]


def _campos(linha: str) -> dict:
    """'ECOS_X a=1.0 b=true c=x' -> {'a': 1.0, 'b': True, 'c': 'x'}."""
    out = {}
    for k, v in re.findall(r"(\w+)=(\S+)", linha):
        if v in ("true", "false"):
            out[k] = v == "true"
        else:
            try:
                out[k] = float(v)
            except ValueError:
                out[k] = v
    return out


# --- Task 4: Motor a Vapor do Eco ---------------------------------------------------------------------------------
# Posições = ECOS_MAQ_POS.motor_cheio / motor_vazio / motor_agua em maquinas_check.js.
MOTOR_CHEIO, MOTOR_VAZIO, MOTOR_AGUA = "2 300 2", "6 300 2", "10 300 2"


@pytest.mark.ingame
def test_motor_vapor_ingame():
    """Motor com 8 000 mB de gtceu:steam gira a 32 RPM e dá 24 SU/mB x 80 mB/t = 1920 SU; o motor sem vapor
    (colocado com NBT vazio, como os que já estão no mundo dos amigos) fica parado e recusa água."""
    montar = [f"setblock {MOTOR_CHEIO} ecosmaquinas:motor_vapor[facing=up]",
              "setblock 2 301 2 create:shaft[axis=y]",
              f"setblock {MOTOR_VAZIO} ecosmaquinas:motor_vapor[facing=up]{{}}",
              # NBT adulterado: água no tanque não pode girar o motor
              f'setblock {MOTOR_AGUA} ecosmaquinas:motor_vapor[facing=up]{{Tanque:{{FluidName:"minecraft:water",Amount:5000}}}}']
    limpar = [f"setblock {p} minecraft:air" for p in ("2 301 2", MOTOR_CHEIO, MOTOR_VAZIO, MOTOR_AGUA)]
    console = _rodar(AREA + montar + ["kubejs custom_command ecos_motor_check"] + _esperar(4) + limpar + FIM)
    c = _campos(_linha(console, "ECOS_MOTOR"))
    assert c["cheio_rpm"] == 32, c
    assert c["su"] == 24 * 80, c
    assert c["mb_t"] == 80, c
    assert c["vazio_rpm"] == 0, c
    assert c["agua_recusada"] is True, c
    extra = _campos(_linha(console, "ECOS_MOTOR_EXTRA"))
    assert extra["vapor_entrou"] == 8000, extra  # o tanque aceitou os 8 000 mB pela capability
    assert extra["vapor_aceito_sim"] == 1000, extra  # contraprova da água: o motor vazio aceitaria vapor
    assert extra["eixo_sem_cap"] is True, extra  # a face do eixo não recebe fluido
    assert extra["dreno_recusado"] is True, extra  # cano não puxa o vapor de volta
    assert extra["agua_nbt_rpm"] == 0 and extra["agua_nbt_limpa"] is True, extra  # NBT com água: descarta, não gira
    assert 0 < extra["vapor_restante"] < 8000, extra  # consumiu de verdade
    assert extra["nbt_tanque"] is True, extra  # o tanque vai para o NBT
