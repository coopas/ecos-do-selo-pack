// Ecos do Selo — DEV ONLY. Só roda se kubejs/config/dev.json existir (o script vai no pack, a flag não).
// Gera kubejs/exported/registry_dump.json e recipe_dump.json para os validadores (tools/registry.py, tools/recipes.py).
// Roda em ServerEvents.loaded: as receitas já incluem as mudanças feitas pelos scripts do pack.
ServerEvents.loaded(event => {
  const flag = JsonIO.read('kubejs/config/dev.json')
  if (!flag) return
  const R = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries')
  const ids = reg => {
    const out = []
    reg.keySet().forEach(k => out.push(String(k)))
    return out
  }
  const tagsOf = reg => {
    const tags = {}
    reg.getTags().forEach(pair => {
      const members = []
      pair.getSecond().forEach(holder => members.push(String(holder.unwrapKey().get().location())))
      tags[String(pair.getFirst().location())] = members
    })
    return tags
  }
  const itemTags = tagsOf(R.ITEM)
  // EMC real do ProjectE: nenhum item do GregTech pode ter valor (trava da alquimia proibida)
  const emcProxy = Java.loadClass('moze_intel.projecte.api.ProjectEAPI').getEMCProxy()
  let emcGtNonzero = []
  R.ITEM.keySet().forEach(key => {
    if (String(key.getNamespace()) !== 'gtceu') return
    let v = emcProxy['getValue(net.minecraft.world.item.ItemStack)'](Item.of(String(key)))
    if (v > 0) emcGtNonzero.push(String(key))
  })
  JsonIO.write('kubejs/exported/registry_dump.json', {
    items: ids(R.ITEM),
    fluids: ids(R.FLUID),
    entities: ids(R.ENTITY_TYPE),
    item_tags: itemTags,
    block_tags: tagsOf(R.BLOCK),
    emc_gtceu_nonzero: emcGtNonzero,
    emc_sanity_dirt: Number(emcProxy['getValue(net.minecraft.world.item.ItemStack)'](Item.of('minecraft:dirt')))
  })

  const server = event.server
  const access = server.registryAccess()
  let recipes = []
  let errors = []
  server.getRecipeManager().getRecipes().forEach(r => {
    let outputs = []
    try {
      let stack = r.getResultItem(access)
      if (stack && !stack.isEmpty()) outputs.push(String(R.ITEM.getKey(stack.getItem())))
    } catch (e) {
      if (errors.length < 5) errors.push('output ' + r.getId() + ': ' + e)
    }
    let inputs = []
    try {
      r.getIngredients().forEach(ing => {
        if (ing.isEmpty()) return
        let parsed = JSON.parse(String(ing.toJson().toString()))
        if (!Array.isArray(parsed)) parsed = [parsed]
        let alts = []
        parsed.forEach(o => {
          if (o.item) alts.push(String(o.item))
          else if (o.tag) alts.push('#' + o.tag)
        })
        if (alts.length) inputs.push(alts)
      })
    } catch (e) {
      if (errors.length < 5) errors.push('input ' + r.getId() + ': ' + e)
    }
    recipes.push({ id: String(r.getId()), type: String(r.getType()), outputs: outputs, inputs: inputs })
  })
  JsonIO.write('kubejs/exported/recipe_dump.json', { recipes: recipes, errors: errors }) // JsonIO ignora array na raiz
  console.info(`[ecos] dumps escritos: ${Object.keys(itemTags).length} item tags, ${recipes.length} receitas`)
})
