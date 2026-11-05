// Ecos do Selo — DEV ONLY. Só roda se kubejs/config/dev.json existir (o script vai no pack, a flag não).
// Gera kubejs/exported/registry_dump.json e recipe_dump.json para os validadores (tools/registry.py, tools/recipes.py).
// Roda em ServerEvents.loaded: as receitas já incluem as mudanças feitas pelos scripts do pack.
let ecosDimensions = server => {
  let out = []
  server.levelKeys().forEach(k => out.push(String(k.location())))
  return out
}

// Coleta strings item/tag/fluid de um JSON de ingrediente (vanilla, GT SizedIngredient interno, FluidIngredient).
// Tags saem com '#'. O circuito programado do GT (sem item no JSON) vira gtceu:programmed_circuit.
let ecosJsonAlts = (json, key) => {
  let out = []
  let walk = o => {
    if (o === null || typeof o !== 'object') return
    if (Array.isArray(o)) { o.forEach(walk); return }
    if (o.type === 'gtceu:circuit') { out.push('gtceu:programmed_circuit'); return }
    if (typeof o[key] === 'string') out.push(String(o[key]))
    else if (typeof o.tag === 'string') out.push('#' + o.tag)
    Object.keys(o).forEach(k => { if (k !== 'nbt' && k !== key && k !== 'tag') walk(o[k]) })
  }
  walk(json)
  return out.filter((v, i) => out.indexOf(v) === i)
}

// Entradas/saídas do GTRecipe (Map<RecipeCapability, List<Content>>): só as capacidades 'item' e 'fluid'.
// Devolve {item: [[alts]...], fluid: [[alts]...]}; os de tick (tickInputs) entram junto.
let ecosGtContents = maps => {
  let res = { item: [], fluid: [] }
  maps.forEach(map => {
    if (!map) return
    map.forEach((cap, list) => {
      let name = String(cap.name)
      if (name !== 'item' && name !== 'fluid') return
      list.forEach(c => {
        let obj = c.content
        let ing = obj.getInner ? obj.getInner() : obj  // SizedIngredient: o Ingredient interno tem o JSON útil
        let alts = ecosJsonAlts(JSON.parse(String(ing.toJson().toString())), name)
        if (alts.length) res[name].push(alts)
      })
    })
  })
  return res
}

