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

## Ato II (`20_ato2`)

Contexto conferido no dump: o lingote de silício do GregTech sai do alto-forno a 2273 K (`gtceu:electric_blast_furnace/blast_silicon`); a bobina de cuproníquel dá 1800 K e a de kanthal (2700 K) só se faz com o alto-forno em HV (`blast_kanthal`, 480 EU/t). Lingote de silício, chapa e transistor são da era HV.

| quest | problema | correção |
|---|---|---|
| `ato2/silicio` | **Aviso do `questcheck`**: lingote de silício pede bobinas acima do Ato II (MV). | Task trocada (slug mantido) por 16 lâminas de silício (`gtceu:silicon_wafer`): monocristal no alto-forno a 1784 K (cuproníquel serve, 120 EU/t) e cortador. Descrição dá o caminho (pó de silício da areia, arseneto de gálio, de onde vêm gálio e arsênio). Aviso zerado. |
| `ato2/componentes` | **Aviso do `questcheck`**: o transistor leva chapa de silício (HV). | Transistor trocado por indutor (anel de aço, fio fino de cobre, polietileno; 120 EU/t). Descrição diz de onde vem o polietileno. Aviso zerado. |
| `ato2/aluminio` | Não dizia de onde vem o alumínio. | Descrição: eletrólise de safira (veio fundo) ou rubi (veio de redstone). |
| `ato2/emissor_mv` | O emissor MV leva esmeralda impecável, que só sai do peneirador (o gravador a laser é HV). | Descrição: minério purificado de esmeralda no peneirador, veio de berílio do Nether (y 5 a 30). |
| `ato2/froststeel` | Não dizia onde está o minério. | Descrição: na shiverstone. |
| `ato2/tocha_fragmento` | A tocha leva estilhaço utérico, que cai dos mobs podres (não dos bulbos, que eram a dependência); 16 tochas = 16 estilhaços. | Pede 8; descrição diz quem deixa cair. |
| `ato2/lingote_esquecido` | O guardião deixa 4 a 16 pepitas; 2 lingotes = 18 pepitas, mais de uma luta na média. | Pede 1 lingote; descrição explica as pepitas. |
| `ato2/sculk`, `sensor`, `catalisador_sculk` | Sculk, sensor e catalisador só caem com Toque Suave; nada avisava. | Descrição: encantamento ou o glifo Extrair do Ars (receita: esmeralda) com Quebrar. |
| `ato2/eco` | Não dizia onde. | Descrição: baús das Cidades Antigas. |
| `ato2/po_alma` | Não dizia de onde. | Descrição: sanguessugas e snappers de sculk, baús dos templos (tabelas de loot do Deeper and Darker). |
| `ato2/ressonario` | Chamado de mineral, mas só cai da gosma (sludge) do Outro Lado. | Descrição corrigida. |
| `ato2/eco_reforcado` | Cada eco reforçado leva 4 carapaças; 2 = 8 carapaças, e o Cego deixa 1 a 3 por morte. | Pede 1; descrição com a receita. |

Revisadas sem mudança: 32 quests.

## Caminho — A Fonte (`21_side_ars`)

Conferido no jar da Ars Nouveau (receitas de glifo, imbuição e aparato; textos do livro). Sem TerraBlender no pack, a floresta de archwood não gera. A câmara de imbuição junta fonte sozinha ("will passively accumulate source"); as essências gastam 2000 de fonte cada, com os outros ingredientes em pedestais arcanos colados à câmara.

