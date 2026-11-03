# Ecos do Selo — Servidor

## Requisitos
- Java 17 (Temurin 17 recomendado). Se tiver outro Java instalado, defina `JAVA17_HOME`.
- 10 GB de RAM livres para o servidor (12 GB se passar de 8 jogadores) (ajuste `-Xmx` em `user_jvm_args.txt`).

## Primeira vez
1. Leia a EULA do Minecraft (https://aka.ms/MinecraftEULA) e troque `eula=false` por `eula=true` em `eula.txt`.
2. Windows: dê dois cliques em `start.bat`. Linux/VPS: `chmod +x start.sh && ./start.sh`.
3. Espere aparecer `Done (...)!` — o primeiro início demora alguns minutos.

## Deixar os amigos entrarem
- **Mesma casa/rede:** use o IP local da máquina.
- **Pela internet, sem mexer no roteador:** use o playit.gg (crie um túnel "Minecraft Java" para a porta 25565 e passe o endereço gerado aos amigos).
- **Abrindo porta:** redirecione a porta TCP 25565 no roteador para esta máquina e libere no firewall.
- **Hospedagem paga/VPS:** envie esta pasta inteira e rode `start.sh` (ou o comando de início da host apontando para os mesmos argumentos).

## Comandos úteis
- `op <nick>` — dá admin a um jogador.
- `whitelist on` + `whitelist add <nick>` — só amigos entram.
- `stop` — desliga salvando o mundo. Nunca feche a janela sem `stop`.

## Backup
Copie a pasta `world` com o servidor desligado. Faça antes de qualquer atualização do pack.