// Dados para simular o jogador: nível das picaretas, nível pedido pelos blocos e veios do GregTech.
let ecosProgressao = (R, itemTags, blockTags) => {
  const RL = Java.loadClass('net.minecraft.resources.ResourceLocation')
  // Nível 0..4: maior degrau seguido que a picareta colhe. ancient_debris é needs_diamond_tool no vanilla, então o
  // degrau 4 usa um bloco de forge:needs_netherite_tool (o único jeito de separar netherite de diamante).
  let netherBlock = (blockTags['forge:needs_netherite_tool'] || [])[0]
  let probes = ['minecraft:stone', 'minecraft:iron_ore', 'minecraft:diamond_ore', 'minecraft:obsidian']
  if (netherBlock) probes.push(netherBlock)
  let states = probes.map(id => R.BLOCK.get(new RL(id)).defaultBlockState())
  let pickaxeTiers = {}
  let picks = (itemTags['minecraft:pickaxes'] || []).concat(itemTags['forge:tools/pickaxes'] || [])
  picks.forEach(id => {
    if (pickaxeTiers[id] !== undefined) return
    let stack = Item.of(id)
    let tier = -1
    for (let i = 0; i < states.length && stack.isCorrectToolForDrops(states[i]); i++) tier = i
    pickaxeTiers[id] = Math.max(tier, 0)
  })
  let blockTiers = {}
  let needs = { 'minecraft:needs_stone_tool': 1, 'minecraft:needs_iron_tool': 2, 'minecraft:needs_diamond_tool': 3,
    'forge:needs_netherite_tool': 4 }
  Object.keys(needs).forEach(tag => (blockTags[tag] || []).forEach(b => {
    blockTiers[b] = Math.max(blockTiers[b] || 0, needs[tag])
  }))

  const GTR = Java.loadClass('com.gregtechceu.gtceu.api.registry.GTRegistries')
  const HRP = Java.loadClass('net.minecraft.world.level.levelgen.placement.HeightRangePlacement')
  const JsonOps = Java.loadClass('com.mojang.serialization.JsonOps')
  // VerticalAnchor em JSON: absolute / above_bottom / below_top (aproximado para o Overworld, -64..320)
  let anchorY = a => a.absolute !== undefined ? a.absolute : a.above_bottom !== undefined ? -64 + a.above_bottom
    : a.below_top !== undefined ? 319 - a.below_top : null
  let gtVeins = []
  const ArrayList = Java.loadClass('java.util.ArrayList')
  let veinKeys = new ArrayList(GTR.ORE_VEINS.keys())  // keys()/entries() são vistas não modificáveis: o Rhino não itera
  for (let i = 0; i < veinKeys.size(); i++) {
    let key = veinKeys.get(i)
    let def = GTR.ORE_VEINS.get(key)
    let dims = []
    def.dimensionFilter().forEach(k => dims.push(String(k.location())))
    let materials = []
    def.veinGenerator().getAllMaterials().forEach(m => { let n = String(m.getName()); if (materials.indexOf(n) < 0) materials.push(n) })
    let h = JSON.parse(String(HRP.CODEC.encodeStart(JsonOps.INSTANCE, def.range()).result().get().toString())).height
    gtVeins.push({ id: String(key), dims: dims, min_y: anchorY(h.min_inclusive), max_y: anchorY(h.max_inclusive),
      weight: Number(def.weight()), materials: materials })
  }
  return { pickaxeTiers: pickaxeTiers, blockTiers: blockTiers, gtVeins: gtVeins }
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
  const blockTags = tagsOf(R.BLOCK)
  let progress = { pickaxeTiers: {}, blockTiers: {}, gtVeins: [] }
  try {
    progress = ecosProgressao(R, itemTags, blockTags)
  } catch (e) {
    console.error('[ecos] dump de progressão falhou: ' + e)  // o boot dev acusa; o resto do dump continua
  }
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
    block_tags: blockTags,
    fluid_tags: tagsOf(R.FLUID),
    emc_gtceu_nonzero: emcGtNonzero,
    emc_sanity_dirt: Number(emcProxy['getValue(net.minecraft.world.item.ItemStack)'](Item.of('minecraft:dirt'))),
    pickaxe_tiers: progress.pickaxeTiers,
    block_tiers: progress.blockTiers,
    gt_veins: progress.gtVeins
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
    let fluidInputs = [], fluidOutputs = [], eut = 0, ebfTemp = 0
    if (r.inputs && r.getInputEUt) {  // GTRecipe: getIngredients() vem vazio, as entradas estão no mapa de capacidades
      try {
        let ins = ecosGtContents([r.inputs, r.tickInputs])
        if (inputs.length === 0) inputs = ins.item
        fluidInputs = ins.fluid
        ecosGtContents([r.outputs, r.tickOutputs]).fluid.forEach(alts => alts.forEach(f => fluidOutputs.push(f)))
        eut = Number(r.getInputEUt().getTotalEU())
        ebfTemp = Number(r.data.getInt('ebf_temp'))
      } catch (e) {
        if (gtDebug.length < 3) gtDebug.push('gt inputs ' + r.getId() + ': ' + e)
      }
    }
    recipes.push({ id: String(r.getId()), type: String(r.getType()), outputs: outputs, inputs: inputs,
      fluid_inputs: fluidInputs, fluid_outputs: fluidOutputs, eut: eut, ebf_temp: ebfTemp })
  })
  JsonIO.write('kubejs/exported/recipe_dump.json', { recipes: recipes, errors: errors, gt_debug: gtDebug }) // JsonIO ignora array na raiz
  console.info(`[ecos] dumps escritos: ${Object.keys(itemTags).length} item tags, ${recipes.length} receitas`)
})
