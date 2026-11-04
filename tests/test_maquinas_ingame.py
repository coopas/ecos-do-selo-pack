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


# --- Task 6: Saída de Vapor da caldeira do Create ------------------------------------------------------------------
# Posições = ECOS_MAQ_POS.caldeira_* / saida_* / tambor_* em maquinas_check.js. Caldeira = torre 1x1x8 de
# create:fluid_tank (y 301..308): tamanho 8 -> nível máximo 2 pelo tamanho; queimador superaquecido = calor 2.
QUEIMADOR = "create:blaze_burner[blaze=seething]{fuelLevel:2,burnTimeRemaining:20000}"
CALDEIRAS = {  # nome: (x, z, queimador?, bomba?, motor do Create?)
    "quente": (2, 13, True, True, False),
    "motores": (8, 13, True, True, True),
    "fria": (13, 13, False, False, False),
    "seca": (2, 9, True, False, False),
    "reserva": (7, 9, True, False, False),
}


@pytest.mark.ingame
def test_saida_vapor_ingame():
    """Caldeira do Create sem motor: a Saída entrega 6 mB/t de gtceu:steam por nível de calor (o mesmo limite de calor,
    tamanho e água que o Create usa para os motores) e gasta 10 mB de água por nível; com um motor a vapor do Create
    acoplado dá 0 (ou rotação, ou vapor); sem queimador ou sem água, 0."""
    montar, limpar = [], []
    for nome, (x, z, queimador, bomba, motor) in CALDEIRAS.items():
        if queimador:
            montar.append(f"setblock {x} 300 {z} {QUEIMADOR}")
        montar.append(f"fill {x} 301 {z} {x} 308 {z} create:fluid_tank")
        if bomba:  # tanque criativo -> bomba (gira por uma engrenagem ao lado, motor criativo) -> caldeira
            montar += [f"setblock {x - 2} 301 {z} create:creative_fluid_tank",
                       f"setblock {x - 1} 301 {z} create:mechanical_pump[facing=east]",
                       f"setblock {x - 2} 301 {z + 1} create:creative_motor[facing=east]{{ScrollValue:256}}",
                       f"setblock {x - 1} 301 {z + 1} create:cogwheel[axis=x]"]
            limpar += [f"setblock {x - 1} 301 {z + 1} minecraft:air", f"setblock {x - 2} 301 {z + 1} minecraft:air",
                       f"setblock {x - 1} 301 {z} minecraft:air", f"setblock {x - 2} 301 {z} minecraft:air"]
        if motor:
            montar.append(f"setblock {x} 304 {z - 1} create:steam_engine[face=wall,facing=north]")
            limpar.append(f"setblock {x} 304 {z - 1} minecraft:air")
        # a saída da quente entra com NBT vazio, como as saídas que já estão no mundo dos amigos
        nbt = "{}" if nome == "quente" else ""
        montar += [f"setblock {x + 1} 302 {z} ecosmaquinas:saida_vapor{nbt}",
                   f"setblock {x + 2} 302 {z} gtceu:steel_drum"]
        limpar += [f"setblock {x + 2} 302 {z} minecraft:air", f"setblock {x + 1} 302 {z} minecraft:air",
                   f"fill {x} 301 {z} {x} 308 {z} minecraft:air", f"setblock {x} 300 {z} minecraft:air"]
    montar.append("setblock 12 302 9 ecosmaquinas:saida_vapor{Nivel:99,Producao:-5,Estado:42}")  # NBT adulterado
    limpar.append("setblock 12 302 9 minecraft:air")
    console = _rodar(AREA + montar + ["kubejs custom_command ecos_saida_check"] + _esperar(20) + limpar + FIM)
    c = _campos(_linha(console, "ECOS_SAIDA"))
    assert c["nivel"] == 2, c  # min(calor 2, tamanho 8/4, água bombeada)
    assert c["mb_t"] == 6 * c["nivel"], c
    assert c["com_motores_mb_t"] == 0, c
    assert c["fria_mb_t"] == 0, c
    e = _campos(_linha(console, "ECOS_SAIDA_EXTRA"))
    assert e["seca_mb_t"] == 0, e
    assert e["calc_quente"] == 12 and e["calc_motores"] == 0, e
    # a caldeira com motor estava viva (motor contado, com calor): o 0 é o modo exclusivo, não falta de calor
    assert e["motores_engines"] == 1 and e["motores_calor"] >= 1, e
    assert e["agua_fria"] == 8000 and e["agua_fria_resta"] == 8000, e  # sem calor não gasta água
    # 1 000 mB de água = 100 níveis-tick = 600 mB de vapor, e depois para
    assert e["reserva_agua_entrou"] == 1000, e
    assert e["reserva_vapor"] == 600 and e["reserva_agua_resta"] == 0 and e["reserva_mb_t"] == 0, e
    assert e["ruim_nivel"] == 0 and e["ruim_mb_t"] == 0, e


