// Ecos do Selo — DEV ONLY. Provas em jogo dos blocos do ecosmaquinas (Tasks 4–7). Lido por tests/test_maquinas_ingame.py.
// Cada bloco de máquina tem seu comando "/kubejs custom_command ecos_<algo>_check", que mexe nos blocos que o teste
// colocou nas posições de ECOS_MAQ_POS, e imprime uma linha "ECOS_<ALGO> chave=valor ..." (server.tell -> console).
// Para acrescentar uma máquina: some as posições em ECOS_MAQ_POS e um novo bloco ServerEvents.customCommand no fim.

const ECOS_MAQ_POS = {
  motor_cheio: [2, 300, 2], motor_vazio: [6, 300, 2], motor_agua: [10, 300, 2],  // Task 4 (facing=up: eixo em cima)
  // Task 5: dínamo em y=301 (facing=down: eixo embaixo, no motor criativo em y=300); saída em cima, buffer em y=302
  dinamo_ulv: [2, 301, 6], dinamo_lv: [4, 301, 6], dinamo_parado: [6, 301, 6], dinamo_reverso: [8, 301, 6],
  dinamo_lento: [10, 301, 6], dinamo_rapido: [12, 301, 6],
  buffer_ulv: [2, 302, 6], buffer_lv: [4, 302, 6], buffer_parado: [6, 302, 6], buffer_reverso: [8, 302, 6],
  buffer_lento: [10, 302, 6], buffer_rapido: [12, 302, 6],
  dinamo_nbt_alto: [2, 301, 10], dinamo_nbt_neg: [4, 301, 10],  // NBT adulterado, sem rotação nem vizinho
  // Task 6: caldeira = torre 1x1x8 de create:fluid_tank (y 301..308) com o queimador embaixo (y=300);
  // saída encostada no 2º tanque (y=302, x+1) e tambor de aço logo depois (x+2). caldeira_* = tanque de baixo.
  caldeira_quente: [2, 301, 13], saida_quente: [3, 302, 13], tambor_quente: [4, 302, 13],
  tanque_criativo_quente: [0, 301, 13],
  caldeira_motores: [8, 301, 13], saida_motores: [9, 302, 13], tambor_motores: [10, 302, 13],
  tanque_criativo_motores: [6, 301, 13],
  caldeira_fria: [13, 301, 13], saida_fria: [14, 302, 13], tambor_fria: [15, 302, 13],
  caldeira_seca: [2, 301, 9], saida_seca: [3, 302, 9], tambor_seca: [4, 302, 9],
  caldeira_reserva: [7, 301, 9], saida_reserva: [8, 302, 9], tambor_reserva: [9, 302, 9],
  saida_nbt_ruim: [12, 302, 9],  // NBT adulterado, sem caldeira
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

// --- Task 5: Dínamo Cinético (ULV e LV) ---------------------------------------------------------------------------
// Cada dínamo gira por um motor criativo (64 RPM; parado 0; reverso -64; lento ULV a 32; rápido LV a 256) e solta EU
// em cima, num gtceu:lv_battery_buffer_4x com uma bateria. Põe a bateria, espera 100 ticks (rede estável) e mede a
// energia que de fato entrou no buffer nos 100 ticks seguintes: eu_t = delta / 100.
ServerEvents.customCommand('ecos_dinamo_check', event => {
  if (!EcosMaq.dev()) return
  const server = event.server, D = EcosMaq.Direction
  const GTCap = Java.loadClass('com.gregtechceu.gtceu.api.capability.forge.GTCapability')
  const nomes = ['ulv', 'lv', 'parado', 'reverso', 'lento', 'rapido']
  const energia = be => {
    let lo = be ? be.getCapability(GTCap.CAPABILITY_ENERGY_CONTAINER, D.DOWN) : null
    return lo && lo.isPresent() ? lo.resolve().get() : null
  }
  let buffers = {}, dinamos = {}
  for (let n of nomes) {
    dinamos[n] = EcosMaq.be(server, 'dinamo_' + n)
    let b = EcosMaq.be(server, 'buffer_' + n)
    // o buffer do GregTech não expõe as baterias como ITEM_HANDLER: põe direto no inventário da máquina
    let maq = b && b.getMetaMachine ? b.getMetaMachine() : null
    let falta = !dinamos[n] ? 'dinamo' : !maq || !maq.getBatteryInventory ? 'buffer' : !energia(b) ? 'energia_buffer' : null
    if (falta) { EcosMaq.diga(server, `ECOS_DINAMO erro=sem_${falta}_${n}`); return }
    let sobra = maq.getBatteryInventory().insertItem(0, Item.of('gtceu:lv_sodium_battery'), false)
    if (!sobra.isEmpty()) { EcosMaq.diga(server, `ECOS_DINAMO erro=bateria_recusada_${n}`); return }
    buffers[n] = b
  }
  let lv = dinamos.lv
  let capSaida = lv.getCapability(GTCap.CAPABILITY_ENERGY_CONTAINER, D.UP)
  let eixoSemCap = !lv.getCapability(GTCap.CAPABILITY_ENERGY_CONTAINER, D.DOWN).isPresent()
  let saida = capSaida.isPresent() ? capSaida.resolve().get() : null
  let alto = EcosMaq.be(server, 'dinamo_nbt_alto'), neg = EcosMaq.be(server, 'dinamo_nbt_neg')
  server.scheduleInTicks(100, () => {
    let antes = {}
    for (let n of nomes) antes[n] = energia(buffers[n]).getEnergyStored()
    server.scheduleInTicks(100, () => {
      let eut = {}
      for (let n of nomes) eut[n] = (energia(buffers[n]).getEnergyStored() - antes[n]) / 100
      EcosMaq.diga(server, `ECOS_DINAMO ulv_eu_t=${eut.ulv} lv_eu_t=${eut.lv} parado_eu_t=${eut.parado} reverso_eu_t=${eut.reverso}`)
      EcosMaq.diga(server, `ECOS_DINAMO_EXTRA lento_eu_t=${eut.lento} rapido_eu_t=${eut.rapido}` +
        ` ulv_calc=${dinamos.ulv.getEuT()} lv_calc=${lv.getEuT()} reverso_calc=${dinamos.reverso.getEuT()}` +
        ` rapido_calc=${dinamos.rapido.getEuT()} ulv_v=${dinamos.ulv.getVoltagem()} lv_v=${lv.getVoltagem()}` +
        ` reverso_rpm=${dinamos.reverso.getSpeed()} saida_cap=${saida != null} eixo_sem_cap=${eixoSemCap}` +
        ` saida_out=${saida != null && saida.outputsEnergy(D.UP)} saida_nao_aceita=${saida != null && !saida.inputsEnergy(D.UP)}` +
        ` saida_recusa=${saida != null ? saida.acceptEnergyFromNetwork(D.UP, 32, 1) == 0 : false}` +
        ` buffer_alto=${alto ? alto.getBuffer() : -1} buffer_neg=${neg ? neg.getBuffer() : -1}` +
        ` buffer_max_lv=${lv.getBufferMax()}`)
    })
  })
})

// --- Task 6: Saída de Vapor da caldeira do Create ------------------------------------------------------------------
// Cinco caldeiras 1x1x8 (tamanho 8 -> nível máx. 2 pelo tamanho), cada uma com uma Saída e um gtceu:steel_drum:
//  quente:   queimador superaquecido (calor 2) + água por tanque criativo e bomba -> nível 2, 12 mB/t
//  motores:  igual à quente, com um create:steam_engine acoplado -> modo exclusivo: 0
//  fria:     8 000 mB de água, sem queimador -> 0
//  seca:     queimador superaquecido, sem água -> 0
//  reserva:  queimador superaquecido e só 1 000 mB de água, sem bomba -> 10 mB de água por nível: 600 mB de vapor e para
// Espera 200 ticks e mede o vapor que de fato entrou em cada tambor nos 100 ticks seguintes: mb_t = delta / 100.
ServerEvents.customCommand('ecos_saida_check', event => {
  if (!EcosMaq.dev()) return
  const server = event.server, D = EcosMaq.Direction, EXEC = EcosMaq.Acao.EXECUTE
  const casos = ['quente', 'motores', 'fria', 'seca', 'reserva']
  let saidas = {}, tambores = {}, caldeiras = {}
  for (let n of casos) {
    saidas[n] = EcosMaq.be(server, 'saida_' + n)
    caldeiras[n] = EcosMaq.be(server, 'caldeira_' + n)
    let t = EcosMaq.be(server, 'tambor_' + n)
    tambores[n] = t ? EcosMaq.fluidos(t, D.WEST) : null
    let falta = !saidas[n] ? 'saida' : !caldeiras[n] || !caldeiras[n].getControllerBE ? 'caldeira' : !tambores[n] ? 'tambor' : null
    if (falta) { EcosMaq.diga(server, `ECOS_SAIDA erro=sem_${falta}_${n}`); return }
  }
  for (let n of ['quente', 'motores']) {
    let ct = EcosMaq.be(server, 'tanque_criativo_' + n)
    if (!ct || !ct.getTankInventory) { EcosMaq.diga(server, `ECOS_SAIDA erro=sem_tanque_criativo_${n}`); return }
    ct.getTankInventory().setContainedFluid(EcosMaq.fluido('minecraft:water', 1000))
  }
  // caldeira sem motor é um tanque comum: a água entra pela capability do tanque
  let aguaFria = EcosMaq.fluidos(caldeiras.fria, D.UP).fill(EcosMaq.fluido('minecraft:water', 8000), EXEC)
  let aguaReserva = EcosMaq.fluidos(caldeiras.reserva, D.UP).fill(EcosMaq.fluido('minecraft:water', 1000), EXEC)
  const vapor = n => tambores[n].getFluidInTank(0).getAmount()
  const agua = n => caldeiras[n].getControllerBE().getTankInventory().getFluidAmount()
  server.scheduleInTicks(200, () => {
    let antes = {}
    for (let n of casos) antes[n] = vapor(n)
    server.scheduleInTicks(100, () => {
      let mbt = {}
      for (let n of casos) mbt[n] = (vapor(n) - antes[n]) / 100
      let q = saidas.quente, bm = caldeiras.motores.getControllerBE().boiler
      let ruim = EcosMaq.be(server, 'saida_nbt_ruim')
      EcosMaq.diga(server, `ECOS_SAIDA nivel=${q.getNivel()} mb_t=${mbt.quente} com_motores_mb_t=${mbt.motores} fria_mb_t=${mbt.fria}`)
      EcosMaq.diga(server, `ECOS_SAIDA_EXTRA seca_mb_t=${mbt.seca} calc_quente=${q.getProducaoMbT()}` +
        ` calc_motores=${saidas.motores.getProducaoMbT()} motores_engines=${bm.attachedEngines}` +
        ` motores_calor=${bm.activeHeat} motores_nivel=${saidas.motores.getNivel()}` +
        ` vapor_quente=${vapor('quente')} agua_fria=${aguaFria} agua_fria_resta=${agua('fria')}` +
        ` reserva_agua_entrou=${aguaReserva} reserva_vapor=${vapor('reserva')} reserva_agua_resta=${agua('reserva')}` +
        ` reserva_mb_t=${mbt.reserva} ruim_nivel=${ruim ? ruim.getNivel() : -1} ruim_mb_t=${ruim ? ruim.getProducaoMbT() : -1}`)
    })
  })
})