| quest | problema | correção |
|---|---|---|
| `side_ars/madeira_arcana` | O texto falava de um lugar "onde a fonte é forte"; aqui só há árvores soltas e raras. | Descrição: árvores raras em qualquer bioma; guardar as mudas. |
| `side_ars/mesa_escriba` | Glifos pedem itens e experiência; nada avisava. | Descrição. |
| `side_ars/gema_fonte` | Não dizia que lápis-lazúli também serve, nem que a câmara funciona sem jarro. | Descrição. |
| `side_ars/essencias` | As essências pedem pedestais arcanos em volta da câmara, mas a quest vinha antes dos pedestais. | Dependência trocada de `gema_fonte` para `pedestal`; descrição com a montagem e o custo de fonte. |
| `side_ars/aparato` | Com a mudança acima, a dependência em `pedestal` ficou redundante. | Removida (fica `essencias`, que já vem dos pedestais). |
| `side_ars/dano` | O glifo Ferir pede essência de terra (câmara + pedestais) e 3 espadas de ferro; abria logo após a mesa. | Dependência nova em `essencias`; descrição com os ingredientes. |
| `side_ars/curar` | O glifo Curar pede essência de abjuração, melancias reluzentes e maçã dourada. | Dependência nova em `essencias`; descrição. |
| `side_ars/amplificar` | Pede uma picareta de diamante. | Descrição. |
| `side_ars/wilden` | O espinho só cai do Defensor, que só vive em covis de biomas frios. | Descrição. |
| `side_ars/livro_aprendiz` | Pede obsidiana, 3 diamantes, 2 blocos de quartzo e 2 varas de blaze. | Descrição. |
| `side_ars/starbuncle` | O texto mandava dar pepita de ouro; isso dá um token, e o amuleto sai do aparato (token + 4 ouros). Dependia do livro, não do aparato. | Dependência trocada de `livro_aprendiz` para `aparato`; descrição com o caminho. |
| `side_ars/cinto` | A essência de ar leva asa de wilden. | Descrição. |
| `side_ars/tunica` | A fibra de magebloom vem de sementes feitas no aparato. | Descrição. |
| `side_ars/arquimago` | Pede estrela do Nether (Wither), totem e o tributo wilden, que só cai da Quimera invocada por ritual. Nada avisava. `ato4/ignaz` e `ato5/bloco_fonte` dependem dela, então fica onde está. | Descrição com os três itens e onde achar. |

Revisadas sem mudança: 14 quests.

## Caminho — Pergaminhos e Runas (`22_side_irons`)

Conferido no jar do Iron's Spellbooks (receitas, tabelas de loot, guia). A runa vazia não tem receita: só sai de baú. A essência de cinzas só cai dos Cavaleiros Antigos (Cidadela e Posto da Legião, estruturas do Nether). O minério de mitril está em `forge:needs_netherite_tool`.

| quest | problema | correção |
|---|---|---|
| `side_irons/mitril` | O minério (y -63 a -38) só cede a picareta de netherita; nada avisava. | Descrição: altura, picareta de netherita, de onde vêm os detritos e o molde. |
| `side_irons/lingote_mitril` | Bruto vira sucata no alto-forno; 4 sucatas = 1 lingote. | Descrição. |
| `side_irons/livro_ouro` | Dependia de `lingote_mitril`, mas a receita não usa mitril (ouro, essência arcana, couro de hoglin). Isso prendia `ato3/solenne` à picareta de netherita. | Dependência em `lingote_mitril` removida; descrição diz de onde vem o couro. |
| `side_irons/livro_diamante` | Couro de hoglin, tecido mágico, diamantes, livro encantado. | Descrição. |
| `side_irons/caldeirao` | Pede essência de cinzas (Cavaleiros Antigos, Nether). | Descrição. |
| `side_irons/orbe` | Pede 4 essências de cinzas. | Descrição. |
| `side_irons/runa_vazia` | Sem receita; só em baús (catacumbas, Cidadela, fortalezas, bibliotecas). | Descrição. |
| `side_irons/runa_fogo`, `runa_gelo`, `runa_sagrada` | Os focos (vara de blaze; osso congelado, dos strays; pérola divina, ouro + ametista) não eram ditos. | Descrições. Piromantes e criomantes deixam runas da sua escola (guia do mod; o drop está no código das entidades). |
| `side_irons/orbe_fogo`, `orbe_mana` | Cada um leva 8 runas (8 runas vazias de baú). São folhas: nada depende delas. | Descrição avisa e aponta o atalho (piromantes). Quantidade mantida, por ser o próprio item. |
| `side_irons/piromante` | Leva o peitoral de mago (8 tecidos mágicos). | Descrição. |
| `side_irons/forja` | Obsidiana chorona não tem receita. | Descrição: bastiões, portais em ruínas, troca com piglins. |

