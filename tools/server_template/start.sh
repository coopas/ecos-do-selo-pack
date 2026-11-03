#!/usr/bin/env sh
cd "$(dirname "$0")"
JAVA="${JAVA17_HOME:+$JAVA17_HOME/bin/}java"
if ! "$JAVA" -version 2>&1 | grep -Eq 'version "17([."]|$)'; then
  echo "[Ecos do Selo] Java 17 nao encontrado. Instale o Java 17 ou defina JAVA17_HOME."
  exit 1
fi
if ! grep -q "eula=true" eula.txt; then
  echo "[Ecos do Selo] Leia https://aka.ms/MinecraftEULA e troque eula=false por eula=true em eula.txt."
  exit 1
fi
if [ -f pack-url.txt ]; then
  echo "[Ecos do Selo] Verificando atualizacoes do modpack..."
  "$JAVA" -jar packwiz-installer-bootstrap.jar -g -s server "$(cat pack-url.txt)" || echo "[Ecos do Selo] AVISO: nao foi possivel atualizar os mods."
fi
exec "$JAVA" @user_jvm_args.txt @libraries/net/minecraftforge/forge/1.20.1-FORGEVER/unix_args.txt nogui "$@"
