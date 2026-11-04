// Ecos do Selo — minério do GregTech no Create, ligas na batedeira e redstone do cascalho. Fonte: kubejs/ecos/create_gt.json
// (gerado por tools/gen_create_gt.py). Sem o addon KubeJS Create: as receitas entram como JSON via event.custom.
let ECOS_CREATE_GT = JsonIO.read('kubejs/ecos/create_gt.json')
if (!ECOS_CREATE_GT) throw new Error('[ecos] kubejs/ecos/create_gt.json ausente ou inválido: minério do GT NÃO entra no Create')

// quantas receitas ecos:create_gt/* o JSON implica (lido pelo teste ingame)
global.ecosCreateGtCount = 0

// JsonIO.read devolve Map/List do Java: copia para objetos/arrays JS (o event.custom e o json.type precisam disso)
const JList = Java.loadClass('java.util.List')
const JMap = Java.loadClass('java.util.Map')
let ecosPlain = node => {
  if (node instanceof JList || Array.isArray(node)) {
    let out = []
    node.forEach(v => out.push(ecosPlain(v)))
    return out
  }
  if (node instanceof JMap) {
    let out = {}
    node.forEach((k, v) => { out[String(k)] = ecosPlain(v) })
    return out
  }
  return node
}

ServerEvents.recipes(event => {
  let add = (type, name, body) => {
    let json = ecosPlain(body)
    json.type = type
    event.custom(json).id('ecos:create_gt/' + name)
    global.ecosCreateGtCount++
  }
  for (let m in ECOS_CREATE_GT.crushing) add('create:crushing', 'crushing/' + m, ECOS_CREATE_GT.crushing[m])
  for (let m in ECOS_CREATE_GT.splashing) add('create:splashing', 'splashing/' + m, ECOS_CREATE_GT.splashing[m])
  for (let m in ECOS_CREATE_GT.pressing) add('create:pressing', 'pressing/' + m, ECOS_CREATE_GT.pressing[m])
  for (let m in ECOS_CREATE_GT.mixing) add('create:mixing', 'mixing/' + m, ECOS_CREATE_GT.mixing[m])
  // cascalho: troca a receita do Create (mantém areia/sílex/argila e acrescenta redstone)
  event.remove({ id: 'create:crushing/gravel' })
  add('create:crushing', 'gravel', ECOS_CREATE_GT.gravel)
  console.info(`[ecos] create_gt: ${global.ecosCreateGtCount} receitas ecos:create_gt/* criadas`)
})
