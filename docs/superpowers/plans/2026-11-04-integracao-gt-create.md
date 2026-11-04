# Integração GregTech × Create × vanilla — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fazer GregTech CEu e Create funcionarem como um só: vapor ↔ rotação ↔ EU, combustíveis unificados com o Create: Diesel Generators, minérios do GregTech processados no Create e redstone cedo.

**Architecture:** Receitas, tags e unificação de fluidos em KubeJS, com dados gerados por Python a partir do dump de registro (padrão do pack: JSON em `pack/kubejs/ecos/` + script que falha alto). Os 3 blocos novos (Motor a Vapor, Dínamo Cinético, Saída de Vapor) num mod Java novo, `ecosmaquinas`, compilado como o `ecosbridge` (javac contra os jars do servidor). Provas em jogo por comandos `kubejs custom_command` em scripts `dev/` e testes `pytest -m ingame`.

**Tech Stack:** Forge 1.20.1 (47.4.28), Java 17, Create 6.0.8, GTCEu 7.5.3, Create: Diesel Generators 1.20.1-1.3.12, KubeJS 2001.6.5, Python 3 + pytest, packwiz.

**Spec:** `docs/superpowers/specs/2026-11-04-integracao-gt-create-design.md`

## Global Constraints
- Tudo visível ao jogador em PT-BR (nomes de blocos em `pt_br.json`; `en_us.json` com o mesmo texto em inglês simples).
- Todo ID (item, fluido, tag, bloco) validado contra `build/registry_dump.json`/`build/recipe_dump.json`; regenerar com `python tools/boot_test.py server --dev` depois de mudar mods/scripts.
- Nenhum laço vapor → rotação → EU → vapor pode render ≥ 100 %: perda mínima de 25 % no ciclo.
- Create nunca rende mais que o GregTech no minério (moer: 1 triturado + 30 %; macerador GT: 2 + subproduto).
- Mundo existente não pode quebrar: nada de remover blocos/itens já registrados; mods novos só adicionam.
- Motor e Dínamo craftáveis na era vapor/LV (nada de componente MV).
- Commits sem `Co-Authored-By` nem menção ao Claude (o hook do usuário prefixa a mensagem: não mexer). Push no repo público só pelo usuário.
- O servidor real dos amigos pode estar rodando nesta máquina na porta 25565: testes usam `boot_test` (porta 25570) e nunca matam processos `java` que não iniciaram.

## Review Focus
1. **Mundo já em andamento com o mod novo** — o servidor dos amigos atualiza por packwiz; um mod novo com bloco/BE que crasha ao carregar chunk derruba o servidor. Teste: Task 7 sobe o servidor com o mundo de `build/server` já existente (não um mundo novo) e o boot do cliente chega ao menu.
2. **Motor a Vapor sem vapor / com outro fluido** — deve parar de girar (0 RPM) e recusar fluido que não seja `gtceu:steam`. Teste em Task 4.
3. **Dínamo com rotação abaixo do mínimo ou girando ao contrário** — produz proporcional ao |RPM| (sentido não importa) e 0 EU parado; não pode dar EU negativo. Teste em Task 5.
4. **Saída de Vapor em caldeira com motores do Create acoplados** — não pode dar vapor e rotação ao mesmo tempo (seria energia de graça). Teste em Task 6.
5. **Combustível do CDG num gerador do GregTech e vice-versa** — os dois sentidos funcionam e com o mesmo EU por mB que o fluido equivalente do outro mod. Teste em Task 1.

---

### Task 1: Create: Diesel Generators + combustíveis unificados

**Files:**
- Modify: `tools/mods.csv` (linha `createdieselgenerators,mr,create-diesel-generators,both,core`)
- Modify: `pack/kubejs/server_scripts/dev/registry_dump.js` (acrescentar `fluid_tags` ao dump: tag → membros)
- Modify: `tools/registry.py` (`Registry.fluid_tag_fluids(tag: str) -> set[str]`, `has_fluid_tag(tag) -> bool`)
- Create: `pack/kubejs/ecos/fuels.json`
- Create: `pack/kubejs/server_scripts/15_ecos_fuels.js`
- Create: `pack/kubejs/server_scripts/dev/fuel_check.js`
- Test: `tests/test_fuels.py`

