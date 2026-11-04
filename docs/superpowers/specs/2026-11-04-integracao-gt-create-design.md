# Design — Integração GregTech × Create × vanilla (Ecos do Selo)

Data: 2026-11-04 · Pack: Forge 1.20.1 · GregTech CEu Modern 7.5.3 · Create 6.0.8 · KubeJS 2001.6.5

## 1. Intenção e o porquê
Os jogadores (grupo de até 7 amigos, já jogando no servidor) sentem que o GregTech e o Create "não conversam":
o vapor de um não serve ao outro, os minérios do GregTech não passam pelas máquinas do Create e itens básicos
(ferro, redstone) ficam presos atrás do GregTech. O GregTech CEu removeu a integração com o Create na versão 1.6.0,
então a ponte precisa ser feita pelo pack. O usuário quer que **os dois mods se comportem como um só**, sendo o
ponto principal **o vapor gerando energia**.

## 2. Decisões do usuário
- Integrar **tudo** do tratamento de minérios entre GregTech e Create, não só o vapor.
- O principal é **integrar vapor para gerar energia**.
- Adicionar o **Create: Diesel Generators** para gerar com diesel e gasolina, integrado aos combustíveis do GregTech.
- Manter o GregTech CEu Modern (é o "Community Edition" que o usuário citou; já é o mais novo).
- Aprovou a proposta abaixo como um todo ("creio que esteja em ordem").

## 3. Objetivos / Não-objetivos / Anti-objetivos
**Objetivos**
1. Vapor ↔ energia nos dois sentidos:
   - **Motor a Vapor do Eco** (bloco novo): consome vapor líquido do GregTech (`gtceu:steam`) por cano e gera rotação do Create.
   - **Dínamo Cinético** (bloco novo): consome rotação do Create e gera EU do GregTech, nas tiers ULV e LV.
   - **Caldeira do Create produz vapor líquido**: um bloco/saída que, acoplado a uma caldeira do Create aquecida, entrega
     `gtceu:steam` proporcional ao nível de calor da caldeira, para alimentar as máquinas a vapor do GregTech.
2. Combustíveis unificados: diesel e gasolina do Create: Diesel Generators e do GregTech são intercambiáveis; os
   motores do CDG queimam os fluidos do GregTech e os geradores de combustão do GregTech queimam os do CDG.
   (Petróleo do Ad Astra e do GregTech também convergem: `ad_astra:oil` ↔ `gtceu:oil`.)
3. Minérios: o Create processa os minérios do GregTech em todas as etapas que tem (moer, lavar, misturar, prensar),
   rendendo **menos** que as máquinas do GregTech, mas sem energia elétrica.
4. Ligas do começo pela Batedeira aquecida do Create (bronze, latão, liga vermelha, estanho-chumbo etc.).
5. Vanilla: caminho viável cedo para itens que o GregTech esconde em veios profundos — **redstone** antes da primeira
   ida ao Nether. **Ferro já tem rota na fornalha** (verificado no dump: hematita, magnetita, goethita, limonita
   amarela, pirita e areias minerais brutas viram lingote de ferro na fornalha comum), então o ferro do Prólogo não
   depende do Create; o projeto só garante que essa rota continue e que o Create também processe esses minérios.

**Não-objetivos**
- Não adicionar o Greate (muda o Create inteiro com tiers de eixo e está "em desenvolvimento").
- Não refazer a progressão de tiers do GregTech (MV+ continua exigindo o caminho do GregTech).
- Não mexer nas quests aqui: as quests novas do conteúdo integrado (decisão do usuário: **sim, criar**) entram no
  projeto "revisão de quests", que vem depois e parte do jogo já integrado.

**Anti-objetivos** (falha mesmo se "funcionar")
- **Laço de energia infinita**: nenhuma combinação vapor → rotação → EU → vapor (ou combustível) pode render mais do que entrou.
- Create virar o caminho **melhor** que o GregTech para minério: o Create é o atalho sem energia, o GregTech é o rendimento.
- Quebrar mundo existente: o servidor dos amigos já está rodando; nada pode exigir mundo novo nem apagar blocos/itens.
- Qualquer item/fluido/receita apontando para ID que não existe (crash ou receita fantasma).

