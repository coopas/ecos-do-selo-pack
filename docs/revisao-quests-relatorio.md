# Revisão das quests — relatório de mudanças

Revisão quest por quest, na ordem do jogador (Task 6 de `docs/superpowers/specs/2026-11-04-revisao-quests-design.md`).
Fontes conferidas no dump de receitas/registro do jogo (`build/recipe_dump.json`, `build/registry_dump.json`).

## Perde progresso

Nenhuma quest.

## Prólogo (`00_prologo`)

| quest | problema | correção |
|---|---|---|
| `prologo/carvao` | A descrição dizia "carvão ou carvão vegetal", mas o GregTech (`harderCharcoalRecipe`) tira o carvão vegetal da fornalha: só sai do forno de coque. | Descrição aponta o veio de carvão (y 10 a 140, minério bruto na fornalha) e avisa do carvão vegetal. |
| `prologo/balde` | O GregTech troca a receita do balde: 3 chapas de ferro + martelo de forja (a receita vanilla sumiu). Nada avisava. | Descrição explica a receita do GregTech (chapa = martelo + 2 lingotes). |
| `prologo/mochila` | A receita da mochila é do pack (`ecos:cross/backpack`) e pede liga de andesito; a pepita de ferro não sai mais do lingote à mão (só com a serra do GregTech ou derretendo ferramenta de ferro). Obrigatória para o fim do Prólogo. | Descrição diz o caminho (pá de ferro na fornalha dá pepita, ou serra do GregTech). Dependência em `ferro` testada, mas cruza linhas no layout; ficou só a descrição. |
| `prologo/mapa` | Bússola pede redstone, que só vem do veio fundo (y -65 a -10) ou do Nether. Decisão: continua **opcional** e no Prólogo — o cascalho moído no Create só sai nas rodas trituradoras, que pedem gemas de fonte (Ars), então não é redstone cedo. | Descrição diz onde está a redstone. Aviso do `questcheck` (veio fundo) fica: é opcional e diz isso. |
| `prologo/diamante` | Só no veio fundo de diamante. Já opcional desde `6cf8eae`. | Descrição ganha a faixa de altura (y -55 a -30). Aviso do `questcheck` fica (opcional). |
| `prologo/encantamento` | Pede 2 diamantes e 4 obsidianas; obsidiana só com picareta de diamante ou de aço. Já opcional. | Descrição diz o que pede, o que quebra obsidiana e de onde vem o papel do livro (o GregTech tirou papel da cana na bancada). Aviso do `questcheck` fica (opcional). |

Revisadas sem mudança: 24 quests.
