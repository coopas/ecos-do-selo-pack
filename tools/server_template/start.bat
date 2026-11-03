@echo off
setlocal
cd /d "%~dp0"
title Ecos do Selo - Servidor
set "JAVA=java"
if defined JAVA17_HOME set "JAVA=%JAVA17_HOME%\bin\java.exe"
"%JAVA%" -version 2>&1 | findstr /r /c:"version .17[^0-9]" >nul
if errorlevel 1 (
  echo [Ecos do Selo] Java 17 nao encontrado.
  echo Instale o Java 17 ^(https://adoptium.net/temurin/releases/?version=17^)
  echo ou defina a variavel JAVA17_HOME apontando para a pasta do Java 17.
  pause
  exit /b 1
)
findstr /c:"eula=true" eula.txt >nul
if errorlevel 1 (
  echo [Ecos do Selo] Leia a EULA do Minecraft ^(https://aka.ms/MinecraftEULA^) e troque eula=false por eula=true no arquivo eula.txt.
  pause
  exit /b 1
)
if exist pack-url.txt set /p PACKURL=<pack-url.txt
if defined PACKURL (
  echo [Ecos do Selo] Verificando atualizacoes do modpack...
  "%JAVA%" -jar packwiz-installer-bootstrap.jar -g -s server %PACKURL%
  if errorlevel 1 echo [Ecos do Selo] AVISO: nao foi possivel atualizar os mods. Iniciando com a versao atual.
)
"%JAVA%" @user_jvm_args.txt @libraries/net/minecraftforge/forge/1.20.1-FORGEVER/win_args.txt nogui %*
pause