**Interfaces:**
- Produces: `fuels.json` = `{"fluid_tags": {"forge:diesel": ["gtceu:diesel"], "forge:gasoline": ["gtceu:gasoline", "gtceu:high_octane_gasoline"], "forge:biodiesel": ["gtceu:bio_diesel"], "forge:ethanol": ["gtceu:ethanol"], "forge:crude_oil": ["gtceu:oil", "ad_astra:oil"]}, "gt_combustion_clones": {"gtceu:diesel": "createdieselgenerators:diesel", "gtceu:gasoline": "createdieselgenerators:gasoline", "gtceu:bio_diesel": "createdieselgenerators:biodiesel", "gtceu:ethanol": "createdieselgenerators:ethanol"}, "gt_distillation_clones": {"gtceu:oil": "createdieselgenerators:crude_oil"}}`
- Produces: `Registry.fluid_tag_fluids`, usado pelas Tasks 2 e 7.

- [ ] **Step 1: Testes que falham** em `tests/test_fuels.py`:
  - `test_cdg_in_manifest`: `tools/mods.csv` tem `createdieselgenerators` com side `both`.
  - `test_fuels_ids_exist` (skip sem dump): todo fluido de `fuels.json` existe em `reg.fluids`; toda chave de `fluid_tags` existe como tag de fluido.
  - `test_fuel_tags_merged` (skip sem dump): `"gtceu:diesel" in reg.fluid_tag_fluids("forge:diesel")` e `"createdieselgenerators:diesel"` também (os dois mods na mesma tag); idem gasoline.
  - `test_fuel_crossing_ingame` (`@pytest.mark.ingame`): roda `kubejs custom_command ecos_fuel_check` e espera a linha `ECOS_FUEL receitas=<n> tags_ok=true missing=[]`, com `n` igual ao número de receitas `ecos:fuel/*` que `fuels.json` implica (4 de combustão + 1 por máquina de destilação clonada).
- [ ] **Step 2:** `python -m pytest tests/test_fuels.py -q` → FAIL (`createdieselgenerators` ausente / arquivo inexistente).
- [ ] **Step 3:** Adicionar a linha ao `mods.csv`, rodar `python tools/add_mods.py` e `python tools/check_manifest.py`.
- [ ] **Step 4:** `15_ecos_fuels.js`: `ServerEvents.tags('fluid', …)` adiciona os membros de `fluid_tags`; `ServerEvents.recipes`: para cada par de `gt_combustion_clones`, `event.forEachRecipe({type: 'gtceu:combustion_generator'}, r => …)` acha a receita cujo fluido de entrada é a chave e cria `ecos:fuel/<id>` com o JSON igual trocando o fluido (mesmo EU e duração); idem `gt_distillation_clones` para `gtceu:distillation_tower` e `gtceu:distillery`. Falha alto (`throw`) se `fuels.json` faltar ou se algum clone não achar a receita de origem.
- [ ] **Step 5:** `dev/fuel_check.js`: comando `ecos_fuel_check` confere via `RecipeManager` quais receitas `ecos:fuel/*` existem e se `Fluid.is(TagKey)` é verdadeiro para `gtceu:diesel`/`#forge:diesel` (a tag que o CDG lê em `fuel_type/diesel.json`); imprime `ECOS_FUEL receitas=<n> tags_ok=<bool> missing=[…]`.
- [ ] **Step 6:** `python tools/build_server.py && python tools/boot_test.py server --dev` → `0 problemas`; `python -m pytest -q` e `python -m pytest -q -m ingame tests/test_fuels.py` → PASS.
- [ ] **Step 7:** Commit `feat: Create Diesel Generators e combustíveis unificados com o GregTech`.

