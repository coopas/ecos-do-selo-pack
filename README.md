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

### Litematica (construções)
Coloque arquivos `.litematic` em `.minecraft/schematics` (pasta da instância → `minecraft/schematics`). Abra o menu com a tecla **M**. No survival, o **Schematicannon** do Create imprime construções `.nbt`.

## Servidor
Veja `tools/server_template/LEIA-ME-SERVIDOR.md` (vai junto no pacote do servidor).

## Desenvolvimento
- `python tools/add_mods.py`: aplica `tools/mods.csv` ao pack.
- `python tools/check_manifest.py`: valida o pack.
- `python tools/build_server.py`: monta `build/server`.
- `python tools/boot_test.py server [--dev]` / `client`: sobe o jogo de verdade e procura erros nos logs.
- `python -m pytest -q`: testes das ferramentas.
