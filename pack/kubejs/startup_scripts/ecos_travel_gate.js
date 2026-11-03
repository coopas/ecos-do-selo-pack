// Ecos do Selo — "chave de viagem": entrar em certas dimensões exige carregar a chave no inventário (não é consumida).
// Substitui a trava pela moldura do Aether (o portal de retorno é gerado em glowstone e quebraria) e fecha a compra
// do Zeal Lighter com o Gatekeeper do Blue Skies. Voltar ao Overworld nunca é bloqueado. Fonte: kubejs/ecos/travel.json
let ECOS_TRAVEL = JsonIO.read('kubejs/ecos/travel.json')
if (!ECOS_TRAVEL) throw new Error('[ecos] kubejs/ecos/travel.json ausente ou inválido: travas de viagem NÃO carregadas')
let EcosComponent = Java.loadClass('net.minecraft.network.chat.Component')

ForgeEvents.onEvent('net.minecraftforge.event.entity.EntityTravelToDimensionEvent', event => {
  let entity = event.getEntity()
  if (!entity.isPlayer()) return
  let key = ECOS_TRAVEL.require[String(event.getDimension().location())]
  if (!key) return
  if (entity.getInventory().countItem(Item.of(key).getItem()) > 0) return
  event.setCanceled(true)
  entity.displayClientMessage(EcosComponent.literal('§5O portal rejeita você. §7Carregue uma §dChave Celeste§7 para atravessar.'), true)
})
