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
| `ato2/componentes` | **Aviso do `questcheck`**: o transistor leva chapa de silício (HV). O capacitor leva folha de alumínio, que não estava nos ancestrais. | Transistor trocado por indutor (anel de aço, fio fino de cobre, polietileno; 120 EU/t). Dependência nova em `aluminio`. Descrição diz da folha de alumínio e de onde vem o polietileno. Aviso zerado. |
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

Conferido no jar do Iron's Spellbooks (receitas, tabelas de loot, guia). A runa vazia não tem receita: só sai de baú. A essência de cinzas só vem do Nether: Cavaleiros Antigos e o chefe Eco de Tyros (`fire_boss`), recompensa do spawner da Cidadela e baús de sepultura do Posto da Legião (`burial_loot`). O minério de mitril está em `forge:needs_netherite_tool`.

| quest | problema | correção |
|---|---|---|
| `side_irons/mitril` | O minério (y -63 a -38) só cede a picareta de netherita; nada avisava. | Descrição: altura, picareta de netherita, de onde vêm os detritos e o molde. |
| `side_irons/lingote_mitril` | Bruto vira sucata no alto-forno; 4 sucatas = 1 lingote. | Descrição. |
| `side_irons/livro_ouro` | Dependia de `lingote_mitril`, mas a receita não usa mitril (ouro, essência arcana, couro de hoglin). Isso prendia `ato3/solenne` à picareta de netherita. | Dependência em `lingote_mitril` removida; descrição diz de onde vem o couro. |
| `side_irons/livro_diamante` | Couro de hoglin, tecido mágico, diamantes, livro encantado. | Descrição. |
| `side_irons/caldeirao` | Pede essência de cinzas (Cidadela e Posto da Legião, no Nether). | Descrição com as fontes. |
| `side_irons/orbe` | Pede 4 essências de cinzas e 4 lingotes arcanos (8 essências arcanas cada). | Descrição. |
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
| `side_occultism/giz_vermelho` | A essência de afrit só cai do afrit selvagem. O ritual (`summon_wild_afrit`) começa com o livro do afrit vinculado e pede pentáculo de giz branco e roxo com caveiras de esqueleto e de esqueleto wither, mais uma vaca. A quest do livro (`afrit`) vinha **depois** do giz: ordem impossível. | Ordem trocada: `afrit` depende de `giz_roxo`, `giz_vermelho` depende de `afrit`, e `mestre_ocultista` passa a depender de `giz_vermelho` em vez de `afrit`. Descrição com o ritual. |
| `side_occultism/afrit` | Ver acima. O livro precisa ser vinculado no Dicionário para abrir o ritual. | Dependência trocada de `giz_vermelho` para `giz_roxo`; descrição. |
| `side_occultism/prata` | Não dizia onde. | Descrição: veio de galena ou minério de prata do Occultism. |

Revisadas sem mudança: 11 quests.

## Ato III (`30_ato3`)

Conferido nos jars do Aether 1.5.2 e do Blue Skies 1.3.31 (worldgen, loot, tags, código dos chefes e das ferramentas). Dois fatos escondidos pesam aqui. Primeiro: no Everbright e no Everdawn, as picaretas de fora (de ferro para cima, inclusive as do GregTech e do Aether) quebram devagar e colhem como madeira (`PlayerHooks.isBreakingNerfed`); as vanilla de pedra, ouro e madeira escapam. Segundo: a falsita e o vêntio só nascem na pedra-turquesa (Everbright) e a horizonita só na pedra-lunar (Everdawn), o contrário do que as quests mostravam.

