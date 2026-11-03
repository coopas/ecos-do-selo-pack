# Design — Modpack "Ecos do Selo" (nome provisório)

## 1. Intenção e o porquê
Modpack para Minecraft no **Prism Launcher**, jogado por **até 7 amigos** num **servidor online**. Nenhum deles jogou estes mods antes (foram escolhidos a partir do que os amigos gostam). A sensação desejada: **novidade constante, algo nunca visto, divertido, que motive a voltar** ("só mais uma quest"). A jornada é **longa (6+ meses)**, com evolução lenta e grind real, amarrada por uma **lore sombria/de mistério** e um **final que "zera" o modpack**.

## 2. Decisões do usuário (como ele decidiu)
- Mods obrigatórios: **GregTech** (CEu Modern), **Create**, **mod de spells** (Iron's Spells 'n Spellbooks), **Occultism**, **Ars Nouveau**, **ProjectE**, mais **mods de dimensões**.
- Sistema de quests completo, cobrindo todos os temas, com lore e grind lento.
- Duração-alvo: **6+ meses**, GregTech pesado.
- Progressão **individual** ("cada um no seu ritmo"): quests por jogador, no mesmo mundo.
- Lore **sombria / mistério**, com a proposta abaixo aprovada.
- **ProjectE = "alquimia proibida"**, liberado só no fim do jogo (aprovado).
- Recompensas: **loot surpresa com raridades + moeda e loja + páginas de lore + chefes de fim de ato** (todas escolhidas).
- Dificuldade **"desafiador justo"**: mobs escalam com o progresso, chefes duros, **sem perder itens na morte** (tumba).
- PCs **variados**: visual bonito e leve por padrão; **shaders incluídos, mas desligados**.
- Servidor: local **ainda indefinido** → **pacote de servidor portátil** (PC próprio, hospedagem ou VPS).
- Dimensões e final aprovados: Twilight Forest → Undergarden / Deeper and Darker → Aether / Blue Skies → **Ad Astra (espaço)** no fim do jogo.
- Quests aceitam **qualquer variante via tag/ID** (ex: "faça uma cama" aceita qualquer cama `#minecraft:beds`), nunca exigindo uma cor ou variante específica, salvo quando a lore pedir isso.
- Imagens: **eu escrevo os prompts para GPT Image 2**, o usuário gera e devolve, e eu processo e integro.
- Mods visuais, de textura e de qualidade de vida (JEI, vein miner etc.).

## 3. Objetivos / Não-objetivos / Anti-objetivos
**Objetivos**
- Uma linha de quests contínua do primeiro soco na árvore até o final, sem becos sem saída.
- Cada mod com sua fase, e **mods entrelaçados por receitas cruzadas** (magia precisa de tecnologia e vice-versa), o que gera novidade em cada ato.
- Todas as tasks verificáveis e completáveis; todos os IDs e tags válidos.
- Servidor estável para 7 jogadores; clientes sincronizados automaticamente quando o pack for atualizado.

**Não-objetivos**
- Não é um pack competitivo/PvP.
- Não vamos criar mods em Java do zero (só configs, KubeJS, datapacks e resource packs).

**Anti-objetivos (seria fracasso mesmo funcionando)**
- Quests quebradas ou impossíveis (item inexistente, receita sem caminho, tag errada).
- Grind **chato** em vez de lento: longos trechos sem novidade nem recompensa.
- ProjectE ou outro mod pulando a progressão (duplicando itens do GregTech antes da hora).
- Pack pesado demais para os PCs mais fracos do grupo.
- Lore genérica ou despejada em textão; ela precisa ser revelada aos poucos.

## 4. Base técnica (minhas escolhas)
- **Minecraft 1.20.1 + Forge (47.x)**: a única versão em que todos os mods obrigatórios coexistem.
- **Gerência do pack: packwiz.** Fonte versionada em `C:\modpack-svers`, exportada como:
  - instância do Prism (`.zip` importável) com **packwiz-installer no pre-launch**, que atualiza os clientes sozinho;
  - **pacote de servidor portátil** (Forge server, scripts `start.bat`/`start.sh`, `server.properties`, `eula`, guia de porta/playit.gg/hospedagem), RAM sugerida de 8–10 GB.
- **FTB Quests + FTB Teams** (times de 1 pessoa = progresso individual), **FTB Filter System** para tasks por tag e filtros "qualquer de".
- **KubeJS** (+ ProbeJS em dev) para receitas cruzadas, gates, itens customizados (moedas, páginas de lore, chaves de dimensão) e travas de progressão.
- Ajustes de EMC do ProjectE via config/KubeJS.

