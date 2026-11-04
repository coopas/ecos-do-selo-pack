// Ecos do Selo — mobs NÃO nascem com mochila do Sophisticated Backpacks (padrão do mod: 1%, com loot de baú,
// armadura extra e disco tocando). A config fica em world/serverconfig e o defaultconfigs só vale para mundo
// novo; por isso o valor é forçado aqui, o que corrige também mundos que já existem.
// O equipamento do Improved Mobs vem de config/improvedmobs/equipment.json (só itens vanilla, em níveis).
ServerEvents.loaded(event => {
  let spawn = Java.loadClass('net.p3pp3rf1y.sophisticatedbackpacks.Config').SERVER.entityBackpackAdditions
  if (spawn.chance.get() != 0) {
    spawn.chance.set(0.0)
    spawn.chance.save()
  }
  console.info(`[ecos] mochilas em mobs: chance=${spawn.chance.get()}`)
})
