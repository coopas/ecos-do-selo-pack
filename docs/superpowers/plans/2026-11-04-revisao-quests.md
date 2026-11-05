# Revisão completa das quests e do layout — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Nenhuma quest impossível ou cedo demais para o ponto da jornada em que está, linhas de dependência sem cruzamentos, e quests novas para a integração GregTech × Create.

**Architecture:** O dump em jogo passa a exportar o que falta para simular o jogador (entradas e EU das receitas do GregTech, fluidos, veios do GregTech por dimensão, nível de mineração de cada picareta). Um motor de fecho (`tools/closure.py`) calcula, para cada quest, tudo o que o jogador consegue produzir a partir das fontes do mundo já liberadas, das recompensas e das tasks anteriores e das máquinas já alcançáveis. O `questcheck` usa esse fecho no lugar do "existe alguma receita". O layout do `questgen` vira camadas com ordenação por baricentro e um teste mede cruzamentos. Por fim, a revisão humana percorre os capítulos na ordem, com relatório.

**Tech Stack:** Python 3 + pytest + PyYAML, KubeJS 2001.6.5 (Rhino), GTCEu 7.5.3, FTB Quests 2001, packwiz.

**Spec:** `docs/superpowers/specs/2026-11-04-revisao-quests-design.md`

## Global Constraints
- Todo texto visível em PT-BR; descrição de quest com no máximo 4 linhas (`questcheck.MAX_DESC_LINES`).
- **ID de quest = hash de `capitulo/slug`** (`questgen.quest_id`): não trocar slug nem mover quest de capítulo sem `legacy_id`. Toda remoção, troca de slug ou movimentação vai para o relatório e é mostrada ao usuário **antes do push**.
- Não mudar o número de atos nem de capítulos; não reescrever a lore.
- Quest "difícil" não vira checkmark: troca por item equivalente da era.
- `x`/`y` explícitos no YAML continuam vencendo o layout automático.
- Dumps regenerados com `python tools/boot_test.py server --dev` (porta 25570; nunca matar `java` que o teste não iniciou).
- Edição de arquivos do repo preservando o fim de linha original (ler/gravar em bytes; o `00_prologo.yaml` é CRLF).
- Commits sem `Co-Authored-By` e sem prefixo de data na mensagem (o hook do usuário já põe). Push no `publico` só com o usuário de acordo.
- Toda mudança em quest passa por: `python tools/questgen.py`, `python tools/questcheck.py` limpo, `packwiz refresh` em `pack/`, `python -m pytest -q`, `boot_test server --dev` com o selftest de quests (511 → contagem nova).

## Review Focus
1. **Receita circular contando como fonte** (bloco de ferro bruto ⇄ ferro bruto): o fecho parte só das fontes; um item que só aparece num ciclo continua indisponível. Teste `test_cycle_is_not_a_source` na Task 2.
2. **Tag de task com um membro fácil e outros impossíveis** (ex.: `forge:gems/diamond`): basta um membro alcançável; a mensagem de erro cita a tag, não cada membro. Teste `test_tag_task_needs_one_member` na Task 3.
3. **Obsidiana e minério que exigem picareta de nível acima do que o jogador tem**: fonte natural com nível de mineração só conta quando há picareta daquele nível no fecho. Teste `test_natural_needs_pickaxe_tier` na Task 2.
4. **Máquina do GregTech de tier menor que o EU da receita** (e steam × LV): a receita só conta com máquina de tier ≥ EU/t. Teste `test_gt_recipe_needs_machine_tier` na Task 2.
5. **Dependência entre capítulos no layout** (não desenha linha no FTB): não entra na contagem de cruzamentos nem na profundidade local. Teste `test_cross_chapter_dep_not_counted` na Task 5.

---

### Task 1: Dump com o que falta para simular o jogador

**Files:**
- Modify: `pack/kubejs/server_scripts/dev/registry_dump.js`
- Modify: `tools/recipes.py`, `tools/registry.py`
- Test: `tests/test_dump_progressao.py` (novo; testes `ingame` leem `build/*.json` depois de um boot)