| quest | problema | correção |
|---|---|---|
| `ato3/horizonita` | Pendurada no Everbright, mas o minério só gera na pedra-lunar do Everdawn (`ore_everdawn_horizonite`). A forja ainda leva pedregulho lunar. | Dependência trocada de `everbright` para `everdawn`; a descrição diz onde nasce. |
| `ato3/falsita`, `ventio` | Penduradas no Everdawn, mas só geram na pedra-turquesa do Everbright (`ore_everbright_falsite`, `ore_everbright_ventium`). | Dependência trocada de `everdawn` para `everbright`; descrição. |
| `ato3/everbright` | A descrição dizia "portal de pedra-de-neve", mas a moldura é de tijolos de pedra-turquesa. Também não dizia como achar a primeira moldura. | Descrição corrigida: tijolos de pedra-turquesa. Toda casa do Porteiro tem uma moldura pronta, de um dos dois céus (12 tijolos; o processador `swap_portal` troca lunar por turquesa). |
| `ato3/everdawn` | Não dizia de que é a moldura. | Descrição: tijolos de pedra-lunar. |
| `ato3/outros_ceus` | Dizia que o isqueiro pede outro Fragmento das Profundezas, mas o Porteiro também vende o isqueiro por esmeraldas (`zeal_lighter_cost`). | A descrição dá os dois caminhos e lembra que, sem a Chave Celeste, nenhum portal aceita. |
| `ato3/piropo` | As picaretas de fora não colhem minério nos dois céus, e nada avisava. | Descrição: usar picareta de pedra ou as do próprio céu. |
| `ato3/diopsidio` | Diopsídio e charoíta pedem picareta de nível 2. Lá dentro, só a de aquita (ou melhor) serve. | Descrição. |
| `ato3/turquesa` | Sem toque de seda, a pedra cai como pedregulho (`blocks/turquoise_stone`). | Descrição: o forno devolve a pedra. |
| `ato3/pedra_lua` | O minério solta lascas, não a pedra. | Descrição: quatro lascas fazem uma pedra. |
| `ato3/invocador` | Nada disso era dito: ele mora no topo da Masmorra Ofuscante, a pedra-chave pede quatro chaves dos baús da masmorra, e ele só fica vulnerável quando conjura. | Descrição. |
| `ato3/esmagador` | Fica na Masmorra da Natureza (Everbright), com a mesma regra das quatro chaves. Só fica vulnerável depois de perder uma parede. | Descrição. |
| `ato3/almas` | O fragmento de alma não vem só da bolsa do Invocador: também cai de espíritos de gelo e de polargeists. | Descrição. |
| `ato3/solenne` | Mecânica escondida: o Espírito do Sol é imune a tudo que não seja frio até ser congelado pelos próprios cristais de gelo (`SunSpirit.isInvulnerableTo`). | Descrição: rebater os cristais de gelo e golpear enquanto ele está congelado. |
| `ato3/slider` | Só toma dano de picareta (`aether:slider_damaging_items`). | Descrição. |
| `ato3/valquirias` | A Rainha só luta com 10 medalhas, e cada valquíria deixa uma. | Descrição. |
| `ato3/paraquedas` | O paraquedas dourado leva 4 nuvens douradas, que são raras (1 em 75 chunks, y 96 a 128). A quest anterior só pede as frias e as azuis. | Descrição. |

Revisadas sem mudança: 27 quests.

## Caminho — A Rede Que Lembra (`31_side_ae2`)

Conferido no jar do AE2 15.4.12 e na config (`spawnPressesInMeteorites: true`). A energia do GregTech entra na rede pelo cabo (`nativeEUToFE: true`).

| quest | problema | correção |
|---|---|---|
| `side_ae2/meteorito` | Mandava usar a bússola de meteorito, que é uma bússola carregada no carregador, e o carregador é uma quest posterior. | Descrição: o carregador leva só ferro e cobre e funciona com manivela, então dá para fazer antes. |
| `side_ae2/silicio` | As prensas só existem no Cubo Misterioso do meteorito, e nada avisava. | Descrição. |
| `side_ae2/brotos` | Não dizia que o bloco brotante impecável, quebrado, cai como defeituoso (o item da quest). | Descrição. |
| `side_ae2/carregador` | No começo não há energia para ele. | Descrição: manivela em cima. |
| `side_ae2/aceitador` | Não dizia como ligar a energia do GregTech. | Descrição: basta encostar um cabo do GregTech. |

Revisadas sem mudança: 18 quests.

## Caminho — Alta Tensão (`32_side_gt_mv_ev`)

O verificador não modela sala limpa nem a voltagem real de cada momento (o teto do Ato III é EV para tudo), e a ordem das quests não seguia o GregTech. Conferi os fatos no dump e no jar do GregTech 7.5.3 (as receitas com `.cleanroom(CLEANROOM)` em `CircuitRecipes`):
- Kanthal (1800 K) e aço inox (1700 K) pedem 480 EU/t. Com duas escotilhas de energia MV o alto-forno roda receitas HV (`getMaxVoltage`: mais de uma escotilha do tier mais alto dá tier+1).
- Todo circuito EV pede sala limpa (estação de trabalho, nano e quântico). O congelador a vácuo leva 3 circuitos EV, a torre de destilação 4 e a montadora de circuitos HV 2. Mesmo assim, o congelador vinha logo depois do inox.
- A montadora de circuitos LV leva circuitos MV, e a MV leva circuitos HV. O circuito integrado avançado (HV, 30 EU/t) sai da LV; o microprocessador (60 EU/t) só sai da MV. Mas a quest do circuito avançado dependia do microprocessador e da montadora HV, a ordem contrária.
- A sala limpa leva 2 motores HV e 1 circuito HV. A multi-fornalha, o compressor de implosão, o reator grande e a turbina HV também levam circuitos HV.
- O reator grande leva canos de PTFE, e o PTFE pede reator químico HV (240 EU/t). As quests estavam na ordem contrária.
- O titânio (1941 K) já sai com bobinas de kanthal. O nicromo pede 2700 K e 1920 EU/t (duas escotilhas HV). Os dois lingotes saem quentes, e só o congelador a vácuo esfria. O fio supercondutor do gerador de campo HV pede 3300 K (bobinas de nicromo). O olho quântico pede radônio, que sai do reator grande a partir de plutônio e urânio do End.

