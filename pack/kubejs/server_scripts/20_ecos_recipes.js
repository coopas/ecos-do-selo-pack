// Ecos do Selo — receitas do pack (travas, cruzadas, finais). Fonte: kubejs/ecos/recipes.json
// replace_output: remove TODAS as receitas que produzem o item antes de adicionar a nossa (sem atalho).
let ECOS_RECIPES = JsonIO.read('kubejs/ecos/recipes.json') || {}

ServerEvents.recipes(event => {
  ;['gates', 'cross', 'late'].forEach(section => {
    let list = ECOS_RECIPES[section]
    if (!list) return
    list.forEach(r => {
      if (r.replace_output) event.remove({ output: r.output })
      event.shaped(Item.of(r.output, r.count), r.pattern, r.key).id(r.id)
    })
  })
})