**Interfaces:**
- Produces (recipe_dump, por receita, campos novos opcionais): `"fluid_inputs": [["<fluid id>", ...], ...]`, `"fluid_outputs": ["<fluid id>"]`, `"eut": int` (EU/t de entrada, 0 se não for GT), `"ebf_temp": int` (0 se não tiver). `inputs` do GregTech preenchido como já é para o vanilla (lista de slots, cada slot lista de alternativas `item` ou `#tag`).
- Produces (registry_dump): `"pickaxe_tiers": {"<item>": 0..4}` (0 = madeira/ouro, 1 = pedra, 2 = ferro, 3 = diamante, 4 = netherite; calculado em jogo com `isCorrectToolForDrops` contra `minecraft:stone`, `minecraft:iron_ore`, `minecraft:diamond_ore`, `minecraft:obsidian`, `minecraft:ancient_debris`, só para itens em `#minecraft:pickaxes` ou `#forge:tools/pickaxes`); `"block_tiers": {"<bloco>": 0..4}` para todo bloco em `minecraft:needs_*_tool`/`forge:needs_netherite_tool`; `"gt_veins": [{"id", "dims": [...], "min_y", "max_y", "weight", "materials": ["<material>"]}]` lido de `GTRegistries.ORE_VEINS`.
- Produces: `Recipes.fluid_producers(fluid) -> list[dict]`; `Registry.pickaxe_tiers: dict[str,int]`, `Registry.block_tiers: dict[str,int]`, `Registry.gt_veins: list[dict]` (todos com default vazio para os fixtures antigos continuarem carregando).

- [ ] **Step 1:** No `registry_dump.js`, ler as entradas do GTRecipe como já se lê a saída (`r.inputs` = Map<Cap, List<Content>>; `getInner().toJson()` no SizedIngredient; o FluidIngredient também tem `toJson`), EU/t por `com.gregtechceu.gtceu.api.recipe.RecipeHelper.getInputEUt(r)` e `r.data.getInt("ebf_temp")`. Erros vão para `errors`/`gt_debug` como hoje, sem derrubar o dump.
- [ ] **Step 2:** Exportar `pickaxe_tiers`, `block_tiers` e `gt_veins` (dimensões do `dimensionFilter`, faixa de altura do `range`, `weight`, materiais das camadas do gerador).
- [ ] **Step 3:** Carregadores em `recipes.py`/`registry.py` com os campos novos e defaults.
- [ ] **Step 4:** `python tools/boot_test.py server --dev` → `0 problemas`.
- [ ] **Step 5: Testes `ingame` (lendo `build/`)**
  - `test_gt_inputs_filled`: menos de 5 % das receitas `gtceu:*` com `inputs` e `fluid_inputs` vazios ao mesmo tempo.
  - `test_gt_eut`: `gtceu:macerator/macerate_iron_ore`-like (qualquer `gtceu:macerator/*`) tem `eut` entre 1 e 32.
  - `test_ebf_temp`: alguma receita `gtceu:electric_blast_furnace/*` com `ebf_temp >= 1000`.
  - `test_pickaxe_tiers`: `minecraft:iron_pickaxe == 2`, `minecraft:diamond_pickaxe == 3`, `minecraft:stone_pickaxe == 1`; `block_tiers["minecraft:obsidian"] == 3`.
  - `test_diamond_vein`: há veio com `"diamond"` em `materials`, `minecraft:overworld` em `dims` e `max_y < 0` (confirma o que o jar mostrou: `diamond_vein` nas regras de deepslate).
  - Registrar no relatório (Task 7) o nível de `gtceu:steel_pickaxe` e `gtceu:bronze_pickaxe`: é a resposta da obsidiana do Ato I.
- [ ] **Step 6:** `python -m pytest -q` e `-m ingame -k dump_progressao` passam. Commit `feat: dump exporta entradas do GregTech, EU, veios e nível das picaretas`.

### Task 2: Motor de fecho e dados de progressão

**Files:**
- Create: `quests/progression.yaml`, `tools/progression.py`, `tools/closure.py`
- Modify: `quests/naturals.yaml` (reorganizado por dimensão; o comentário do topo explica o formato)
- Test: `tests/test_closure.py` (fixtures pequenos em Python, sem dump)

