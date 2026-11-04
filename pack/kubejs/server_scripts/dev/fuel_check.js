// Ecos do Selo — DEV ONLY. "/kubejs custom_command ecos_fuel_check" confere as receitas ecos:fuel/* registradas no
// RecipeManager (contra as que 15_ecos_fuels.js criou) e se os fluidos do GT estão nas tags que o CDG lê. Lido por tests/test_fuels.py.
ServerEvents.customCommand('ecos_fuel_check', event => {
  if (!JsonIO.read('kubejs/config/dev.json')) return
  const R = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries')
  const fuels = JsonIO.read('kubejs/ecos/fuels.json')
  let receitas = 0
  event.server.getRecipeManager().getRecipes().forEach(r => { if (String(r.getId()).startsWith('ecos:') && String(r.getId()).indexOf('/fuel/') > 0) receitas++ })
  // membros reais de cada tag de fluido no registro (a mesma tag que o CDG lê em fuel_type/*.json)
  let members = {}
  R.FLUID.getTags().forEach(pair => {
    let list = []
    pair.getSecond().forEach(holder => list.push(String(holder.unwrapKey().get().location())))
    members[String(pair.getFirst().location())] = list
  })
  let missing = []
  for (let tag in fuels.fluid_tags) {
    fuels.fluid_tags[tag].forEach(f => {
      if ((members[tag] || []).indexOf(f) < 0) missing.push(`${f}@${tag}`)
    })
  }
  let tagsOk = missing.length == 0
  let line = `ECOS_FUEL receitas=${receitas} esperadas=${global.ecosFuelExpected} tags_ok=${tagsOk} missing=[${missing.join(',')}]`
  event.server.tell(line)
  console.info(line)
})
