# Ecos do Selo — checklist de playtest

O que os testes automáticos **já provaram** (não precisa repetir):
- O servidor sobe sem erros; o FTB Quests carrega **17 capítulos e 511 quests** e as 4 caixas de loot.
- Todo item, tag, entidade e dimensão das quests existe; toda task tem caminho de obtenção; não há ciclos.
- As 30 páginas do diário saem uma vez cada; nenhuma quest repetível dá moeda.
- Filtros de tag casam com todos os membros (ex.: as 17 camas).
- Em jogo: o Lich derruba o Fragmento da Floresta; fragmentos não queimam na lava; o Arauto recebe 1/3 do
  dano, causa 1,5× e deixa o Eco do Arauto ao morrer.

O que **só uma pessoa jogando** confirma. Use um mundo de teste em modo criativo e marque cada item.

## 1. Livro de quests e tags
- [ ] Abra o livro de quests (tecla padrão do FTB Quests). Os grupos *Atos*, *Caminhos* e *Loja* aparecem.
- [ ] Prólogo → "Árvores Tortas": pegue troncos de qualquer árvore. A task mostra os troncos girando (não um *smart filter*) e completa.
- [ ] Prólogo → quest da cama: faça uma cama **de cor diferente da vermelha**. A quest completa.
- [ ] Quest de madeira/tábuas: use um tipo de madeira incomum (ex.: cerejeira). A quest completa.
- [ ] Abra uma página do diário recebida como recompensa: o livro tem título, autora "Ilse Varrow" e texto em PT.

## 2. Recompensas
- [ ] Abra uma caixa de loot comum e uma lendária (recompensa ou `/ftbquests` em modo edição).
- [ ] Loja: com Fragmentos de Eco no inventário, compre "Provisões". As moedas somem e a comida chega.
- [ ] Tente comprar de novo: a quest repetível reaparece.
- [ ] Itens da loja de atos futuros ficam travados até a quest inicial do ato.

## 3. Portais e travas
- [ ] Twilight: o lago com flores **não** abre com diamante; abre com a Chave Crepuscular.
- [ ] Aether / Everbright / Everdawn: sem a Chave Celeste, a mensagem "O portal rejeita você" aparece.
      Com a chave no inventário, você entra. A volta ao Overworld sempre funciona.
- [ ] O Gatekeeper do Blue Skies vende o Zeal Lighter, mas sem a Chave Celeste não se entra.
- [ ] Undergarden: o Catalisador acende o portal (o código do mod confirma que ele **não** é gasto).
- [ ] A Pedra Filosofal não aparece no JEI como craftável antes de ter o Fragmento das Estrelas.
      Ao usá-la numa receita de pó de covalência, **ela volta para a grade?** (ponto em aberto).

## 4. Chefes (pontos em aberto do Plano 2)
- [ ] Lich: os **clones** também derrubam fragmento? (Se derrubarem, anote: seria fragmento extra.)
- [ ] Ignis: na Arena Ardente do Nether, as **Cinzas Ardentes** reinvocam o Ignis no altar de fogo.
- [ ] Warden: um segundo Warden (sculk shrieker) derruba outro Fragmento das Profundezas.

## 5. Final
- [ ] Monte o pentáculo de **espírito maior** (giz branco + roxo, crânios de esqueleto, tigela dourada),
      com 2 fragmentos de eco, 1 sino e 1 eco reforçado nas tigelas.
- [ ] Use o **Artefato do Selo** na tigela dourada: o **Arauto do Eco** aparece com o nome na barra de chefe.
- [ ] Derrote-o (criativo serve): você recebe o **Eco do Arauto** e a mensagem de escolha.
- [ ] Clique direito com o Eco → Marca do Silêncio → a quest "Feche a Porta" completa.
- [ ] Faça de novo e use agachado → Marca do Eco → a quest "Abra a Sua" completa.

## 6. Multijogador (servidor)
- [ ] Dois jogadores entram no servidor; cada um tem o próprio progresso de quests.
- [ ] Um jogador entrega itens ao outro; o outro completa a quest com eles.
- [ ] Dois jogadores perto de um chefe (ex.: a Naga): só um dá o golpe final, e a quest de matar completa para os **dois**.
- [ ] Morte: a tumba guarda os itens e o dono consegue recuperá-los.

## 7. Vapor, rotação e energia (GregTech × Create)
Os testes já mediram: motor a 32 RPM / 1920 SU com 80 mB/t; dínamo ULV 8 e LV 32 EU/t; Saída 6 mB/t por nível;
o ciclo Saída → Motor → Dínamo LV entregou 9 600 EU com 28 800 mB de vapor (perda de 33 %). Falta o que só o olho vê:
- [ ] Motor a Vapor com vapor (cano do GregTech ligado): o **eixo gira visivelmente** no motor e no eixo encostado.
- [ ] Dínamo ligado a um eixo girando: o **meio-eixo do dínamo gira** junto.
- [ ] Óculos de engenheiro no motor: mostra "Motor a Vapor do Eco", o vapor no tanque e o consumo; a capacidade (SU) bate.
- [ ] Óculos no dínamo: "Dínamo Cinético (LV)", "Tier: LV (32 V, 1 A)", a geração em EU/t e a energia guardada;
      parado aparece "Sem rotação: dínamo parado" em vermelho.
- [ ] Óculos na Saída de Vapor: nível da caldeira, mB/t de vapor; sem queimador, sem água ou com motor do Create na
      caldeira aparece o motivo em vermelho.
- [ ] Um **cabo do GregTech** encostado na face de saída do dínamo (oposta ao eixo) leva energia até uma máquina LV
      (ou um buffer de bateria) e a máquina trabalha.
- [ ] Dínamo LV encostado numa máquina ULV: ela explode (regra do GregTech; só para conferir que o aviso é verdade).
- [ ] Motor sem nada no eixo: o vapor do tanque continua baixando (gasta mesmo sem carga).
- [ ] Encha o **motor do Create: Diesel Generators** com **diesel do GregTech** (balde ou cano): ele gira.
      Gasolina do GregTech também.
- [ ] Gerador de combustão do GregTech com diesel do Diesel Generators: gera EU.
- [ ] Rodas de moer do Create com minério bruto do GregTech dão minério moído; a lavagem (ventilador + água) dá o
      purificado. No JEI, o rendimento do Create é menor que o do macerador do GregTech.
- [ ] Rodas de moer com cascalho: de vez em quando sai pó de redstone.

Anote qualquer falha com o nome da quest (aparece no topo da janela da quest) e me mande.
