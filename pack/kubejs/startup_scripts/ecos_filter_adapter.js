// Ecos do Selo — liga os smart filters do FTB Filter System às tasks do FTB Quests.
// O FTB Quests 2001.4 só reconhece filtros por adaptadores registrados (ItemFilterAdapter) e o FTB Filter
// System 20.0.1 não registra nenhum: sem isto, toda task por tag (ex.: "qualquer tronco") pede o próprio
// item smart_filter. Roda no cliente (exibição no livro) e no servidor (checagem do inventário).
// Métodos em try/catch: são chamados a cada checagem de inventário e um erro não pode derrubar o jogo.
StartupEvents.postInit(event => {
  try {
    let QuestsAPI = Java.loadClass('dev.ftb.mods.ftbquests.api.FTBQuestsAPI')
    let FilterAPI = Java.loadClass('dev.ftb.mods.ftbfiltersystem.api.FTBFilterSystemAPI')
    QuestsAPI.api().registerFilterAdapter({
      getName: () => 'ecos_ftbfiltersystem',
      isFilterStack: stack => {
        try { return FilterAPI.api().isFilterItem(stack) } catch (e) { return false }
      },
      doesItemMatch: (filter, stack) => {
        try { return FilterAPI.api().doesFilterMatch(filter, stack) } catch (e) { return false }
      },
      getMatcher: filter => stack => {
        try { return FilterAPI.api().doesFilterMatch(filter, stack) } catch (e) { return false }
      },
      hasItemTagFilter: () => true,
      makeTagFilterStack: tag => FilterAPI.api().makeTagFilter(tag)
    })
    console.info('[ecos] adaptador FTB Filter System → FTB Quests registrado')
  } catch (e) {
    console.warn('[ecos] FALHA ao registrar adaptador de filtros no FTB Quests: ' + e)
  }
})