### Task 2: Minério do GregTech no Create, ligas e redstone cedo

**Files:**
- Create: `tools/gen_create_gt.py` (gera os dados a partir do dump)
- Create: `pack/kubejs/ecos/create_gt.json` (gerado; commitado)
- Create: `pack/kubejs/server_scripts/25_ecos_create_gt.js`
- Test: `tests/test_create_gt.py`

**Interfaces:**
- Consumes: `registry.load(path) -> Registry` (`has_item`, `tag_items`).
- Produces: `gen_create_gt.build(reg) -> dict` com chaves `crushing`, `splashing`, `pressing`, `mixing`, `gravel`; `gen_create_gt.write(reg, out: Path) -> int` (nº de receitas).

Regras (valores do spec):
- `crushing`: para cada `gtceu:raw_<m>` com `gtceu:crushed_<m>_ore` e `gtceu:purified_<m>_ore` no registro (107 hoje), entrada `#forge:raw_materials/<m>` → `gtceu:crushed_<m>_ore` ×1 + ×1 com chance 0.3. Sem subproduto.
- `splashing`: `gtceu:crushed_<m>_ore` → `gtceu:purified_<m>_ore` ×1.
- `pressing`: para cada material com `#forge:ingots/<m>` e `gtceu:<m>_plate`, sem receita `create:pressing` existente para o mesmo lingote → placa ×1.
- `mixing` (calor `heated`): bronze 3 cobre + 1 estanho → 4; liga de estanho 1 ferro + 1 estanho → 2; cuproníquel 1 cobre + 1 níquel → 2; invar 2 ferro + 1 níquel → 3; liga vermelha 1 cobre + 4 redstone → 1. Entradas por tag `forge:ingots/*`/`forge:dusts/redstone`; saídas `gtceu:<liga>_ingot`.
- `gravel`: substituir `create:crushing/gravel` por: `minecraft:gravel` → `minecraft:sand` ×1 + `minecraft:redstone` ×1 chance 0.1 (mantém as saídas atuais da receita; o gerador lê-as do `recipe_dump.json`).

- [ ] **Step 1: Testes que falham** em `tests/test_create_gt.py`:
  - `test_crushing_yield_below_gt`: com um `Registry` de fixture (raw_hematite, crushed/purified), `build()` dá `crushing` com saída principal count 1 e extra chance `0.3`.
  - `test_skips_material_without_purified`: `raw_rubber_dust` não gera receita.
  - `test_mixing_values`: bronze sai 4 de 3+1; liga vermelha 1 de 1+4.
  - `test_gravel_keeps_original_outputs_and_adds_redstone`: saída contém `minecraft:sand` e `{"item":"minecraft:redstone","chance":0.1}`.
  - `test_generated_file_ids_exist` (skip sem dump): todo id em `create_gt.json` existe; `len(crushing) >= 100`.
  - `test_create_gt_in_recipe_dump` (skip sem dump): após o boot dev, `recipe_dump.json` tem `create:crushing` com entrada `#forge:raw_materials/hematite` e `create:crushing/gravel` com saída `minecraft:redstone`.
- [ ] **Step 2:** rodar → FAIL (módulo não existe).
- [ ] **Step 3:** Implementar `gen_create_gt.py` (`build`, `write`, `main` que lê `build/registry_dump.json` e `build/recipe_dump.json` e escreve `pack/kubejs/ecos/create_gt.json`).
- [ ] **Step 4:** `25_ecos_create_gt.js`: lê o JSON (falha alto se faltar), registra `event.recipes.create.crushing/splashing/pressing/mixing(...)` com ids `ecos:create_gt/<tipo>/<m>`; para `gravel`, `event.remove({id: 'create:crushing/gravel'})` antes de recriar com id `ecos:create_gt/gravel`.
- [ ] **Step 5:** `python tools/gen_create_gt.py`, build + boot dev, `python -m pytest -q` → PASS; `python tools/questcheck.py` → `OK`.
- [ ] **Step 6:** Commit `feat: Create processa minérios do GregTech, ligas na batedeira e redstone do cascalho`.

