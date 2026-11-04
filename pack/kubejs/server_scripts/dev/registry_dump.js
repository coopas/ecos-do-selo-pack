// Ecos do Selo — DEV ONLY. Só roda se kubejs/config/dev.json existir (o script vai no pack, a flag não).
// Gera kubejs/exported/registry_dump.json e recipe_dump.json para os validadores (tools/registry.py, tools/recipes.py).
// Roda em ServerEvents.loaded: as receitas já incluem as mudanças feitas pelos scripts do pack.
let ecosDimensions = server => {
  let out = []
  server.levelKeys().forEach(k => out.push(String(k.location())))
  return out
}

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
    dimensions: ecosDimensions(event.server),
    block_tags: tagsOf(R.BLOCK),
    emc_gtceu_nonzero: emcGtNonzero,
    emc_sanity_dirt: Number(emcProxy['getValue(net.minecraft.world.item.ItemStack)'](Item.of('minecraft:dirt')))
  })

  const server = event.server
  const access = server.registryAccess()
  let recipes = []
  let errors = []
  let gtDebug = []
  server.getRecipeManager().getRecipes().forEach(r => {
    let outputs = []
    try {
      let stack = r.getResultItem(access)
      if (stack && !stack.isEmpty()) outputs.push(String(R.ITEM.getKey(stack.getItem())))
    } catch (e) {
      if (errors.length < 5) errors.push('output ' + r.getId() + ': ' + e)
    }
    if (outputs.length === 0 && r.outputs) {
      // GregTech (GTRecipe.outputs: Map<Cap, List<Content>>) e Ars (CrushRecipe.outputs: List<CrushOutput>).
      // Em subclasses de Ingredient o Rhino não traduz getItems: no GT usa getInner() (Ingredient vanilla).
      let pushStacks = stacks => { for (let i = 0; i < stacks.length; i++) outputs.push(String(R.ITEM.getKey(stacks[i].getItem()))) }
      try {
        let outs = r.outputs
        let lists = outs.values ? outs.values() : [outs]
        lists.forEach(list => list.forEach(c => {
          let obj = c.content !== undefined ? c.content : c
          try {
            if (obj.stack !== undefined) { pushStacks([obj.stack]); return }
            if (obj.getInner) {  // GT SizedIngredient: lê o JSON do Ingredient interno (getItems não é exposto ao Rhino)
              let parsed = JSON.parse(String(obj.getInner().toJson().toString()))
              if (!Array.isArray(parsed)) parsed = [parsed]
              parsed.forEach(o => { if (o.item) outputs.push(String(o.item)); else if (o.tag) outputs.push('#' + o.tag) })
              return
            }
          } catch (e2) {
            if (gtDebug.length < 3) gtDebug.push(String(r.getId()) + ' ' + obj.getClass().getName() + ': ' + e2)
          }
        }))
      } catch (e) {
        if (errors.length < 5) errors.push('machine output ' + r.getId() + ': ' + e)
      }
    }
    if (outputs.length === 0) {
      // Ars Nouveau (imbuement, enchanting_apparatus...) guarda o resultado em campos próprios
      ;['result', 'output', 'outputStack'].forEach(name => {
        try {
          let st = r[name]
          if (typeof st === 'function') st = r[name]()  // records (Ad Astra): result() é método
          if (st && st.getItem && !st.isEmpty()) outputs.push(String(R.ITEM.getKey(st.getItem())))
        } catch (e) { /* campo inexistente */ }
      })
    }
    let inputs = []
    try {
      let ings = r.getIngredients()
      if (ings.isEmpty() && typeof r.ingredients === 'function') ings = r.ingredients()  // records (Ad Astra)
      ings.forEach(ing => {
        if (!ing.isEmpty && typeof ing.ingredient === 'function') ing = ing.ingredient()  // IngredientHolder (Ad Astra)
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
  JsonIO.write('kubejs/exported/recipe_dump.json', { recipes: recipes, errors: errors, gt_debug: gtDebug }) // JsonIO ignora array na raiz
  console.info(`[ecos] dumps escritos: ${Object.keys(itemTags).length} item tags, ${recipes.length} receitas`)
})
