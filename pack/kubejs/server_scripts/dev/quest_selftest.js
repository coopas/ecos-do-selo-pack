// Ecos do Selo — DEV ONLY (só com kubejs/config/dev.json). Prova em jogo que:
//  (a) o item-filtro de tag do FTB Filter System casa com TODOS os membros da tag e recusa item de fora;
//  (b) a TASK do FTB Quests (ItemTask.test) aceita um membro da tag e recusa pedra — prova o adaptador de filtros;
//  (c) o FTB Quests carregou exatamente as quests da fonte (releitura via writeData).
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
  let taskProbes = {}
  let chapterData = {}
  let chapters = 0
  try {
    let file = Java.loadClass('dev.ftb.mods.ftbquests.quest.ServerQuestFile').INSTANCE
    file.getAllChapters().forEach(ch => {
      chapters++
      let cn = new CompoundTag()
      ch.writeData(cn)
      chapterData[String(ch.getFilename())] = String(cn.toString())
      ch.getQuests().forEach(q => {
        let nbt = new CompoundTag()
        q.writeData(nbt)
        let tasks = []
        q.getTasks().forEach(t => {
          let tn = new CompoundTag()
          t.writeData(tn)
          ecosProbeTagTask(t, String(q.getCodeString()), BuiltIn, Registries, TagKey, RL, taskProbes)
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

  let tables = {}
  try {
    let file = Java.loadClass('dev.ftb.mods.ftbquests.quest.ServerQuestFile').INSTANCE
    file.getRewardTables().forEach(t => {
      let crate = t.getLootCrate()
      let n = 0
      let weight = 0
      t.getWeightedRewards().forEach(wr => { n++; weight += wr.getWeight() })
      tables[crate ? String(crate.getStringID()) : String(t.getFilename())] = {
        rewards: n, total_weight: weight, crate: crate ? String(crate.getStringID()) : null
      }
    })
  } catch (e) {
    tables = { error: String(e) }
  }

  JsonIO.write('kubejs/exported/quest_selftest.json', {
    filter_sample: sample, filters: filters, task_probes: taskProbes, chapter_data: chapterData, chapters: chapters, quests: quests, tables: tables
  })
  console.info(`[ecos] quest_selftest: ${Object.keys(filters).length} filtros, ${chapters} capítulos`)
}

// Testa a task de verdade: o mesmo caminho que o FTB Quests usa ao checar o inventário do jogador.
function ecosProbeTagTask(t, questId, BuiltIn, Registries, TagKey, RL, out) {
  if (String(t.getClass().getSimpleName()) !== 'ItemTask') return
  let filter = t.getItemStack()
  if (String(filter.getId()) !== 'ftbfiltersystem:smart_filter') return
  let m = String(filter.getNbt().getString('ftbfiltersystem:filter')).match(/item_tag\(([^)]+)\)/)
  if (!m) return
  let member = null
  BuiltIn.ITEM.getTag(TagKey.create(Registries.ITEM, new RL(m[1]))).ifPresent(set => set.forEach(h => {
    if (member === null) member = String(h.unwrapKey().get().location())
  }))
  let res = { tag: m[1], member: member, member_ok: false, outsider_ok: null }
  try {
    res.member_ok = member !== null && t.test(Item.of(member))
    res.outsider_ok = t.test(Item.of('minecraft:stone'))
  } catch (e) {
    res.error = String(e)
  }
  out[questId + ':' + String(t.getCodeString())] = res
}