### Task 3: Mod `ecosmaquinas` — esqueleto, build e registro dos blocos

**Files:**
- Create: `tools/ecosmaquinas/build.sh` (como `tools/ecosbridge/build.sh`; classpath = libs do Forge/MC + `build/server/mods/create-*.jar` + `gtceu-*.jar` + jars aninhados extraídos de `META-INF/jarjar` dos dois para `build/cache/jarjar/`; copia o jar para `pack/mods/ecosmaquinas-1.0.0.jar`)
- Create: `tools/ecosmaquinas/res/META-INF/mods.toml` (modId `ecosmaquinas`, dependências obrigatórias `create [6.0.8,6.1)`, `gtceu [7.5,)`, ordering AFTER)
- Create: `tools/ecosmaquinas/src/ecos/maquinas/EcosMaquinas.java` (registro de blocos, itens e block entities via `DeferredRegister`)
- Create: `tools/ecosmaquinas/res/assets/ecosmaquinas/{blockstates,models,textures,lang}/…` (`lang/pt_br.json`: "Motor a Vapor do Eco", "Dínamo Cinético (ULV)", "Dínamo Cinético (LV)", "Saída de Vapor")
- Create: `tools/ecosmaquinas/res/data/ecosmaquinas/{recipes,loot_tables}/…`
- Create: `tools/ecosmaquinas/gen_textures.py` (texturas 16×16 originais por PIL, sem copiar arte de outros mods)
- Test: `tests/test_ecosmaquinas.py`

**Interfaces:**
- Produces: ids `ecosmaquinas:motor_vapor`, `ecosmaquinas:dinamo_cinetico_ulv`, `ecosmaquinas:dinamo_cinetico_lv`, `ecosmaquinas:saida_vapor` (bloco e item); classes `ecos.maquinas.MotorVaporBlockEntity`, `DinamoBlockEntity`, `SaidaVaporBlockEntity` (corpos nas Tasks 4–6; aqui só existem e registram).
- Produces: `EcosMaquinas.Constantes` com `SU_POR_MB_VAPOR = 24`, `SU_POR_EU = 64`, `MOTOR_RPM = 32`, `MOTOR_MAX_MB_T = 80`, `SAIDA_MB_T_POR_NIVEL = 6`, `DINAMO_ULV_IMPACTO = 8`, `DINAMO_LV_IMPACTO = 32` (perda do ciclo: 2 mB → 1 EU; 2 mB → 48 SU → 0,75 EU).

- [ ] **Step 1: Testes que falham**: `test_jar_in_pack` (`pack/mods/ecosmaquinas-1.0.0.jar` existe e está no `index.toml`); `test_lang_pt` (4 nomes acima no `pt_br.json` dentro do jar); `test_recipes_era` (receitas dentro do jar não usam itens `gtceu:mv_*`/`hv_*` etc.); `test_blocks_registered` (skip sem dump: os 4 ids em `reg.items`); `test_constantes_perda` (lê `Constantes` do fonte Java por regex e confere `SU_POR_MB_VAPOR * 2 / SU_POR_EU <= 0.75`).
- [ ] **Step 2:** rodar → FAIL.
- [ ] **Step 3:** Implementar o esqueleto, as texturas, as receitas (motor: bronze/placas de bronze + `create:fluid_pipe` + `create:shaft`; dínamo ULV: `gtceu:ulv_machine_hull`-equivalente de ferro forjado + `create:shaft` + bobina de cobre; LV: `gtceu:lv_machine_hull` + `gtceu:lv_electric_motor`; saída: `create:fluid_pipe` + placas de cobre) e o `build.sh`. Registrar stress no Create (`BlockStressValues.IMPACTS`/`CAPACITIES` da API de Create 6 — confirmar nome com `javap` no jar).
- [ ] **Step 4:** `sh tools/ecosmaquinas/build.sh`, `packwiz refresh`, build + boot dev (`0 problemas`), `python -m pytest -q` → PASS.
- [ ] **Step 5:** Commit `feat: mod ecosmaquinas com os blocos de integração (registro)`.

