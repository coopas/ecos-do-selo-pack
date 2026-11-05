# Ecos do Selo

Modpack para Minecraft **1.20.1 (Forge)** jogado no **Prism Launcher**: tecnologia (GregTech, Create, AE2), magia (Ars Nouveau, Iron's Spells, Occultism), dimensões (Twilight Forest, Undergarden, Deeper and Darker, Aether, Blue Skies, Ad Astra) e uma alquimia proibida (ProjectE) no fim da jornada.

> ⚠️ Versão de desenvolvimento (0.1.x): mods e configs base. Quests, lore e conteúdo chegam nas próximas versões.

## Como instalar (jogadores)
1. Instale o [Prism Launcher](https://prismlauncher.org/) e entre com sua conta Microsoft.
2. Baixe o arquivo `EcosDoSelo-<versão>.zip` da página de releases.
3. No Prism: **Adicionar instância → Importar → selecione o zip**.
4. Abra a instância. Na primeira vez, uma janela baixa todos os mods; espere terminar.
5. Se o Prism perguntar qual Java usar, aceite baixar o **Java 17**.

Atualizações do pack são baixadas sozinhas toda vez que você abre o jogo.

### Desempenho
- 6 GB de RAM já vêm configurados na instância.
- **Shaders** vêm instalados, mas desligados: *Opções → Vídeo → Shader Packs* (Complementary ou BSL).
- **Fresh Animations** (animações de mobs) também vem desligado: *Opções → Pacotes de recursos*.

### Mapa, zoom e distância de visão
- **Mapa:** Xaero's Minimap + World Map. O FTB Chunks fica só para reivindicar e manter chunks carregados
  (o minimapa dele vem desligado; o mapa dele ainda abre para clicar nos chunks).
- **Zoom:** Just Zoom (tecla em *Opções → Controles*).
- **Distant Horizons:** mostra terreno muito além da distância de renderização, só no cliente.
  Se pesar no seu PC, diminua a qualidade no botão dele em *Opções → Vídeo*.
- **Lixeira no inventário:** Trash Slot (o espaço de lixo fica ao lado do inventário).
- **Loot de baús por jogador:** Lootr. Cada baú de estrutura (dungeon, templo, Twilight etc.) tem um loot
  separado para cada amigo: quem abre primeiro não leva o de todo mundo. Para quebrar um baú desses, agache.

### Litematica (construções)
O Litematica original é só para Fabric; aqui ele vem como **Forgematica** (o mesmo mod adaptado para Forge,
com a biblioteca MaFgLib). Coloque arquivos `.litematic` em `.minecraft/schematics` (pasta da instância → `minecraft/schematics`). Abra o menu com a tecla **M**. No survival, o **Schematicannon** do Create imprime construções `.nbt`.

## Vapor, rotação e energia (GregTech × Create)
Três blocos ligam o vapor do GregTech, a rotação do Create e a energia (EU) do GregTech:
- **Motor a Vapor do Eco**: recebe vapor do GregTech por cano e gira o Create a **32 RPM**, com até **1920 SU**
  queimando **80 mB/t** (menos vapor = menos SU). **Ele queima vapor mesmo sem nada ligado no eixo.**
- **Dínamo Cinético (ULV / LV)**: recebe rotação e solta EU na face oposta ao eixo: **ULV 8 EU/t**, **LV 32 EU/t**.
  Conta a velocidade em módulo (qualquer sentido serve); a produção cheia vem a partir de **64 RPM**
  (a 32 RPM, metade). Ele pesa bastante na rede: ULV 32 SU e LV 128 SU por RPM, ou seja, a 64 RPM o **ULV pede
  2048 SU** e o **LV pede 8192 SU** (256 SU para cada EU/t). Exemplos: um moinho pequeno (8 velas, 512 SU) dá
  **≈ 2 EU/t**; um motor a vapor do Create numa caldeira com blaze (16384 SU) dá **≈ 64 EU/t**. Um Motor a Vapor do
  Eco dá no máximo 1920 SU, então um dínamo LV cheio só com eles precisa de **vários motores** (5 ou mais).
  Regra do GregTech: o dínamo **LV** encostado numa máquina **ULV** dá sobretensão e a máquina explode.
- **Saída de Vapor**: encoste num tanque de uma caldeira do Create com queimador. Ela entrega **6 mB/t de vapor por
  nível da caldeira** e gasta a água da caldeira. **Caldeira com motor a vapor do Create ou com apito não solta vapor
  pela Saída** (ou a caldeira é do Create, ou é da Saída).

O ciclo vapor → rotação → EU **perde energia**: o vapor rende bem menos EU passando pelo motor e pelo dínamo do que
queimado direto numa máquina a vapor do GregTech.

Também:
- **Diesel e gasolina** servem nos dois mods: os motores do mod Create: Diesel Generators queimam os do GregTech, e os
  geradores de combustão do GregTech queimam os do Diesel Generators.
- O Create **mói e lava os minérios do GregTech**, mas rende **menos** que as máquinas do GregTech (é o atalho sem
  energia elétrica).
- **Redstone pelo Create**: moer cascalho nas rodas trituradoras às vezes dá pó de redstone (10 %). Mas as rodas são
  feitas no montador mecânico, que pede gema de fonte (Ars Nouveau), então isso só vale a partir do Ato II.

## Servidor
Veja `tools/server_template/LEIA-ME-SERVIDOR.md` (vai junto no pacote do servidor).

## Desenvolvimento
- `python tools/add_mods.py`: aplica `tools/mods.csv` ao pack.
- `python tools/check_manifest.py`: valida o pack.
- `python tools/build_server.py`: monta `build/server`.
- `python tools/boot_test.py server [--dev]` / `client`: sobe o jogo de verdade e procura erros nos logs.
- `python -m pytest -q`: testes das ferramentas.
