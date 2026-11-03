// Ecos do Selo — DEV ONLY (só com kubejs/config/dev.json). Prova em jogo que:
//  (a) o item-filtro de tag do FTB Filter System casa com TODOS os membros da tag e recusa item de fora;
//  (b) o FTB Quests carregou exatamente as quests da fonte (releitura via writeData).
// Grava kubejs/exported/quest_selftest.json (lido por tests/test_questgen.py).
// O FTB Quests só carrega as quests DEPOIS de ServerEvents.loaded: o teste roda 200 ticks (10 s) depois.
ServerEvents.loaded(event => {
  if (!JsonIO.read('kubejs/config/dev.json')) return
  event.server.scheduleInTicks(200, () => ecosQuestSelftest())
})

function ecosQuestSelftest() {
  const Registries = Java.loadClass('net.minecraft.core.registries.Registries')
  const TagKey = Java.loadClass('net.minecraft.tags.TagKey')
  const RL = Java.loadClass('net.minecraft.resources.ResourceLocation')
  const CompoundTag = Java.loadClass('net.minecraft.nbt.CompoundTag')
  const BuiltIn = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries')
  const FilterAPI = Java.loadClass('dev.ftb.mods.ftbfiltersystem.api.FTBFilterSystemAPI').api()

  let wanted = JsonIO.read('kubejs/ecos/quest_tags.json')
  let tags = (wanted && wanted.tags) ? wanted.tags : ['minecraft:beds']
  let filters = {}
  let sample = null
  tags.forEach(tag => {
    let key = TagKey.create(Registries.ITEM, new RL(tag))
    let filterStack = FilterAPI.makeTagFilter(key)
    if (sample === null) sample = String(filterStack.save(new CompoundTag()).toString())
    let ok = 0
    let fail = []
    BuiltIn.ITEM.getTag(key).ifPresent(set => set.forEach(holder => {
      let id = String(holder.unwrapKey().get().location())
      if (FilterAPI.doesFilterMatch(filterStack, Item.of(id))) ok++
      else fail.push(id)
    }))
    let outsider = FilterAPI.doesFilterMatch(filterStack, Item.of('minecraft:stone'))
    filters[tag] = { members_ok: ok, members_fail: fail, outsider_matches: outsider }
  })

  let quests = {}
  let chapters = 0
  try {
    let file = Java.loadClass('dev.ftb.mods.ftbquests.quest.ServerQuestFile').INSTANCE
    file.getAllChapters().forEach(ch => {
      chapters++
      ch.getQuests().forEach(q => {
        let nbt = new CompoundTag()
        q.writeData(nbt)
        let tasks = []
        q.getTasks().forEach(t => {
          let tn = new CompoundTag()
          t.writeData(tn)
          tasks.push({ type: String(t.getClass().getSimpleName()), data: String(tn.toString()) })
        })
        let rewards = []
        q.getRewards().forEach(r => {
          let rn = new CompoundTag()
          r.writeData(rn)
          let tableOk = null
          try { tableOk = r.getTable() != null } catch (e) { /* não é recompensa de tabela */ }
          rewards.push({ type: String(r.getClass().getSimpleName()), data: String(rn.toString()), table_ok: tableOk })
        })
        quests[String(q.getCodeString())] = { quest: String(nbt.toString()), tasks: tasks, rewards: rewards }
      })
    })
  } catch (e) {
    quests = { error: String(e) }
  }

  JsonIO.write('kubejs/exported/quest_selftest.json', {
    filter_sample: sample, filters: filters, chapters: chapters, quests: quests
  })
  console.info(`[ecos] quest_selftest: ${Object.keys(filters).length} filtros, ${chapters} capítulos`)
}
