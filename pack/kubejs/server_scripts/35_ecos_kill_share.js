// Ecos do Selo — morte de chefe conta para TODOS os jogadores vivos a até 64 blocos (mesma dimensão),
// não só para quem deu o último golpe. Progresso é individual; sem isto, cada amigo precisaria da sua própria
// torre/masmorra. Só credita quem já pode fazer a quest (dependências cumpridas). Fonte: kubejs/ecos/kill_tasks.json
let ECOS_KILLS = JsonIO.read('kubejs/ecos/kill_tasks.json')
if (!ECOS_KILLS) throw new Error('[ecos] kubejs/ecos/kill_tasks.json ausente ou inválido: kills compartilhados NÃO carregados')
let ecosTaskCache = null

function ecosFindTasks(file) {
  // ids de 64 bits não cabem num número JS: compara pela string hex
  if (ecosTaskCache) return ecosTaskCache
  ecosTaskCache = {}
  file.getAllChapters().forEach(ch => ch.getQuests().forEach(q => q.getTasks().forEach(t => {
    ecosTaskCache[String(t.getCodeString()).toUpperCase()] = t
  })))
  return ecosTaskCache
}

ServerEvents.loaded(event => { ecosTaskCache = null })

EntityEvents.death(event => {
  try {
    let boss = event.entity
    let ids = ECOS_KILLS.kills[String(boss.type)]
    if (!ids) return
    let file = Java.loadClass('dev.ftb.mods.ftbquests.quest.ServerQuestFile').INSTANCE
    let tasks = ecosFindTasks(file)
    event.server.players.forEach(p => {
      if (!p.isAlive() || p.isSpectator()) return
      if (p.level.dimension != boss.level.dimension || p.distanceToEntity(boss) > 64) return
      let data = file.getOrCreateTeamData(p)
      ids.forEach(id => {
        let t = tasks[String(id).toUpperCase()]
        if (!t || data.isCompleted(t) || !data.canStartTasks(t.getQuest())) return
        data.setProgress(t, t.getMaxProgress())
      })
    })
  } catch (e) {
    console.error('[ecos] kill compartilhado falhou: ' + e)
  }
})