# --- Task 7: o ciclo inteiro perde energia ------------------------------------------------------------------------
# Posições = ECOS_MAQ_POS.ciclo_* em maquinas_check.js. Caldeira 2x2x8 (x 8..9, z 2..3, y 301..308): tamanho 32 ->
# nível máximo 8; quatro queimadores superaquecidos = calor 8 -> a Saída dá 48 mB/t. O motor queima os 48 mB/t e dá
# 24 x 48 = 1152 SU a 32 RPM; o dínamo LV pede 32 SU/RPM x 32 = 1024 SU e gera 32 x 32 / 64 = 16 EU/t.
CICLO_SAIDA, CICLO_MOTOR, CICLO_DINAMO, CICLO_BUFFER = "10 302 2", "11 302 2", "11 303 2", "11 304 2"


@pytest.mark.ingame
def test_ciclo_perde_energia_ingame():
    """Saída de Vapor -> Motor a Vapor -> Dínamo LV -> buffer do GregTech: em 600 ticks, o EU entregue no buffer é no
    máximo 75 % do que o vapor consumido valeria numa máquina do GregTech (2 mB de vapor = 1 EU). Não há moto-contínuo."""
    montar = [f"setblock {x} 300 {z} {QUEIMADOR}" for x in (8, 9) for z in (2, 3)]
    montar += ["fill 8 301 2 9 308 3 create:fluid_tank",
               f"setblock {CICLO_SAIDA} ecosmaquinas:saida_vapor",
               f"setblock {CICLO_MOTOR} ecosmaquinas:motor_vapor[facing=up]",
               f"setblock {CICLO_DINAMO} ecosmaquinas:dinamo_cinetico_lv[facing=down]",
               f"setblock {CICLO_BUFFER} gtceu:lv_battery_buffer_4x[facing=north]"]
    limpar = [f"setblock {p} minecraft:air" for p in (CICLO_BUFFER, CICLO_DINAMO, CICLO_MOTOR, CICLO_SAIDA)]
    limpar += ["fill 8 301 2 9 308 3 minecraft:air", "fill 8 300 2 9 300 3 minecraft:air"]
    console = _rodar(AREA + montar + ["kubejs custom_command ecos_ciclo_check"] + _esperar(50) + limpar + FIM)
    c = _campos(_linha(console, "ECOS_CICLO"))
    e = _campos(_linha(console, "ECOS_CICLO_EXTRA"))
    assert c["ticks"] == 600, c
    assert c["eu"] > 0, (c, e)  # a corrente funciona de ponta a ponta (sem isso o <= passaria com tudo parado)
    assert c["vapor_mb"] > 0, (c, e)
    assert c["eu"] <= 0.75 * c["vapor_mb"] / 2, (c, e)  # perde pelo menos 25 %
    # a medição é a do circuito esperado: nível 8, motor a 32 RPM, dínamo LV sem sobrecarga
    assert e["nivel"] == 8 and e["rpm"] == 32 and e["sobrecarga"] is False, e
    # o vapor somado tick a tick bate com a água que a caldeira perdeu (10 mB de água por 6 mB de vapor)
    assert abs(e["agua_gasta"] * 6 / 10 - e["vapor_entregue"]) <= 6, e
