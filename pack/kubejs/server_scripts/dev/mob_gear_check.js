// Ecos do Selo — DEV ONLY. "/kubejs custom_command ecos_gear_check" confere o equipamento dos zumbis e
// esqueletos carregados no Overworld: só itens vanilla (minecraft:), sem os utilitários que os mobs usariam; nada de mochila.
// Lido por tests/test_mob_gear.py.
const ECOS_GEAR_BAD = ['minecraft:lava_bucket', 'minecraft:tnt', 'minecraft:ender_pearl', 'minecraft:flint_and_steel',
  'minecraft:enchanted_book']
ServerEvents.customCommand('ecos_gear_check', event => {
  if (!JsonIO.read('kubejs/config/dev.json')) return
  const Slot = Java.loadClass('net.minecraft.world.entity.EquipmentSlot')
  let total = 0, equipped = 0, bad = [], types = {}, itemsOnFloor = []
  event.server.overworld().getEntities().forEach(e => {
    if (Math.abs(e.x - 8.5) < 3 && Math.abs(e.z - 8.5) < 3) types[String(e.type)] = (types[String(e.type)] || 0) + 1
    if (String(e.type) == 'minecraft:item' && Math.abs(e.x - 8.5) < 3 && Math.abs(e.z - 8.5) < 3) itemsOnFloor.push(String(e.item.id))
    if (['minecraft:zombie', 'minecraft:skeleton'].indexOf(String(e.type)) < 0) return  // só os mobs invocados no teste
    total++
    let any = false
    Slot.values().forEach(s => {
      let st = e.getItemBySlot(s)
      if (st.isEmpty()) return
      any = true
      let id = String(st.getId())
      if ((!id.startsWith('minecraft:') || ECOS_GEAR_BAD.indexOf(id) >= 0) && bad.indexOf(id) < 0) bad.push(id)
    })
    if (any) equipped++
  })
  event.server.tell(`ECOS_GEAR total=${total} equipped=${equipped} bad=[${bad.join(',')}]`)
  console.info(`ECOS_GEAR_TYPES ${JSON.stringify(types)} items=${JSON.stringify(itemsOnFloor)}`)
  console.info(`ECOS_GEAR total=${total} equipped=${equipped} bad=[${bad.join(',')}]`)
})

// causa da morte de zumbis/esqueletos (diagnóstico do teste)
EntityEvents.death(event => {
  if (!JsonIO.read('kubejs/config/dev.json')) return
  let t = String(event.entity.type)
  if (t != 'minecraft:zombie' && t != 'minecraft:skeleton') return
  let src = event.source
  console.info(`ECOS_GEAR_DEATH ${t} by ${src.getType()} actor=${src.actual ? src.actual.type : '-'}`)
})
