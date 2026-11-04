#!/bin/sh
# Recompila tools/ecosbridge/ecosbridge-1.0.0.jar e copia para pack/mods. Precisa de build/server/mods (rode build_server antes).
set -e
cd "$(dirname "$0")"
L="$APPDATA/PrismLauncher/libraries"; M=../../build/server/mods; J="$APPDATA/PrismLauncher/java/java-runtime-gamma/bin"
CP=""; for f in "$L"/net/minecraft/client/1.20.1-20230612.114412/client-1.20.1-20230612.114412-srg.jar "$L"/net/minecraftforge/fmlcore/1.20.1-47.4.28/*.jar "$L"/net/minecraftforge/javafmllanguage/1.20.1-47.4.28/*.jar "$L"/net/minecraftforge/eventbus/*/*.jar "$L"/org/slf4j/slf4j-api/*/*.jar "$L"/net/minecraftforge/forge/1.20.1-47.4.28/forge-1.20.1-47.4.28-universal.jar $M/ftb-quests*.jar $M/ftb-filter-system*.jar; do [ -f "$f" ] && CP="$CP$(cygpath -w "$f");"; done
rm -rf out && mkdir out && "$J/javac.exe" --release 17 -nowarn -cp "$CP" -d out src/ecos/bridge/EcosBridge.java
cp -r res/* out/ && (cd out && "$J/jar.exe" cf ../ecosbridge-1.0.0.jar .)
cp ecosbridge-1.0.0.jar ../../pack/mods/
