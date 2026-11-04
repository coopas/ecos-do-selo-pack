// Ecos do Selo — DEV ONLY. Provas em jogo dos blocos do ecosmaquinas (Tasks 4–7). Lido por tests/test_maquinas_ingame.py.
// Cada bloco de máquina tem seu comando "/kubejs custom_command ecos_<algo>_check", que mexe nos blocos que o teste
// colocou nas posições de ECOS_MAQ_POS, e imprime uma linha "ECOS_<ALGO> chave=valor ..." (server.tell -> console).
// Para acrescentar uma máquina: some as posições em ECOS_MAQ_POS e um novo bloco ServerEvents.customCommand no fim.

const ECOS_MAQ_POS = {
  motor_cheio: [2, 300, 2], motor_vazio: [6, 300, 2], motor_agua: [10, 300, 2],  // Task 4 (facing=up: eixo em cima)
}

const EcosMaq = {
  BlockPos: Java.loadClass('net.minecraft.core.BlockPos'),
  Direction: Java.loadClass('net.minecraft.core.Direction'),
  Caps: Java.loadClass('net.minecraftforge.common.capabilities.ForgeCapabilities'),
  Acao: Java.loadClass('net.minecraftforge.fluids.capability.IFluidHandler$FluidAction'),
  dev() { return !!JsonIO.read('kubejs/config/dev.json') },
  be(server, nome) {
    let p = ECOS_MAQ_POS[nome]
    return server.overworld().getBlockEntity(new EcosMaq.BlockPos(p[0], p[1], p[2]))
  },
  // handler de fluido do bloco na face pedida, ou null se a face não expõe fluido
  fluidos(be, face) {
    let lo = be.getCapability(EcosMaq.Caps.FLUID_HANDLER, face)
    return lo.isPresent() ? lo.resolve().get() : null
  },
  // FluidStack do KubeJS (Fluid.of): o conversor de tipos do KubeJS transforma em FluidStack do Forge na chamada.
  // Um FluidStack do Forge criado aqui chega VAZIO ao Java (o conversor não o reconhece).
  fluido(id, mb) { return Fluid.of(id, mb) },
  // capacidade total (SU) da rede cinética do bloco, como o Create a guarda no NBT
  suRede(be) {
    let t = be.saveWithoutMetadata()
    return t.contains('Network') ? t.getCompound('Network').getFloat('Capacity') : 0
  },
  diga(server, linha) { server.tell(linha); console.info(linha) },
}

// --- Task 4: Motor a Vapor do Eco ---------------------------------------------------------------------------------
// Enche o motor_cheio com 8 000 mB de gtceu:steam pela capability (face norte), tenta água no motor_vazio,
// espera 40 ticks e mede: RPM dos dois, SU da rede do cheio, consumo (mB/t).
ServerEvents.customCommand('ecos_motor_check', event => {
  if (!EcosMaq.dev()) return
  const server = event.server, D = EcosMaq.Direction, EXEC = EcosMaq.Acao.EXECUTE
  let cheio = EcosMaq.be(server, 'motor_cheio'), vazio = EcosMaq.be(server, 'motor_vazio'), agua = EcosMaq.be(server, 'motor_agua')
  if (!cheio || !vazio || !agua) { EcosMaq.diga(server, 'ECOS_MOTOR erro=sem_motor'); return }
  let hCheio = EcosMaq.fluidos(cheio, D.NORTH), hVazio = EcosMaq.fluidos(vazio, D.NORTH)
  if (!hCheio || !hVazio) { EcosMaq.diga(server, 'ECOS_MOTOR erro=sem_capability'); return }
  let entrou = hCheio.fill(EcosMaq.fluido('gtceu:steam', 8000), EXEC)
  let aguaRecusada = hVazio.fill(EcosMaq.fluido('minecraft:water', 1000), EXEC) == 0
  // contraprova: o mesmo motor aceitaria vapor (simulado), então a recusa da água não é um FluidStack vazio
  let vaporAceitoSim = hVazio.fill(EcosMaq.fluido('gtceu:steam', 1000), EcosMaq.Acao.SIMULATE)
  let eixoSemCap = EcosMaq.fluidos(cheio, D.UP) == null  // facing=up: o eixo está em cima
  let drenoRecusado = hCheio.drain(1000, EXEC).isEmpty()
  server.scheduleInTicks(40, () => {
    let nbt = cheio.saveWithoutMetadata()
    EcosMaq.diga(server, `ECOS_MOTOR vazio_rpm=${Math.abs(vazio.getSpeed())} cheio_rpm=${Math.abs(cheio.getSpeed())}` +
      ` su=${EcosMaq.suRede(cheio)} mb_t=${cheio.getConsumoMbT()} agua_recusada=${aguaRecusada}`)
    EcosMaq.diga(server, `ECOS_MOTOR_EXTRA vapor_entrou=${entrou} vapor_aceito_sim=${vaporAceitoSim}` +
      ` eixo_sem_cap=${eixoSemCap} dreno_recusado=${drenoRecusado}` +
      ` agua_nbt_rpm=${Math.abs(agua.getSpeed())} agua_nbt_limpa=${agua.getVapor() == 0}` +
      ` vapor_restante=${cheio.getVapor()} nbt_tanque=${nbt.contains('Tanque') && nbt.getCompound('Tanque').getInt('Amount') > 0}`)
  })
})
