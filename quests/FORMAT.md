# Formato das quests (FTB Quests 2001.4.22 + FTB Filter System 20.0.1)

Descoberto no jar (nomes de campo via `javap -v`) e **provado em jogo** pelo `quest_selftest.js`
(o FTB relê cada quest/task/recompensa e o teste compara com a fonte).

- Pasta: `config/ftbquests/quests/` → `data.snbt`, `chapter_groups.snbt`, `chapters/<slug>.snbt`, `reward_tables/<slug>.snbt`.
- IDs: 16 hex (long positivo). Gerados por `questgen.quest_id(path)` = sha1 do caminho `capitulo/slug`.
- Capítulo: `id, group, order_index, filename, title, icon, default_quest_shape, default_hide_dependency_lines, quests, quest_links, images`.
- Quest: `id, title, description[], x, y, dependencies[], tasks[], rewards[], shape?, icon?, can_repeat?`.
- Task `item`: `item: {Count:1b, id:"..."}`, `count: NL`. **Tag** = item-filtro:
  `{Count:1b, id:"ftbfiltersystem:smart_filter", tag:{"ftbfiltersystem:filter":"ftbfiltersystem:item_tag(<tag>)"}}`
  (saída de `FTBFilterSystemAPI.makeTagFilter`; todos os membros casam, item de fora não — testado).
- Task `kill`: `entity`, `value: NL` · `dimension`: `dimension` · `checkmark`.
- Recompensas: `item` (`item`, `count`), `xp_levels`, `loot` (`table_id: <long>`).
- **Ordem de carga:** o FTB Quests carrega as quests DEPOIS de `ServerEvents.loaded` (log "Loaded N chapter groups, X chapters, Y quests").
