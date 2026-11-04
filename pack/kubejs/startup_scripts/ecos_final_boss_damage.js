// Ecos do Selo — reforço do Arauto do Eco (entidades com a tag ecos_final, vindas do ritual ecos:ritual_entidade).
// O atributo de vida máxima é limitado a 1024 no vanilla, então "vida ×3" vira dano recebido ÷3 (vida efetiva ×3).
// Dano causado pelo Arauto (corpo a corpo ou projétil dele) ×1,5. Feito no LivingHurtEvent, antes de armadura.
// Erro de script num evento Forge derruba o servidor: todo o corpo fica em try/catch e só registra no log.
const ECOS_FINAL_TAG = 'ecos_final'

ForgeEvents.onEvent('net.minecraftforge.event.entity.living.LivingHurtEvent', event => {
  try {
    if (event.getEntity().getTags().contains(ECOS_FINAL_TAG)) {
      event.setAmount(event.getAmount() / 3)
      return
    }
    let src = event.getSource().getActual()  // DamageSourceKJS: atacante (dono do projétil, se houver)
    if (src && src.getTags().contains(ECOS_FINAL_TAG)) event.setAmount(event.getAmount() * 1.5)
  } catch (e) {
    console.error('[ecos] reforço do Arauto falhou: ' + e)
  }
})
