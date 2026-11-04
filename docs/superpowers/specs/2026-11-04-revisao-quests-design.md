# Design — Revisão completa das quests e do layout (Ecos do Selo)

Data: 2026-11-04 · Depende de: `2026-11-04-integracao-gt-create-design.md` (fazer a integração antes)

## 1. Intenção e o porquê
Os amigos já estão jogando e travaram em quests impossíveis ou cedo demais: "Ferro Bruto" (o GregTech desliga os
minérios vanilla; o ferro vem de hematita/magnetita/limonita/pirita, que não contam como ferro bruto) e a bússola
(precisa de redstone, que no GregTech só aparece em veios profundos). O usuário quer uma **revisão geral completa**:
"se imagine no contexto do jogador passando 1 por uma, se algum mod impede". Também reclamou que **as linhas das
quests estão confusas, muita coisa atravessando uma em cima da outra**.

Por que o verificador atual (`tools/questcheck.py`) não pegou: ele aceita um item se existe **qualquer** receita que o
produza (o ferro bruto "tem receita" — a do bloco de ferro bruto, um círculo) e não sabe em que ponto da jornada o
jogador está. O layout (`questgen.layout`) só põe cada quest numa coluna pela profundidade, sem evitar cruzamentos.

## 2. Decisões do usuário
- Revisão de **todas** as 511 quests, na ordem do jogador, considerando o que cada mod muda.
- Quest impossível/cedo demais: trocar por equivalente, mudar de lugar ou remover.
- Arrumar as linhas cruzadas.
- Fazer depois da integração GregTech × Create (projeto 1).
- Correção rápida **agora**, separada (aprovado em 2026-11-04): "Ferro Bruto" aceita os minérios que viram ferro
  e a bússola fica **opcional** (sai das dependências do fim do Prólogo). Quando a integração trouxer redstone cedo,
  a revisão decide se a bússola volta a ser obrigatória.
- **Criar quests novas** para o conteúdo da integração (Motor a Vapor, Dínamo Cinético, saída de vapor da caldeira,
  motores a diesel, minério no Create) nos capítulos laterais do Create e do GregTech, sem mudar o número de atos.

## 3. Objetivos / Não-objetivos / Anti-objetivos
**Objetivos**
1. **Verificador de progressão** que simula o jogador: para cada quest, o item/tag pedido precisa ser produzível
   **a partir do que existe naquele ponto** — fontes naturais do mundo/dimensões já liberadas, drops de mobs/chefes
   alcançáveis, recompensas de quests anteriores, e receitas cujas **máquinas** já estão disponíveis (o fecho é
   calculado de verdade, recursivamente, a partir das fontes; receita circular não conta).
   - "Ponto na jornada" = o ato da quest + suas dependências (travas de portal, tier de energia do GregTech,
     dimensões liberadas por ato, conforme `docs/2026-11-03-ecos-do-selo-design.md` e `pack/kubejs/ecos/travel.json`).
   - Considera o worldgen real: minérios vanilla desligados pelo GregTech (`removeVanillaOreGen: true`), veios do
     GregTech por dimensão.
   - Sinaliza também **"difícil cedo demais"**: item possível, mas que exige máquina/tier acima do ato (ex.: redstone
     no Prólogo).
2. **Revisão humana assistida**: o construtor percorre capítulo por capítulo na ordem (Prólogo → Final, depois os
   Caminhos e a Loja), lendo cada quest como jogador e corrigindo o que o verificador apontou e o que ele não
   consegue ver (ex.: quest que pede item de mod com mecânica escondida, quantidade absurda para o ato).
3. **Layout sem cruzamentos**: posições geradas para que as linhas de dependência não se cruzem (ou o mínimo
   possível) e **nenhuma linha passe por cima de outra quest**; capítulos legíveis da esquerda para a direita.
   Um teste automático mede cruzamentos e linhas sobre quests e falha acima de zero (ou de um limite justificado).
4. **Correção rápida primeiro** (decisão do usuário; feita em 2026-11-04 antes do resto):
   "Ferro Bruto" aceita qualquer minério bruto que vira ferro na fornalha (tag nova do pack unindo
   `forge:raw_materials/` iron, hematite, magnetite, goethite, yellow_limonite, pyrite); a bússola sai do Prólogo para depois do ponto em que
   o jogador obtém redstone — por ora ela só ficou opcional, sem mudar de capítulo (no Prólogo fica o minimapa).
5. **Quests novas** da integração, com a mesma checagem de progressão.

**Não-objetivos**
- Não reescrever a lore nem o número de atos/capítulos.
- Não mudar IDs das quests que não mudam (o progresso salvo dos jogadores é por ID: trocar o slug zera a quest).

**Anti-objetivos**
- Apagar progresso dos jogadores: quest **removida**, com **slug trocado** ou **movida de capítulo** perde o
  progresso (o ID é hash de `capitulo/slug`). Chamada minha: o YAML ganha um campo opcional `legacy_id: <capitulo/slug
  antigo>` para a quest movida manter o ID antigo; o verificador impede IDs duplicados. Preferir editar a
  task mantendo o slug; remoções e trocas de slug ficam listadas para o usuário antes de publicar.
- Beco sem saída: nenhuma quest pode ficar sem caminho (o verificador garante) e o "Fim" de cada ato continua alcançável.
- Esconder problema: quest "difícil" não vira "fácil" trocando por checkmark; troca por um item equivalente da era.

## 4. Restrições
- Fontes em `quests/src/*.yaml`, gerador `tools/questgen.py`, verificador `tools/questcheck.py`, dados
  `quests/naturals.yaml`, `quests/variant_tags.yaml`. Saída em `pack/config/ftbquests/quests/`.
- O selftest em jogo (`dev/quest_selftest.js`) continua provando que o FTB carregou exatamente a fonte.
- Coordenadas explícitas `x/y` em YAML continuam vencendo o layout automático.
- Tudo em PT-BR; IDs contra o dump de registro.

## 5. Deixado para o construtor
- Algoritmo do layout (camadas por profundidade + ordenação por baricentro para reduzir cruzamentos, com ajuste para
  linhas não atravessarem quests; deps entre capítulos não desenham linha).
- Modelagem das "capacidades por ato" (tabela de máquinas/tiers/dimensões liberadas) e das fontes naturais por
  dimensão (incluindo veios do GregTech).
- Como tratar receitas de máquinas do GregTech no fecho (máquina disponível = quest dela concluída ou receita da
  máquina alcançável na tier do ato).
- Lista final de mudanças por quest, num relatório (`docs/revisao-quests-relatorio.md`) com: quest, problema, correção.

## 6. Verificação
`questcheck` novo limpo; teste de cruzamentos zerado; `pytest`; `boot_test.py server --dev` com o selftest de quests;
o relatório de mudanças revisado com o usuário antes do push (por causa do progresso salvo).
