// Ecos do Selo — combustíveis unificados GregTech x Create: Diesel Generators. Fonte: kubejs/ecos/fuels.json
// 1) os fluidos do GT entram nas tags de fluido que o CDG lê (fuel_type/*.json): o motor diesel queima diesel do GT;
// 2) os fluidos do CDG viram combustível das máquinas do GT (gerador de combustão) e entrada da destilação (óleo cru do CDG).
let ECOS_FUELS = JsonIO.read('kubejs/ecos/fuels.json')
if (!ECOS_FUELS) throw new Error('[ecos] kubejs/ecos/fuels.json ausente ou inválido: combustíveis NÃO unificados')

const ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')

ServerEvents.tags('fluid', event => {
  for (let tag in ECOS_FUELS.fluid_tags) ECOS_FUELS.fluid_tags[tag].forEach(f => event.add(tag, f))
})

// No Rhino o campo público `id` do RecipeJS esconde o método; o GTRecipeJS tem id(ResourceLocation): chama por reflexão
let ecosSetRecipeId = (rec, id) => {
  let rl = new ResourceLocation(id)
  rec.getClass().getMethod('id', rl.getClass()).invoke(rec, rl)
}

// As receitas do GT pedem o fluido por TAG (forge:<nome>) ou por id. Troca (em profundidade) toda entrada que
// seja o fluido `from` (por id ou pela tag forge:<nome>) pelo fluido `to`; devolve quantas trocas fez
let ecosSwapFluid = (node, from, to) => {
  let n = 0
  let tag = 'forge:' + from.split(':')[1]
  if (Array.isArray(node)) {
    node.forEach(v => { n += ecosSwapFluid(v, from, to) })
  } else if (node && typeof node === 'object') {
    if (node.fluid === from || node.tag === tag) {
      delete node.tag
      node.fluid = to
      return 1
    }
    for (let k in node) n += ecosSwapFluid(node[k], from, to)
  }
  return n
}

// quantas receitas ecos:fuel/* o fuels.json implica (lido por dev/fuel_check.js)
global.ecosFuelExpected = 0

ServerEvents.recipes(event => {
  let clone = (machine, map, label) => {
    for (let src in map) {
      let dst = map[src]
      let found = []
      event.forEachRecipe({ type: machine }, r => {
        let json = JSON.parse(String(r.json.toString()))
        if (ecosSwapFluid(json.inputs, src, dst) > 0) {
          found.push({ id: String(r.getId()), json: json })
        }
      })
      if (found.length == 0) throw new Error(`[ecos] fuels: nenhuma receita ${machine} com entrada ${src} para clonar (${label})`)
      found.forEach(f => {
        let name = f.id.replace(':', '_').replace(/\//g, '_')
        let rec = event.custom(f.json)
        ecosSetRecipeId(rec, `ecos:fuel/${name}_${dst.replace(":", "_")}`)
        global.ecosFuelExpected++
      })
    }
  }
  clone('gtceu:combustion_generator', ECOS_FUELS.gt_combustion_clones, 'combustão')
  for (let machine of ['gtceu:distillation_tower', 'gtceu:distillery']) {
    // nem toda máquina destila óleo: só falha se NENHUMA tiver receita de origem
    try { clone(machine, ECOS_FUELS.gt_distillation_clones, 'destilação') } catch (e) {
      if (machine == 'gtceu:distillation_tower') throw e
      console.info(`[ecos] fuels: ${machine} sem receita de origem (ok): ${e}`)
    }
  }
  console.info(`[ecos] fuels: ${global.ecosFuelExpected} receitas ecos:fuel/* criadas`)
})
