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


# --- Task 5: Dínamo Cinético (ULV e LV) ---------------------------------------------------------------------------
# Posições = ECOS_MAQ_POS.dinamo_* / buffer_* em maquinas_check.js: motor criativo y=300 (facing=up), dínamo y=301
# (facing=down: eixo embaixo, saída de EU em cima), gtceu:lv_battery_buffer_4x y=302.
DINAMOS = {  # x: (tier, RPM do motor criativo, NBT do dínamo)
    2: ("ulv", 64, "{}"),  # NBT vazio, como os dínamos que já estão no mundo dos amigos
    4: ("lv", 64, ""), 6: ("lv", 0, ""), 8: ("lv", -64, ""),
    10: ("ulv", 32, ""),  # lento: 8 SU/RPM x 32 / 64 = 4 EU/t (meio ampere em média)
    12: ("lv", 256, ""),  # rápido: 32 x 256 / 64 = 128 EU/t teóricos, mas no máximo 1 A de 32 V
}
DINAMO_Z = 6


@pytest.mark.ingame
def test_dinamo_ingame():
    """Rotação do Create vira EU do GregTech: EU/t = min(voltagem, impacto x |RPM| / 64), 1 A na voltagem da tier."""
    montar, limpar = [], []
    for x, (tier, rpm, nbt) in DINAMOS.items():
        montar += [f"setblock {x} 300 {DINAMO_Z} create:creative_motor[facing=up]{{ScrollValue:{rpm}}}",
                   f"setblock {x} 301 {DINAMO_Z} ecosmaquinas:dinamo_cinetico_{tier}[facing=down]{nbt}",
                   f"setblock {x} 302 {DINAMO_Z} gtceu:lv_battery_buffer_4x[facing=north]"]
        limpar += [f"setblock {x} {y} {DINAMO_Z} minecraft:air" for y in (302, 301, 300)]
    # NBT adulterado: buffer acima do máximo e negativo têm de ser corrigidos ao carregar
    montar += ["setblock 2 301 10 ecosmaquinas:dinamo_cinetico_lv[facing=down]{Buffer:999999L}",
               "setblock 4 301 10 ecosmaquinas:dinamo_cinetico_lv[facing=down]{Buffer:-5L}"]
    limpar += ["setblock 2 301 10 minecraft:air", "setblock 4 301 10 minecraft:air"]
    console = _rodar(AREA + montar + ["kubejs custom_command ecos_dinamo_check"] + _esperar(14) + limpar + FIM)
    c = _campos(_linha(console, "ECOS_DINAMO"))
    assert c["ulv_eu_t"] == 8, c
    assert c["lv_eu_t"] == 32, c
    assert c["parado_eu_t"] == 0, c
    assert c["reverso_eu_t"] == 32, c
    e = _campos(_linha(console, "ECOS_DINAMO_EXTRA"))
    assert e["reverso_rpm"] < 0, e  # o reverso gira mesmo ao contrário
    assert e["lento_eu_t"] == 4, e  # fração acumulada no buffer e entregue em pacotes de 8 V
    assert e["rapido_eu_t"] == 32 and e["rapido_calc"] == 32, e  # nunca mais que 1 A na voltagem da tier
    assert (e["ulv_calc"], e["lv_calc"], e["reverso_calc"]) == (8, 32, 32), e
    assert (e["ulv_v"], e["lv_v"]) == (8, 32), e
    assert e["saida_cap"] is True and e["eixo_sem_cap"] is True, e  # IEnergyContainer só na face de saída
    assert e["saida_out"] is True and e["saida_nao_aceita"] is True and e["saida_recusa"] is True, e
    assert e["buffer_max_lv"] == 16 * 32, e
    assert e["buffer_alto"] == 16 * 32 and e["buffer_neg"] == 0, e