**Interfaces:**
- `quests/naturals.yaml`: chaves = dimensão (`minecraft:overworld`, `minecraft:the_nether`, …) ou `qualquer`; valor = lista de entradas, cada uma `"<item>"`, `"#tag"`, `"fluid:<id>"` ou `{id: ..., needs: [itens, um basta], tier: 0..4}`. Os minérios **saem** daqui (`#forge:ores`, `#forge:raw_materials`, `#forge:gems`, `minecraft:diamond`, `minecraft:redstone`… eram a causa de "tudo é natural"): vêm dos `gt_veins` + `block_tiers`, e minérios de outros mods (Aether, Blue Skies, Twilight, Undergarden, Ad Astra) entram listados na dimensão deles.
- `quests/progression.yaml`:
  - `dimension_unlocks: {<dim>: <capitulo/slug da quest que libera>}` (overworld sempre liberado; ex.: `minecraft:the_nether: ato1/nether`, Aether e Blue Skies pela quest da Chave Celeste — conferir com `travel.json`).
  - `manual_types: [...]` (crafting shaped/shapeless/special, kubejs, smithing etc.: sempre disponíveis).
  - `machines: {<recipe type>: [itens da máquina, um basta]}` para tipos que não são do GregTech (`minecraft:smelting: [minecraft:furnace]`, `create:milling: [create:millstone]`, `create:mixing: [create:mechanical_mixer]`…); tipos `gtceu:<x>` resolvidos por nome: `gtceu:<tier>_<x>` (tier ulv/lv/mv/hv/ev/iv/luv/zpm/uv), `gtceu:lp_steam_<x>`/`gtceu:hp_steam_<x>`, ou controlador `gtceu:<x>`.
  - `steam_max_eut: {lp: <n>, hp: <n>}` — valor lido do jar (`SimpleSteamMachine`) no Step 1, não chutado.
  - `eu_sources: [...]` (geradores, turbinas, `ecosmaquinas:dinamo_cinetico_*`): máquina elétrica só conta com uma fonte de EU no fecho.
  - `coils: {<item da bobina>: <temperatura>}` para `ebf_temp`.
  - `deep_ok_from_act: 1` (veio com `max_y < 0` antes desse ato vira aviso "difícil cedo demais").
- Produces: `progression.load(path) -> Progression`; `closure.reach(seed: set[str], dims: set[str], prog, rec, reg) -> Reach` com `Reach.items: set[str]`, `Reach.fluids: set[str]`, `Reach.why(item) -> str` (receita ou fonte que trouxe o item, para a mensagem); `closure.deep_only(item, dims, prog, reg) -> bool`.
- Regra do fecho: fontes naturais das `dims` cujo `needs`/`tier` já é satisfeito, mais a `seed`; depois ponto fixo por fila (índice entrada → receitas): receita entra quando todo slot de item e de fluido tem uma alternativa alcançada e a máquina está disponível (manual; item da máquina alcançado; GT com tier ≥ `eut` e fonte de EU se elétrica; `ebf_temp` ≤ bobina alcançada). Liberar uma picareta reavalia as fontes naturais. Fluido também vem do balde cheio alcançado.

- [ ] **Step 1: Testes que falham** (`tests/test_closure.py`):
  - `test_cycle_is_not_a_source`: receitas `a→b` e `b→a`, sem fonte → nem `a` nem `b` em `reach`.
  - `test_natural_needs_pickaxe_tier`: obsidiana com `tier: 3`; com só picareta de ferro na seed → fora; com `minecraft:diamond_pickaxe` → dentro.
  - `test_gt_recipe_needs_machine_tier`: receita `gtceu:macerator` com `eut: 30`; seed com `gtceu:lp_steam_macerator` e `steam_max_eut.lp = 8` → fora; com `gtceu:lv_macerator` + fonte de EU → dentro; com `gtceu:lv_macerator` sem fonte → fora.
  - `test_machine_must_be_reached`: receita `minecraft:smelting` sem `minecraft:furnace` alcançável → fora.
  - `test_dimension_gates_naturals`: item natural só do Nether fica fora sem `minecraft:the_nether` em `dims`.
  - `test_tag_alternative_slot`: slot `#forge:ingots/iron` satisfeito por qualquer membro.
  - `test_ebf_needs_coil`: `ebf_temp: 1800` fora sem bobina de ≥ 1800.
- [ ] **Step 2:** Rodar → falham.
- [ ] **Step 3:** Implementar `progression.py` e `closure.py`; reorganizar `naturals.yaml` por dimensão.
- [ ] **Step 4:** Testes passam; `python -m pytest -q` todo verde. Medir `reach` no dump real: abaixo de 2 s por chamada (anotar o número no commit).
- [ ] **Step 5:** Commit `feat: motor de fecho de progressão (fontes do mundo, máquinas, tiers)`.

### Task 3: `questcheck` usa o ponto da jornada

**Files:**
- Modify: `tools/questcheck.py`, `tests/test_questcheck.py`, `tests/fixtures/*` se precisar

