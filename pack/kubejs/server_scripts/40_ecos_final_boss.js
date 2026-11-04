// Ecos do Selo — o Arauto do Eco: cataclysm:the_harbinger invocado pelo ritual ecos:ritual_entidade (tag ecos_final).
// Reforço (vida efetiva ×3, dano ×1,5): startup_scripts/ecos_final_boss_damage.js. Na morte, cada jogador a até 64 blocos recebe o
// Eco do Arauto; jogadores mortos e o caso sem ninguém perto deixam o Eco no chão, sem despawn. Usar o Eco escolhe o desfecho:
// clique direito = Marca do Silêncio (selar); agachado + clique direito = Marca do Eco (absorver).
const ECOS_FINAL_TAG = 'ecos_final'

EntityEvents.death(event => {
  try {
    let e = event.entity
    if (!e.tags.contains(ECOS_FINAL_TAG)) return
    let drops = 0
    let given = 0
    event.server.players.forEach(p => {
      if (p.level.dimension != e.level.dimension || p.distanceToEntity(e) > 64) return
      if (!p.isAlive() || p.isSpectator()) { drops++; return }  // morto: o inventário some ao renascer
      p.give(Item.of('ecos:eco_do_arauto'))
      p.tell(Text.of('O Arauto cai. O eixo para de girar. Use o Eco do Arauto para escolher.').darkAqua())
      p.tell(Text.of('Clique direito: selar. Agachado + clique direito: absorver.').gray())
      given++
    })
    if (given === 0 && drops === 0) drops = 1
    for (let i = 0; i < drops; i++) {
      let item = event.level.createEntity('minecraft:item')
      item.setItem(Item.of('ecos:eco_do_arauto'))
      item.setPos(e.x, e.y + 0.5, e.z)
      item.setUnlimitedLifetime()
      item.spawn()
    }
    console.info(`[ecos] Arauto do Eco morreu: ${given} receberam o Eco, ${drops} no chão`)
  } catch (err) {
    console.error('[ecos] morte do Arauto falhou: ' + err)
  }
})

ItemEvents.rightClicked('ecos:eco_do_arauto', event => {
  if (String(event.hand) != 'MAIN_HAND') return  // sem isso a mão secundária também dispara
  let p = event.player
  let absorver = p.isCrouching()
  event.item.shrink(1)
  p.give(Item.of(absorver ? 'ecos:poder_absorvido' : 'ecos:selo_restaurado'))
  p.tell(absorver
    ? Text.of('Você segura o eixo que Ilse soltou. Tudo o que soa agora obedece a você.').darkPurple()
    : Text.of('O eixo para. Ilse Varrow descansa. O mundo fica quieto.').aqua())
  event.cancel()
})