## 5. Lore e estrutura de atos
**Premissa:** uma civilização antiga fundiu **máquina e magia** para selar uma entidade de além das dimensões. Para sustentar o selo, recorreu à **transmutação (alquimia proibida)**, e foi isso que a destruiu. O jogador desperta num mundo em ruínas, guiado por **fragmentos de diário** encontrados ou ganhos nas quests. Create e GregTech são a "ciência perdida"; Ars, Iron's e Occultism, o "conhecimento arcano". Cada dimensão guarda um **fragmento do selo**.

| Ato | Tema / lore | Mods em foco | Tier GT | Dimensão | Chefe de fim de ato |
|---|---|---|---|---|---|
| Prólogo: O Despertar | ruínas, primeiras páginas | vanilla, QoL, Create básico | — / Steam | Overworld | — |
| I: Ferrugem e Engrenagens | a ciência perdida | Create, GT Steam→LV | Steam, LV | Twilight Forest | chefe da Twilight (Naga → Lich) + chefe de lore |
| II: Ecos Arcanos | o conhecimento proibido | Ars Nouveau, Iron's Spells, Occultism inicial | LV→MV | Undergarden, Deeper and Darker | Warden / chefe das profundezas |
| III: Os Céus Partidos | os guardiões do selo | Occultism avançado, Create avançado, Aether, Blue Skies | HV→EV | Aether, Blue Skies | chefes do Aether/Blue Skies |
| IV: Além do Véu | a origem nas estrelas | Ad Astra, GT espacial | EV→IV/LuV | Lua, Marte… (Ad Astra) | chefe de lore |
| V: A Heresia | a alquimia proibida | **ProjectE liberado**, GT LuV→ZPM+ | LuV+ | — | **Chefe final** + reconstrução do Selo |

- **Final:** construir o **Artefato do Selo** (receita que exige marcos de *todos* os caminhos) e enfrentar a entidade. Dois desfechos de lore (**selar** ou **absorver**), ambos contam como "zerado".
- **Gates:** portais de dimensão e foguetes travados por itens de quest e receitas KubeJS (ex: o portal da Twilight exige um item feito com Create; foguetes do Ad Astra exigem componentes GT); a Pedra Filosofal do ProjectE exige componentes do Ato V.
- **Chefes extras:** adicionar **L_Ender's Cataclysm** para chefes de lore marcantes (minha escolha).
- **ProjectE:** EMC removido ou muito alto em materiais e intermediários do GregTech, para preservar o grind mesmo depois de liberado.

