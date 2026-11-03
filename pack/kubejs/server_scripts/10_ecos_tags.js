// Ecos do Selo — tags sobrescritas (set) ou estendidas (add). Fonte: kubejs/ecos/tags.json
// Usado nas travas: ativador do portal da Twilight e itens que a Uncrafting Table da Twilight não pode desmontar.
let ECOS_TAGS = JsonIO.read('kubejs/ecos/tags.json')
if (!ECOS_TAGS) throw new Error('[ecos] kubejs/ecos/tags.json ausente ou inválido: travas NÃO carregadas')

let ecosApplyTags = (kind, event) => {
  let defs = ECOS_TAGS[kind]
  if (!defs) return
  for (let tag in defs) {
    let op = defs[tag]
    if (op.set) {
      event.removeAll(tag)
      op.set.forEach(v => event.add(tag, v))
    }
    if (op.add) op.add.forEach(v => event.add(tag, v))
  }
}

ServerEvents.tags('item', event => ecosApplyTags('item', event))
ServerEvents.tags('block', event => ecosApplyTags('block', event))