**Interfaces:**
- Consumes: `closure.reach`, `progression.load`.
- Produces: `check(...)` mantém a assinatura e passa a receber `prog` (com default que reproduz o comportamento antigo nos testes antigos); `check_progress(chapters, reg, rec, prog, naturals, boss_drops) -> list[Finding]`, `Finding(path: str, level: "erro" | "aviso", msg: str)`. CLI: erros saem com código 1; avisos aparecem mas não falham. `python tools/questcheck.py --relatorio` grava `build/questcheck_progresso.txt`.
- Estado de cada quest: `dims` = overworld + dimensões cuja quest de `dimension_unlocks` é ancestral (ou a própria quest, para a task de dimensão); `seed` = recompensas e itens de task de todos os ancestrais + drops de chefes cujas tasks de kill são ancestrais. Quests em ordem topológica, memorizando `reach` por `(frozenset(seed), frozenset(dims))`.
- Erro: item/tag da task fora do `reach` → `"<path>: <item> impossível neste ponto (falta: <o que faltou no caminho mais curto>)"`. Aviso: só alcançável por veio fundo antes de `deep_ok_from_act`, ou por receita GT acima do tier esperado do ato (`act_tier: {0: none, 1: lv, 2: mv, 3: ev, 4: luv, 5: uv}` no `progression.yaml`).

- [ ] **Step 1: Testes que falham**:
  - `test_tag_task_needs_one_member`: tag com um membro alcançável e um não → sem erro.
  - `test_reward_of_ancestor_is_seed`: item só vindo de recompensa de ancestral → ok; de quest não ancestral → erro.
  - `test_iron_vanilla_raw_impossible_in_prologue`: task `forge:raw_materials/iron` sem fonte (vanilla desligado) → erro; `ecos:minerios_de_ferro` com hematita natural → ok (o caso real de hoje).
  - `test_deep_only_warns_before_act`: diamante só em veio `max_y < 0`, quest do ato 0 → aviso, ato 1 → nada.
  - `test_dimension_task_quest_sees_its_dimension`.
- [ ] **Step 2:** Rodar → falham. **Step 3:** Implementar. **Step 4:** `pytest -q` verde.
- [ ] **Step 5:** Rodar no pack real e salvar `build/questcheck_progresso.txt` (lista de entrada da Task 6). Esperado: Prólogo acusa bússola (aviso/erro de redstone), diamante (aviso) e a obsidiana do Ato I conforme o nível das picaretas da Task 1.
- [ ] **Step 6:** Commit `feat: questcheck simula o jogador no ponto de cada quest`.

### Task 4: `legacy_id` e IDs únicos

**Files:**
- Modify: `tools/questgen.py`, `tools/questcheck.py`, `quests/FORMAT.md`, `tests/test_questgen.py`, `tests/test_questcheck.py`

**Interfaces:**
- Campo opcional de quest `legacy_id: "<capitulo/slug antigo>"`: `build` usa `quest_id(legacy_id)` para a quest e suas tasks/recompensas (`legacy_id#t0`…), e as deps que apontam para ela resolvem para o mesmo ID.
- `questcheck`: erro `"ID duplicado: <a> e <b>"` quando dois caminhos (ou `legacy_id`) dão o mesmo ID.

- [ ] **Step 1:** Testes `test_legacy_id_keeps_old_ids` (quest movida para outro capítulo mantém o ID, as tasks e as deps) e `test_duplicate_id_rejected`. **Step 2:** falham. **Step 3:** implementar + documentar no `FORMAT.md`. **Step 4:** verde. **Step 5:** commit `feat: legacy_id preserva o progresso de quest movida`.

### Task 5: Layout sem cruzamentos

**Files:**
- Modify: `tools/questgen.py` (`layout`)
- Create: `tools/layoutcheck.py`
- Test: `tests/test_layout.py`

**Interfaces:**
- Produces: `layoutcheck.crossings(c, pos) -> int` (pares de segmentos de dependência local que se cruzam, sem contar os que dividem uma ponta); `layoutcheck.lines_over_quests(c, pos, radius=0.6) -> int` (segmento que passa a menos de `radius` do centro de uma quest que não é ponta dele); CLI imprime por capítulo.
- `layout(c)`: camadas pela profundidade local (como hoje); ordem dentro da camada por baricentro das posições dos pais, várias passadas ida e volta; aresta que pula camadas recebe pontos virtuais no cálculo (não viram quest) para não atravessar quests; quest sem dependência local fica na coluna 0. `x`/`y` explícitos continuam vencendo.

