// Ecos do Selo — fragmentos do selo em TODA morte do chefe do ato (qualquer causa). Fonte: kubejs/ecos/boss_drops.json
// - Cada jogador vivo a até 64 blocos (mesma dimensão) recebe o próprio fragmento direto no inventário
//   (progresso é individual; inventário cheio = cai aos pés). Nada cai no vazio do Aether.
// - Sem ninguém perto: o fragmento cai no lugar do chefe, sem despawn.
// - Clones do Lich (NBT ShadowClone) não contam.
let ECOS_BOSS_DROPS = JsonIO.read('kubejs/ecos/boss_drops.json')
if (!ECOS_BOSS_DROPS) throw new Error('[ecos] kubejs/ecos/boss_drops.json ausente ou inválido: travas NÃO carregadas')

function ecosIsShadowClone(entity) {
  try {
    let nbt = entity.getNbt()
    return nbt != null && nbt.getBoolean('ShadowClone')
  } catch (e) {
    return false
  }
}

EntityEvents.death(event => {
  try {
    let entity = event.entity
    let drop = ECOS_BOSS_DROPS[String(entity.type)]
    if (!drop || ecosIsShadowClone(entity)) return
    let given = 0
    event.server.players.forEach(p => {
      if (!p.isAlive() || p.isSpectator()) return
      if (p.level.dimension != entity.level.dimension || p.distanceToEntity(entity) > 64) return
      p.give(Item.of(drop))
      given++
    })
    if (given === 0) {
      let item = event.level.createEntity('minecraft:item')
      item.setItem(Item.of(drop))
      item.setPos(entity.x, entity.y + 0.5, entity.z)
      item.setUnlimitedLifetime()
      item.spawn()
    }
    console.info(`[ecos] ${entity.type} morreu: ${drop} para ${given} jogador(es)${given === 0 ? ' (no chão)' : ''}`)
  } catch (e) {
    console.error('[ecos] drop de fragmento falhou: ' + e)
  }
})
