# Revisão das quests — relatório de mudanças

Revisão quest por quest, na ordem do jogador (Task 6 de `docs/superpowers/specs/2026-11-04-revisao-quests-design.md`).
Fontes conferidas no dump de receitas/registro do jogo (`build/recipe_dump.json`, `build/registry_dump.json`).

## Perde progresso

Nenhuma quest.

## Prólogo (`00_prologo`)

| quest | problema | correção |
|---|---|---|
| `prologo/carvao` | A descrição dizia "carvão ou carvão vegetal", mas o GregTech (`harderCharcoalRecipe`) tira o carvão vegetal da fornalha: só sai do forno de coque. | Descrição aponta o veio de carvão (y 10 a 140, minério bruto na fornalha) e avisa do carvão vegetal. |
| `prologo/balde` | O GregTech troca a receita do balde: 3 chapas de ferro + martelo de forja (a receita vanilla sumiu). Nada avisava. | Descrição explica a receita do GregTech (chapa = martelo do GregTech, a ferramenta, + 2 lingotes). |
| `prologo/mochila` | A receita da mochila é do pack (`ecos:cross/backpack`) e pede liga de andesito; a pepita de ferro não sai mais do lingote à mão (só com a serra do GregTech ou derretendo ferramenta de ferro). Obrigatória para o fim do Prólogo. | Descrição diz o caminho mais curto: a liga aceita pepita de zinco, e lingote de zinco (minério do Create) vira 9 pepitas à mão; ou pá de ferro derretida dá pepita; ou a banca vende a mochila (8 ecos). Dependência em `ferro` testada, mas cruza linhas no layout; ficou só a descrição. |
| `prologo/mapa` | Bússola pede redstone, que só vem do veio fundo (y -65 a -10) ou do Nether. Decisão: continua **opcional** e no Prólogo — o cascalho moído no Create só sai nas rodas trituradoras, que pedem gemas de fonte (Ars), então não é redstone cedo. | Descrição diz onde está a redstone. Aviso do `questcheck` (veio fundo) fica: é opcional e diz isso. |
| `prologo/diamante` | Só no veio fundo de diamante. Já opcional desde `6cf8eae`. | Descrição ganha a faixa de altura (y -55 a -30). Aviso do `questcheck` fica (opcional). |
| `prologo/encantamento` | Pede 2 diamantes e 4 obsidianas; obsidiana só com picareta de diamante ou de aço. Já opcional. | Descrição diz o que pede, o que quebra obsidiana e de onde vem o papel do livro (o GregTech tirou papel da cana na bancada). Aviso do `questcheck` fica (opcional). |

Revisadas sem mudança: 24 quests.

## Ato I (`10_ato1`)

Contexto conferido na config do GregTech do servidor (`gtceu.yaml`): `flintAndSteelRequireSteel`, `disableManualCompression`
(lingote não vira bloco na bancada), `hardGlassRecipes` (areia não vira vidro na fornalha), `nerfPaperCrafting`,
`harderCharcoalRecipe`. A pepita de ferro só sai do lingote com a serra do GregTech.

| quest | problema | correção |
|---|---|---|
| `ato1/obsidiana` | O isqueiro do GregTech pede engrenagem e mola pequenas de aço, e a obsidiana só cede à picareta de aço (ou diamante): sem aço não há Nether. A quest abria logo no início do ato. | Dependência nova em `side_gt_steam_lv/aco` (entre capítulos, sem linha) e descrição com o caminho (picareta de aço/diamante, ou magma lavado no ventilador do Create). |
| `ato1/quartzo` | Não dizia onde. | Descrição: veio de quartzo do Nether, y 40 a 80. |
| `ato1/ferro_em_massa` | Dependia das rodas trituradoras, que pedem montadores mecânicos, cuja receita do pack pede gemas de fonte (Ars, Ato II): quest do Ato I presa ao Ato II. | Dependência trocada para `side_gt_steam_lv/macerador_vapor` (moer antes de derreter também rende mais); descrição cita os dois caminhos. |
| `ato1/chave` | A receita pede um diamante, e a descrição dizia "o diamante não serve mais". | Descrição lista os ingredientes (mecanismo, latão, mudas, diamante) e esclarece que é jogar diamante no lago que não serve. |
| `ato1/mapa_magico` | O foco do mapa leva pó de glowstone (Nether) e o mapa leva 8 papéis (a bancada não faz papel). | Descrição diz os dois. |
| `ato1/ferro_madeira` | Ferro-madeira pede `minecraft:raw_iron`, que só o minério de ferro comum dá (veio de cobre, y -40 a 10); hematita e cia. não servem. A pepita de ouro não sai do lingote à mão. | Descrição diz onde está o ferro e que a pepita de ouro sai derretendo uma pá de ouro. |
| `ato1/folha_aco` | Steeleaf só vem de baús; a descrição sugeria folhas. | Descrição: baús das colinas ocas e do labirinto. |
| `ato1/amuleto` | Só de loot, sem dica. | Descrição: baús da floresta. |

Revisadas sem mudança: 35 quests.

## Caminho — Engrenagens de Aurend (`11_side_create`)