### Task 4: Motor a Vapor do Eco

**Files:**
- Modify: `tools/ecosmaquinas/src/ecos/maquinas/MotorVaporBlockEntity.java`
- Create: `pack/kubejs/server_scripts/dev/maquinas_check.js` (comandos de prova em jogo, usados também nas Tasks 5–7)
- Test: `tests/test_maquinas_ingame.py`

**Interfaces:**
- Consumes: `Constantes` (Task 3).
- Produces: comando `kubejs custom_command ecos_motor_check` → linha `ECOS_MOTOR vazio_rpm=<f> cheio_rpm=<f> su=<f> mb_t=<f> agua_recusada=<bool>`.

Comportamento: `GeneratingKineticBlockEntity` com tanque interno de 8 000 mB que só aceita `gtceu:steam` (capability `FLUID_HANDLER` em todos os lados menos o eixo). Por tick consome até `MOTOR_MAX_MB_T`; gira a `MOTOR_RPM` com capacidade `SU_POR_MB_VAPOR * consumido / MOTOR_RPM` por RPM; sem vapor → 0 RPM.

- [ ] **Step 1: Teste que falha** `test_motor_vapor_ingame`: monta via comandos (`setblock` do motor numa área forceload), o dev script enche o tanque com 8 000 mB de `gtceu:steam` pela capability, espera 40 ticks; assert `cheio_rpm == 32`, `su == 24 * 80`, `vazio_rpm == 0` (motor sem vapor ao lado), `agua_recusada is True`.
- [ ] **Step 2:** rodar `python -m pytest -q -m ingame tests/test_maquinas_ingame.py -k motor` → FAIL.
- [ ] **Step 3:** Implementar `MotorVaporBlockEntity` (tick, `getGeneratedSpeed()`, `calculateAddedStressCapacity()`, NBT do tanque, tooltip de óculos de engenheiro em PT).
- [ ] **Step 4:** build.sh + build + teste → PASS.
- [ ] **Step 5:** Commit `feat: Motor a Vapor do Eco (vapor do GregTech gira o Create)`.

### Task 5: Dínamo Cinético (ULV e LV)

**Files:**
- Modify: `tools/ecosmaquinas/src/ecos/maquinas/DinamoBlockEntity.java`
- Modify: `pack/kubejs/server_scripts/dev/maquinas_check.js`
- Modify: `tests/test_maquinas_ingame.py`

**Interfaces:**
- Produces: comando `ecos_dinamo_check` → `ECOS_DINAMO ulv_eu_t=<n> lv_eu_t=<n> parado_eu_t=<n> reverso_eu_t=<n>`.

Comportamento: `KineticBlockEntity` com impacto `DINAMO_*_IMPACTO` por RPM; EU/t = `min(voltagem_tier, impacto * |RPM| / SU_POR_EU)` (ULV 8, LV 32); buffer interno de 16× a voltagem; a cada tick empurra para o vizinho na face de saída que tenha `GTCapability.CAPABILITY_ENERGY_CONTAINER` com `acceptEnergyFromNetwork(face, voltagem, amperes=1)`; expõe também `IEnergyContainer` de saída para cabos do GregTech puxarem.

- [ ] **Step 1: Teste que falha** `test_dinamo_ingame`: `create:creative_motor` a 64 RPM ligado a cada dínamo, saída num `gtceu:lv_battery_buffer_4x` (ou o buffer que existir no dump — conferir id) com baterias; após 100 ticks, `ulv_eu_t == 8`, `lv_eu_t == 32`; motor a 0 RPM → `parado_eu_t == 0`; motor a −64 RPM → `reverso_eu_t == 32`.
- [ ] **Step 2:** rodar `-k dinamo` → FAIL.
- [ ] **Step 3:** Implementar.
- [ ] **Step 4:** build + teste → PASS.
- [ ] **Step 5:** Commit `feat: Dínamo Cinético (rotação do Create vira EU do GregTech)`.