## 4. Restrições
- Forge 1.20.1, Java 17. Mods novos precisam de build Forge 1.20.1 e entram via `tools/mods.csv` + `tools/add_mods.py`.
- Blocos novos vão no mod Java do pack (`tools/ecosbridge`, hoje um adaptador de filtros; compilado por `build.sh`).
  Ele passa a depender do Create e do GregTech em tempo de compilação.
- Receitas e tags via KubeJS (`pack/kubejs/server_scripts`, dados em `pack/kubejs/ecos/*.json`, padrão do pack:
  dados em JSON + script que falha alto se o JSON faltar).
- Todo ID validado contra o dump de registro (`build/registry_dump.json`) e de receitas (`build/recipe_dump.json`).
- Tudo em PT-BR (nomes, tooltips, Ponder/descrições se houver).
- Teste de verdade: boot de servidor e cliente + testes em jogo (`pytest -m ingame`) provando cada conversão.
- Commits sem coautoria do Claude; publicação (push no repo público) só com o usuário.

## 5. Números (chamada minha; o construtor pode ajustar mantendo as razões)
Referência do GregTech: 2 mB de vapor = 1 EU. Referência do Create: SU = força × RPM.
- **Motor a Vapor do Eco**: 1 motor ≈ equivalente a 1 Motor a Vapor do Create num nível de caldeira (ordem de 16 384 SU
  no máximo), consumindo vapor a uma taxa tal que **1 EU de vapor ≥ 1 EU que o Dínamo devolveria** (perda ≥ 25 % no ciclo).
- **Dínamo Cinético**: ULV (8 EU/t) e LV (32 EU/t); exige rotação mínima e consome SU proporcional; perda ≥ 25 %.
- **Saída de Vapor da caldeira do Create**: vapor por nível de calor da caldeira, calibrado para que 1 caldeira de
  nível máximo alimente ~2–4 máquinas a vapor do GregTech; a água consumida segue a da caldeira.
- **Moer (Create)**: minério bruto do GregTech → 1 minério triturado do GregTech + chance de extra (~30 %), sem subproduto.
  (Macerador do GregTech: 2 triturados + subproduto — continua melhor.)
- **Lavar (ventilador com água)**: triturado → minério purificado do GregTech (sem subproduto).
- **Prensa**: lingote → placa do GregTech, 1:1 (mesma razão da Bender/martelo).
- **Redstone cedo**: moer cascalho no Create rende pó de redstone com chance baixa (~10 %) — chamada minha;
  qualquer outra rota serve desde que seja viável antes do Nether e mais cara por unidade que o veio de redstone.

## 6. Deixado para o construtor
- IDs exatos dos fluidos e configuração de combustível do Create: Diesel Generators (verificar no jar/registro e se a
  lista de combustíveis é por tag, datapack ou config) e a forma de unificar (tag comum, receitas 1:1 ou config).
- Como acoplar a Saída de Vapor à caldeira do Create (API do `FluidTankBlockEntity`/`BoilerData`) e como o Dínamo
  expõe energia ao GregTech (capability de EU do GTCEu).
- Texturas/modelos dos 3 blocos novos (simples, no estilo do Create) e receitas de fabricação coerentes com a era
  (Motor e Dínamo craftáveis na era do vapor/LV; nada de MV).
- Quais ligas entram na Batedeira e com que calor; quais minérios do GregTech têm receita de moer/lavar (todos os que
  têm `raw_materials`/`crushed_ores`).
- Lista de testes em jogo. No mínimo: cada bloco novo convertendo de verdade; um laço completo provando perda;
  receitas do Create com minério do GregTech; motor do CDG queimando diesel do GregTech; redstone obtida cedo.

## 7. Verificação de ponta a ponta
`pytest` (unitários) + `boot_test.py server --dev` (dump novo) + `questcheck` limpo + `pytest -m ingame` com os testes
novos + `boot_test.py client` chegando ao menu. Só então o commit; o push fica com o usuário.
