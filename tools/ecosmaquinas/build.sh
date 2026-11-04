#!/bin/sh
# Recompila tools/ecosmaquinas/ecosmaquinas-1.0.0.jar e copia para pack/mods. Precisa de build/server/mods (rode build_server antes).
# Compila contra Create e GregTech; os jars aninhados deles (META-INF/jarjar: Ponder, Registrate, flywheel, ldlib...)
# são extraídos para build/cache/jarjar só para o classpath; não vão no nosso jar.
set -e
cd "$(dirname "$0")"
L="$APPDATA/PrismLauncher/libraries"; M=../../build/server/mods; J="$APPDATA/PrismLauncher/java/java-runtime-gamma/bin"
JJ=../../build/cache/jarjar
CREATE=$(ls $M/create-1.20.1-*.jar | head -1); GT=$(ls $M/gtceu-1.20.1-*.jar | head -1)
[ -f "$CREATE" ] && [ -f "$GT" ] || { echo "faltam os jars do Create/GregTech em $M (rode tools/build_server.py)"; exit 1; }
rm -rf "$JJ" && mkdir -p "$JJ"
for j in "$CREATE" "$GT"; do (cd "$JJ" && "$J/jar.exe" xf "$(cygpath -w "$OLDPWD/$j")" META-INF/jarjar); done
CP=""; for f in "$L"/net/minecraft/client/1.20.1-20230612.114412/client-1.20.1-20230612.114412-srg.jar "$L"/net/minecraftforge/fmlcore/1.20.1-47.4.28/*.jar "$L"/net/minecraftforge/fmlloader/1.20.1-47.4.28/*.jar "$L"/net/minecraftforge/mergetool/*/mergetool-*-api.jar "$L"/net/minecraftforge/javafmllanguage/1.20.1-47.4.28/*.jar "$L"/net/minecraftforge/eventbus/*/*.jar "$L"/net/minecraftforge/forgespi/*/*.jar "$L"/org/slf4j/slf4j-api/*/*.jar "$L"/com/mojang/datafixerupper/*/*.jar "$L"/com/mojang/brigadier/*/*.jar "$L"/net/minecraftforge/forge/1.20.1-47.4.28/forge-1.20.1-47.4.28-universal.jar "$CREATE" "$GT" "$JJ"/META-INF/jarjar/*.jar; do [ -f "$f" ] && CP="$CP$(cygpath -w "$f");"; done
# Stub do AT do Forge (BlockEntitySupplier público): compila à parte e entra ANTES do Minecraft no classpath; não vai no jar.
ST=../../build/cache/ecosmaquinas-stubs
rm -rf "$ST" && mkdir -p "$ST" && "$J/javac.exe" --release 17 -nowarn -encoding UTF-8 -cp "$CP" -d "$ST" stubs/net/minecraft/world/level/block/entity/BlockEntityType.java
rm -rf out && mkdir out && "$J/javac.exe" --release 17 -nowarn -encoding UTF-8 -cp "$(cygpath -w "$ST");$CP" -d out $(find src -name '*.java')
[ -z "$(find out -path 'out/net/*' -print -quit)" ] || { echo "stub vazou para o jar"; exit 1; }
cp -r res/* out/ && (cd out && "$J/jar.exe" cf ../ecosmaquinas-1.0.0.jar .)
cp ecosmaquinas-1.0.0.jar ../../pack/mods/
echo "ok: pack/mods/ecosmaquinas-1.0.0.jar"