| quest | problema | correção |
|---|---|---|
| `side_gt_mv_ev/kanthal` | Pede 480 EU/t sem dizer como, e o lingote sai quente. | Dependência trocada de `inicio` para `banho`. A descrição explica as duas escotilhas MV e o banho químico. |
| `side_gt_mv_ev/inox` | Pede 480 EU/t sem dizer como. | Descrição. |
| `side_gt_mv_ev/circuito_avancado` | Dependia do microprocessador e da montadora HV, que vêm depois dele. | Dependências trocadas para `boule`, `gravador`. Descrição: montadora LV, chips do gravador, silício a 2273 K. |
| `side_gt_mv_ev/microprocessador` | A montadora MV pede circuitos HV. | Dependências trocadas de `boule`, `gravador` para `circuito_avancado` (mantém `placa_plastico`); descrição. |
| `side_gt_mv_ev/sala_limpa` | Pede motores e circuito HV. A partir dela os circuitos EV ficam possíveis. | Dependência trocada de `casco_hv` para `motor_hv`, `microprocessador`; descrição. |
| `side_gt_mv_ev/congelador` | Leva 3 circuitos EV, mas dependia só do inox. | Dependência trocada de `inox` para `sala_limpa`; descrição. |
| `side_gt_mv_ev/destilaria` | Leva 4 circuitos EV e bombas HV, mas dependia da pirólise e do reator MV. | Dependência trocada para `sala_limpa`; descrição. |
| `side_gt_mv_ev/montadora_circuito` | Leva 2 circuitos EV e um emissor HV, mas dependia só do motor HV. | Dependência trocada de `motor_hv` para `escotilha`, `emissor_hv`; descrição. |
| `side_gt_mv_ev/escotilha` | É montada a 480 EU/t com chip LPIC, e esse chip só é cortado na sala limpa. | Dependência trocada de `casco_hv` para `sala_limpa`; descrição. |
| `side_gt_mv_ev/titanio` | Dependia do nicromo, mas o kanthal basta. Precisa do congelador a vácuo. | Dependências trocadas de `nicromo`, `congelador`, `escotilha` para só `congelador`; descrição. |
| `side_gt_mv_ev/nicromo` | A descrição dizia "calor para o titânio", o que é falso. Pede 1920 EU/t e o congelador. | Dependência trocada de `inox` para `congelador`, `escotilha`; descrição. |
| `side_gt_mv_ev/campo_hv` | O fio supercondutor pede bobinas de nicromo, e o olho quântico pede radônio. | Dependência trocada de `emissor_hv` para `nicromo`, `reator_grande`; descrição. |
| `side_gt_mv_ev/ptfe`, `reator_grande` | Estavam em ordem contrária: o reator grande leva canos de PTFE. | `ptfe` passa a depender de `sala_limpa` (antes `reator_grande`). `reator_grande` passa a depender de `ptfe` (antes `inox`, `reator_mv`). Descrições. |
| `side_gt_mv_ev/nano` | A lâmina nano pede 1920 EU/t e sala limpa, e o nano sai da montadora HV. | Dependências trocadas de `circuito_avancado`, `sala_limpa` para `montadora_circuito`, `reator_grande`; descrição. |
| `side_gt_mv_ev/multi_fornalha`, `implosao` | Levam 3 circuitos HV, mas dependiam do kanthal ou do inox. | Dependência trocada para `circuito_avancado`; descrição. |
| `side_gt_mv_ev/turbina_hv`, `mineradora` | Levam circuitos e motores HV. | Dependências trocadas para `sala_limpa` (`turbina_hv` mantém `turbina_gas`). |
| `side_gt_mv_ev/turbina_gas` | Dependia da torre de destilação (EV), mas a turbina MV queima o gás de madeira e de carvão da pirólise. | Dependência trocada de `destilaria` para `pirolise`; descrição. |

O `LIMITES` de `side_gt_mv_ev` no `layoutcheck` continua em 5 cruzamentos; só o comentário foi atualizado.

Revisadas sem mudança: 22 quests.
