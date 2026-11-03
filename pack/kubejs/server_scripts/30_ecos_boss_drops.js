// Ecos do Selo — fragmentos do selo caem em TODA morte do chefe do ato (qualquer causa), sem despawn.
// Assim um fragmento perdido sempre pode ser reobtido enfrentando o chefe de novo. Fonte: kubejs/ecos/boss_drops.json
let ECOS_BOSS_DROPS = JsonIO.read('kubejs/ecos/boss_drops.json') || {}

EntityEvents.death(event => {
  let entity = event.entity
  let drop = ECOS_BOSS_DROPS[String(entity.type)]
  if (!drop) return
  let item = event.level.createEntity('minecraft:item')
  item.setItem(Item.of(drop))
  item.setPos(entity.x, entity.y + 0.5, entity.z)
  item.setUnlimitedLifetime()
  item.spawn()
  console.info(`[ecos] ${entity.type} morreu: dropou ${drop}`)
})
