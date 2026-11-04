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
- [ ] Undergarden: o Catalisador acende o portal. **Anote se o Catalisador é gasto** (ponto em aberto do Plano 2).
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
- [ ] Morte: a tumba guarda os itens e o dono consegue recuperá-los.

Anote qualquer falha com o nome da quest (aparece no topo da janela da quest) e me mande.