Revisadas sem mudança: 10 quests.

## Caminho — Os que Servem (`23_side_occultism`)

Conferido no jar do Occultism 1.158 (receitas, rituais, pentáculos do Dicionário dos Espíritos). Nesta versão o giz branco é pedra de outro mundo assada + cinzas de tora de outro mundo (o sebo vai só nas velas); a pedra de outro mundo sai do fogo espiritual (andesito), sem óculos; os óculos pedem um ritual com o foliot (pentáculo de giz branco e dourado); a picareta infundida é ritual do djinni (giz roxo); o iésnio só se vê com os óculos e só se quebra com a picareta infundida. A ordem antiga das quests (óculos logo no início, pedra depois dos óculos, fogo depois do giz) não deixava o jogador seguir.

| quest | problema | correção |
|---|---|---|
| `side_occultism/fogo_espiritual` | Vinha depois do giz branco, mas o giz (e a pedra) precisam do fogo. | Dependência trocada de `giz_branco` para `datura`; descrição corrigida (jogar datura no chão e acender com isqueiro). |
| `side_occultism/pedra_outra` | Dependia dos óculos; a pedra sai do andesito no fogo espiritual. | Dependência trocada de `oculos` para `fogo_espiritual`; descrição. |
| `side_occultism/giz_branco` | Dependia do sebo, que não entra no giz; pede pedra de outro mundo e cinzas, e o caminho da tora (Terceiro Olho) não era dito. | Dependência trocada de `sebo` para `pedra_outra`; descrição com o passo a passo. |
| `side_occultism/sebo` | "Base para giz" não vale mais. | Descrição: base das velas; quais animais. |
| `side_occultism/oculos` | Abria logo no início, mas as lentes infundidas pedem o ritual do foliot (giz dourado). | Dependência trocada de `datura` para `giz_dourado`; descrição. |
| `side_occultism/varinha` | Dependia dos óculos; a varinha só leva gema sintonizada. | Dependência trocada para `gema_espiritual`. |
| `side_occultism/gema_espiritual` | Não dizia que é diamante no fogo. | Descrição. |
| `side_occultism/livro_vinculo`, `foliot` | O livro vinculado sai juntando o livro ao Dicionário; nada avisava. | Descrições. |
| `side_occultism/picareta_infundida` | Dependia só da gema, mas é ritual do djinni (pentáculo com giz roxo). | Dependência trocada para `giz_roxo`; descrição. |
| `side_occultism/iesnio` | Precisa dos óculos (para ver) e da picareta infundida (para quebrar). | Dependências trocadas de `djinni` para `picareta_infundida` e `oculos`; descrição. |
| `side_occultism/minerador` | O minerador sai de ritual com lâmpada mágica (leva iésnio) e picareta de iésnio, mas dependia só do foliot. | Dependência trocada para `picareta_iesnio`; descrição. |
| `side_occultism/giz_roxo` | **Erro do `questcheck`**, lacuna do dump: a moagem do Occultism com saída em tag virou `minecraft:barrier`. No jar, `occultism:crushing/end_stone_dust` mói `#forge:end_stones` em `#forge:dusts/end_stone` (= `occultism:crushed_end_stone`), feito pelo foliot triturador (`summon_foliot_crusher`, pentáculo só de giz branco, que vem antes). O pó de obsidiana sai do macerador do GregTech ou das rodas do Create. O Fim abre com o Nether (`ato1/nether`). Dá para fazer neste ponto. | Quest mantida; descrição dá o caminho. **O erro continua no `questcheck` até o dump ler saídas em tag da moagem do Occultism.** |
| `side_occultism/giz_vermelho` | A essência de afrit só cai do afrit selvagem, invocado por ritual com caveiras. | Descrição. |
| `side_occultism/prata` | Não dizia onde. | Descrição: veio de galena ou minério de prata do Occultism. |

Revisadas sem mudança: 13 quests.
