// Ecos do Selo — itens e blocos próprios. Fonte única: kubejs/ecos/items.json (também lido pelos testes Python).
let ECOS_ITEMS = JsonIO.read('kubejs/ecos/items.json').items // JsonIO não lê array na raiz

StartupEvents.registry('item', event => {
  ECOS_ITEMS.forEach(def => {
    if (def.kind !== 'item') return
    let b = event.create(def.id)
      .texture(def.texture)
      .maxStackSize(def.max_stack)
      .rarity(def.rarity)
    if (def.glow) b.glow(true)
  })
})

StartupEvents.registry('block', event => {
  ECOS_ITEMS.forEach(def => {
    if (def.kind !== 'block') return
    event.create(def.id)
      .textureAll(def.texture)
      .soundType('stone')
      .hardness(3.0)
      .resistance(6.0)
      .requiresTool(true)
      .tagBlock('minecraft:mineable/pickaxe')
      .tagBlock('minecraft:needs_iron_tool')
      .lightLevel(1.0)
  })
})