| quest | problema | correção |
|---|---|---|
| `side_create/liga` | Liga de andesito pede pepitas; as de ferro só a serra do GregTech corta do lingote. | Descrição aponta o atalho: lingote de zinco vira 9 pepitas à mão e a liga aceita zinco. |
| `side_create/oculos` | Óculos pedem vidro; aqui o vidro só sai do fundidor de ligas do GregTech com molde de bloco (molde = chapas de aço). | Dependências novas em `side_gt_steam_lv/ligas_vapor` e `side_gt_steam_lv/aco` (entre capítulos) e descrição. |
| `side_create/chave_inglesa` | Chapas de ouro antes da prensa: só com o martelo do GregTech. | Descrição diz isso. |
| `side_create/prensa` | A prensa pede bloco de ferro, que só sai de máquina (compressor a vapor). Abria antes do jogador ter como fazer. | Dependência nova em `side_gt_steam_lv/compressor_vapor` (entre capítulos) e descrição. |
| `side_create/zinco` | Não dizia de onde (o GregTech não tem esfalerita no Overworld). | Descrição: minério de zinco do Create. |
| `side_create/queimador` | **Erro do `questcheck`**: netherrack e blaze só no Nether, que abre em `ato1/nether`, fora dos ancestrais. | Dependência nova em `ato1/nether` e descrição. Erro zerado. |
| `side_create/latao` | O misturador só faz latão aquecido (queimador, Nether). Não dizia o caminho antes do Nether. | Descrição: queimador aceso, ou pó de cobre e zinco à mão (pilão do GregTech) na fornalha. |
| `side_create/valvula` | Válvula eletrônica = quartzo rosa = quartzo do Nether + 8 redstone. Abria sem o Nether; 8 válvulas = 64 redstone. | Dependência nova em `ato1/quartzo`; pede 4 (bastam para aplicador e 9 montadores); descrição com a receita. |
| `side_create/montador` | A receita do pack (`ecos:cross/mechanical_crafter`) pede gemas de fonte da Ars Nouveau; nada avisava. | Descrição dá os passos (6 gemas; tábuas de archwood, ouro e liga de andesito fazem a Câmara de Imbuição; ametista nela vira gema), sem mandar para o capítulo da Ars, que ainda está escondido. Dependência em `side_ars/gema_fonte` deixaria as deps locais redundantes (o teste proíbe) e travaria a quest até o Ato II; ficou só a descrição. |
| `side_create/rodas_trituradoras` | O cascalho moído dá redstone (10 %) e ninguém sabia. | Descrição cita. |
| `side_create/motor_vapor` | Cada motor pede um bloco de cobre (só compressor). | Descrição diz isso. |
| `side_create/medidores` | O velocímetro leva bússola (redstone). | Descrição diz isso. |
| `side_create/trilhos` | Trilho sai de montagem em sequência (aplicador), que não estava nos ancestrais; a estação pede bússola e chapa de obsidiana (GregTech). | Dependência nova em `aplicador` e descrição. |

Revisadas sem mudança: 21 quests.

## Caminho — Vapor e Corrente (`12_side_gt_steam_lv`)

| quest | problema | correção |
|---|---|---|
| `side_gt_steam_lv/resina` | Não dizia como pegar resina. | Descrição: tronco nativo de seringueira solta resina (85 %), slime derrete em resina. |
| `side_gt_steam_lv/tijolos_refratarios` | Argila refratária comprimida só sai do compressor; o alto-forno (e o aço) dependem disso e a quest abria antes. | Dependência nova em `compressor_vapor` e descrição. |
| `side_gt_steam_lv/compressor_vapor` | Pistões pedem redstone (veio fundo); é o compressor que faz blocos. | Descrição diz os dois. |
| `side_gt_steam_lv/macerador_vapor` | Pede 2 diamantes e pistões. | Descrição diz onde (veio fundo ou banca). |
| `side_gt_steam_lv/ligas_vapor` | É ele que faz vidro aqui; o molde vazio é de aço. | Descrição diz isso. |
| `side_gt_steam_lv/extrator_vapor` | Leva vidro (fundidor de ligas). | Descrição. Dependências novas testadas, mas passavam do limite de cruzamentos do capítulo. |
| `side_gt_steam_lv/borracha` | A barra de borracha pede enxofre, que só tem veio no Nether (y 10 a 30); o macerador a vapor não dá subproduto. | Dependência nova em `ato1/nether` e descrição. |
| `side_gt_steam_lv/tubo_vidro` | Molde de bola é de aço. | Descrição (dependência em `aco` passava do limite de cruzamentos; a válvula logo depois já herda o aço pelo Nether). |
| `side_gt_steam_lv/valvula` | Pede parafusos de aço. | Descrição. |
| `side_gt_steam_lv/resistor` | Leva papel, que a bancada não faz mais. | Descrição: cana na prensa do Create. |
| `side_gt_steam_lv/liga_vermelha` | Não dizia onde está a redstone. | Descrição: veio fundo ou veio do Nether. |
| `side_gt_steam_lv/ferro_forjado` | Pepita de ferro forjado só vira lingote numa máquina (bancada não compacta). | Dependência trocada de `mais_ferramentas` para `compressor_vapor` (que junta nove pepitas num lingote, sem molde); descrição. |
| `side_gt_steam_lv/martelo_vapor` | Leva bigorna, e a bigorna do GregTech pede 5 blocos de ferro (só compressor). Dependia só da caldeira. | Dependência trocada para `ferro_forjado` (que vem do compressor): `compressor_vapor` direto quebra o teste de layout (raiz `seringueira` sai da coluna). Descrição cita a bigorna e o compressor. |
| `side_gt_steam_lv/maquinas_lv` | O macerador LV pede um diamante. | Descrição. |
| `side_gt_steam_lv/casco_lv` | Dependência em `aco` ficou redundante (o aço já vem pela borracha → Nether). | Removida (só a dependência local; a quest não muda). |

Revisadas sem mudança: 24 quests.