- [ ] **Step 1: Testes que falham**:
  - `test_crossing_counter`: X simples (a→d, b→c com a,b na coluna 0 e c,d invertidos) conta 1.
  - `test_line_over_quest_counter`: a→c passando reto por b conta 1.
  - `test_cross_chapter_dep_not_counted`.
  - `test_all_chapters_clean`: para cada capítulo de `load_sources()`, `crossings == 0` e `lines_over_quests == 0`; se algum capítulo não zerar com o algoritmo, posições `x`/`y` explícitas naquele capítulo, ou limite por capítulo em `LIMITES = {...}` com o motivo ao lado.
  - `test_explicit_position_wins` (já existe) continua passando.
- [ ] **Step 2:** falham. **Step 3:** implementar. **Step 4:** verde; `python tools/layoutcheck.py` mostra 0 em todos.
- [ ] **Step 5:** Abrir o livro em jogo não dá para automatizar: gerar uma imagem por capítulo (`tools/layoutcheck.py --png build/layout/`, linhas e círculos com Pillow) e olhar os PNGs do Prólogo, Ato I e de um capítulo grande antes de seguir.
- [ ] **Step 6:** Commit `feat: layout das quests por baricentro, sem cruzamentos`.

### Task 6: Revisão humana capítulo por capítulo

**Files:**
- Modify: `quests/src/*.yaml` (na ordem abaixo)
- Create: `docs/revisao-quests-relatorio.md`

Ordem: `00_prologo` → `10_ato1`, `11_side_create`, `12_side_gt_steam_lv` → `20_ato2`, `21`–`23` → `30_ato3`, `31`, `32` → `40_ato4`, `41` → `50_ato5`, `51` → `60_final` → `90_loja`. Um commit por ato.

Para cada quest, como jogador no ponto dela: (1) o `questcheck` acusa algo? (2) o que pede é razoável para o ato (quantidade, mecânica escondida de mod, onde se acha)? (3) a descrição diz onde achar quando não é óbvio? Correção, nessa preferência: editar a task mantendo o slug → mudar de lugar com `legacy_id` → remover. Casos já conhecidos: bússola (redstone agora vem do cascalho moído no Create: decidir se volta a ser obrigatória e onde), diamante/mesa de encantamento (opcionais desde `6cf8eae`), obsidiana do Ato I (conforme o nível das picaretas do GT; se só diamante quebra, trocar a task ou dar caminho), `loja/diamantes` dependendo de `ato1/inicio`.

- [ ] **Step 1:** Por ato: corrigir, rodar `questgen` + `questcheck` (zero erros; avisos que ficarem têm motivo no relatório) + `layoutcheck` + `pytest -q`, commit `fix: revisão das quests do <ato>`.
- [ ] **Step 2:** Relatório: tabela `| quest | problema | correção |` por capítulo, e no topo a seção **"Perde progresso"** com toda quest removida, com slug trocado ou movida sem `legacy_id` (vazia se não houver).

### Task 7: Quests novas da integração

**Files:**
- Modify: `quests/src/11_side_create.yaml`, `quests/src/12_side_gt_steam_lv.yaml`

Quests novas (slugs novos, nenhum ID antigo muda), cada uma checada pelo `questcheck` novo: `motor_vapor` (`ecosmaquinas:motor_vapor`), `dinamo_ulv` e `dinamo_lv` (`ecosmaquinas:dinamo_cinetico_ulv`/`_lv`), `saida_vapor` (`ecosmaquinas:saida_vapor`), `diesel` (um motor do Create: Diesel Generators — ID confirmado no registro), `minerio_no_create` (minério triturado do GregTech saído das rodas trituradoras). Descrições curtas em PT-BR dizendo o que o bloco faz (números do `LEIA-ME-SERVIDOR.md`).

- [ ] **Step 1:** Escrever, gerar, checar, `layoutcheck` 0, `pytest -q`. **Step 2:** commit `feat: quests da integração GregTech × Create`.

### Task 8: Verificação final e entrega

- [ ] **Step 1:** `python tools/questgen.py`; `python tools/questcheck.py` → `OK`; `python tools/layoutcheck.py` → 0; `cd pack && packwiz refresh`; `python tools/check_manifest.py` → OK; `python -m pytest -q`.
- [ ] **Step 2:** `python tools/build_server.py` e `python tools/boot_test.py server --dev` → `0 problemas`; `build/quest_selftest.json` novo com `quests` igual ao total gerado.
- [ ] **Step 3:** Atualizar `docs/playtest-checklist.md` com o que mudou.
- [ ] **Step 4:** Mostrar ao usuário o relatório (principalmente "Perde progresso") e só então, com o ok dele, `git push publico main`.