## 6. Quests
- Capítulos: Prólogo, um por ato, mais **capítulos laterais por mod** (Create, GregTech, Ars, Iron's, Occultism, Dimensões, ProjectE) e capítulos de **Loja** e **Diário (lore)**.
- Escala-alvo: ~400–600 quests (o construtor ajusta).
- **Regra de IDs:** toda task usa tag quando existir uma variante equivalente (`#minecraft:beds`, `#forge:ingots/iron`, `#minecraft:logs`…); item exato só quando necessário. Nada de NBT exigido sem motivo.
- **Recompensas:**
  - **Caixas de loot** (reward tables do FTB Quests) em 4 raridades: comum, rara, épica, lendária.
  - **Moeda própria** (item KubeJS, ex: "Fragmento de Eco"), ganha em quests.
  - **Loja:** capítulo de quests repetíveis que consomem moedas e dão itens úteis.
  - **Páginas de diário:** itens/livros com trechos da lore, liberados por quest.
- Idioma: **português (PT-BR)**.

## 7. Mods de suporte (minhas escolhas; lista final é do construtor, desde que compatível com 1.20.1 Forge)
- **QoL:** JEI, Jade, AppleSkin, **FTB Ultimine** (vein miner), Xaero's Minimap + World Map, Sophisticated Backpacks, Mouse Tweaks, Inventory sorting, Waystones, FTB Chunks (claim e chunk loading), Corail Tombstone (tumba), Curios, Controlling, Clumps.
- **Litematica (pedido do usuário), para importar construções:** a Litematica original é só para Fabric. No Forge 1.20.1, usar o port **Forgematica** (+ MaFgLib) se houver versão estável para 1.20.1. Se não houver, usar a Litematica Fabric via **Sinytra Connector** + Forgified Fabric API. Isso precisa ser verificado na implementação. É mod só de cliente e fica fora do pacote do servidor. Complemento: o **Schematicannon do Create** imprime schematics `.nbt` no survival. Incluir uma pasta `schematics/` e um guia curto de como importar.
- **Armazenamento:** **Applied Energistics 2**, essencial para um GregTech de 6 meses (minha escolha).
- **Performance:** Embeddium, Oculus (shaders desligados por padrão; Complementary/BSL incluídos), ModernFix, FerriteCore, ImmediatelyFast, Entity Culling.
- **Visual/áudio:** Fresh Animations (+ EMF/ETF), Sound Physics Remastered, AmbientSounds, Falling Leaves, Visuality, FancyMenu + Drippy Loading Screen (menu e tela de carregamento com a arte do pack).
- **Dificuldade:** escalonamento de mobs por progresso/distância (ex: Improved Mobs ou In Control!).

## 8. Imagens (GPT Image 2)
Eu entrego um arquivo `prompts-imagens.md`, com estilo visual unificado (dark fantasy + steampunk/arcano), contendo: logo do pack, fundo do menu principal, tela de carregamento, ícone da instância, ícones dos capítulos, artes dos chefes, ilustrações das páginas de lore, texturas da moeda, das caixas de loot (4 raridades) e das páginas de diário. Para texturas de item, o prompt pede pixel-art em fundo transparente; eu reduzo para 16×16/32×32 e corrijo a paleta. O usuário gera as imagens, coloca numa pasta, e eu integro tudo (resource pack próprio, FancyMenu, quests).

## 9. Garantia de qualidade (anti-bug)
1. **Validação de IDs/tags:** script que lê todas as quests (SNBT) e scripts KubeJS e confere cada item, tag, fluido e entidade contra o dump do registro do jogo (`/kubejs dump_registry` ou export).
2. **Alcançabilidade:** a partir do export de receitas (KubeJS/JEI), verificar que todo item exigido por quest tem um caminho de craft obtenível naquele ponto da progressão, sem ciclos impossíveis.
3. **Dependências de quests:** sem órfãs, sem ciclos, todos os capítulos alcançáveis a partir do Prólogo.
4. **Boot test:** servidor dedicado sobe sem erros nem mods client-only; cliente conecta; log limpo de erros KubeJS.
5. **Playtest guiado:** completar amostras de cada ato via comandos de teste (dar itens, `/ftbquests` para checar se completa).
6. **Compatibilidade de versões** travada via packwiz (hashes).

## 10. Decisões da revisão
**Do usuário:**
- **Compartilhamento livre:** quests são individuais, mas itens, portais, foguetes e máquinas podem ser usados e trocados por todos. Travas são só de receita/KubeJS, sem Game Stages. Cada quest só completa quando o próprio jogador cumpre a task. O chefe final e o "zerar" contam **por jogador** (cada um completa sua quest final, e o chefe pode ser invocado de novo pelo ritual).
- **Lançamento único:** o pack inteiro (todos os atos, quests, lore e imagens) fica pronto e testado **antes** de começarem a jogar.
- **Chefe final:** um chefe existente (Cataclysm ou similar), mais forte, com **nome, textura e ritual de invocação próprios** (Occultism). Os dois desfechos mudam a lore e a recompensa, não a luta. O mesmo vale para os chefes de lore.

**Minhas escolhas (conferir):**
- Meta de **~300 horas por jogador**, com o GregTech indo **até UV**. A Pedra Filosofal e o Artefato do Selo ficam na faixa LuV–ZPM.
- Visuais pesados (Fresh Animations/EMF, Visuality, Sound Physics) ficam **incluídos, mas desativados por padrão**, ou como resource pack opcional. RAM de cliente recomendada: 6 GB.
- Chunk loading via FTB Chunks com limite por jogador, para segurar a carga do servidor com 7 bases de GregTech.

## 11. Ordem de construção (resumo; detalhar com writing-plans após aprovação)
1. Esqueleto packwiz + Forge 1.20.1 + todos os mods, com boot de cliente e servidor limpos.
2. Configs base (performance, dificuldade, FTB, ProjectE desabilitado/gated, Litematica).
3. KubeJS: itens customizados (moeda, páginas, chaves, artefato), receitas cruzadas e gates de cada ato.
4. Lore escrita completa e roteiro de capítulos.
5. Quests FTB (SNBT) de todos os capítulos, loot tables e loja.
6. `prompts-imagens.md` → o usuário gera → eu integro (resource pack, FancyMenu, ícones).
7. QA da seção 9 (validação de IDs/tags, alcançabilidade, dependências, boot, playtest).
8. Export: zip da instância do Prism + pacote do servidor + guia de instalação e hospedagem.

## 12. Verificação de ponta a ponta
- Script de validação de IDs/tags e de dependências das quests sem erros.
- Servidor sobe limpo em `start.bat`; cliente Prism importado do zip conecta.
- Playtest com uma conta de teste: completar a primeira quest de cada capítulo e uma task por tag (cama de cor diferente completa "faça uma cama").
- Os gates funcionam: o portal da Twilight não acende sem o item; a Pedra Filosofal não é craftável antes do Ato V.

## 13. Deixado para o construtor
- Lista final exata de mods de suporte e suas versões (respeitando as categorias acima).
- Texto completo da lore, nomes de capítulos e chefes de lore, número exato de quests.
- Valores de EMC, recompensas e preços da loja.
- Receitas cruzadas específicas de cada gate.
- Configurações de dificuldade de mobs.
