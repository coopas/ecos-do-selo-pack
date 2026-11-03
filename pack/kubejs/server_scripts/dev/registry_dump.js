// Ecos do Selo — DEV ONLY. Só roda se kubejs/config/dev.json existir (nunca vai no pack).
// Gera kubejs/exported/registry_dump.json para os validadores de quests/receitas (tools/registry.py).
ServerEvents.loaded(event => {
  const flag = JsonIO.read('kubejs/config/dev.json')
  if (!flag) return
  const R = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries')
  const ids = reg => {
    const out = []
    reg.keySet().forEach(k => out.push(String(k)))
    return out
  }
  const itemTags = {}
  R.ITEM.getTags().forEach(pair => {
    const members = []
    pair.getSecond().forEach(holder => members.push(String(holder.unwrapKey().get().location())))
    itemTags[String(pair.getFirst().location())] = members
  })
  JsonIO.write('kubejs/exported/registry_dump.json', {
    items: ids(R.ITEM),
    fluids: ids(R.FLUID),
    entities: ids(R.ENTITY_TYPE),
    item_tags: itemTags
  })
  console.info(`[ecos] registry dump escrito: ${Object.keys(itemTags).length} tags`)
})