### Task 6: Saída de Vapor da caldeira do Create

**Files:**
- Modify: `tools/ecosmaquinas/src/ecos/maquinas/SaidaVaporBlockEntity.java`
- Modify: `pack/kubejs/server_scripts/dev/maquinas_check.js`
- Modify: `tests/test_maquinas_ingame.py`

**Interfaces:**
- Produces: comando `ecos_saida_check` → `ECOS_SAIDA nivel=<n> mb_t=<n> com_motores_mb_t=<n> fria_mb_t=<n>`.

Comportamento (chamada de design, ver spec §5): a Saída fica encostada num `FluidTankBlockEntity` do Create; pega o controlador e o `BoilerData`. Se `boiler.attachedEngines == 0` e `boiler.activeHeat > 0`: produz `SAIDA_MB_T_POR_NIVEL * nível` mB/t de `gtceu:steam` (nível = `min(activeHeat, getMaxHeatLevelForWaterSupply(), getMaxHeatLevelForBoilerSize(...))`, o mesmo limite que o Create usa para os motores) e empurra para vizinhos com `FLUID_HANDLER` (exceto o tanque). Com qualquer motor do Create acoplado → 0 (modo exclusivo: ou rotação, ou vapor).

- [ ] **Step 1: Teste que falha** `test_saida_vapor_ingame`: caldeira 1×1×2 de `create:fluid_tank` com `create:blaze_burner` aceso (alimentado), água por `create:creative_fluid_tank` + bomba, saída ligada a um `gtceu:steel_drum` (ou tanque do dump); após 200 ticks `mb_t == 6 * nivel` e `nivel >= 1`; com um `create:steam_engine` acoplado → `com_motores_mb_t == 0`; sem queimador → `fria_mb_t == 0`.
- [ ] **Step 2:** rodar `-k saida` → FAIL.
- [ ] **Step 3:** Implementar.
- [ ] **Step 4:** build + teste → PASS.
- [ ] **Step 5:** Commit `feat: Saída de Vapor (caldeira do Create alimenta máquinas a vapor do GregTech)`.

### Task 7: Prova do ciclo, mundo existente, cliente e documentação

**Files:**
- Modify: `pack/kubejs/server_scripts/dev/maquinas_check.js` (comando `ecos_ciclo_check`)
- Modify: `tests/test_maquinas_ingame.py`
- Modify: `README.md`, `tools/server_template/LEIA-ME-SERVIDOR.md` (seção curta "Vapor, rotação e energia" em PT)
- Modify: `docs/playtest-checklist.md` (itens de teste humano dos 3 blocos e do diesel)

- [ ] **Step 1: Teste que falha** `test_ciclo_perde_energia_ingame`: Saída de Vapor → Motor a Vapor → Dínamo LV → buffer; medir EU entregue em 600 ticks e vapor consumido; assert `eu_entregue <= 0.75 * vapor_mb / 2` (perda ≥ 25 %).
- [ ] **Step 2:** rodar → FAIL até o comando existir; implementar o comando; → PASS.
- [ ] **Step 3:** Mundo existente: `python tools/boot_test.py server` (sem `--dev`, mundo atual de `build/server`) → `0 problemas`; `python tools/boot_test.py client` → `cliente chegou ao menu`, `0 problemas`.
- [ ] **Step 4:** `python -m pytest -q` e `python -m pytest -q -m ingame` (todos) → PASS; `python tools/questcheck.py` → `OK`.
- [ ] **Step 5:** Atualizar README, LEIA-ME e checklist; commit `test: ciclo vapor-rotação-EU com perda e docs da integração`.
- [ ] **Step 6:** Avisar o usuário: o que mudou, o que testar em jogo e o comando de push (`! git push publico main`); não publicar sozinho.
