"""Sobe servidor/cliente de verdade e analisa os logs."""
import argparse
import os
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path

import build_server
import log_scan
from paths import BUILD, JAVA17


def server_cmd(server_dir: Path, forge_version: str) -> list[str]:
    return [str(JAVA17), "@user_jvm_args.txt",
            f"@libraries/net/minecraftforge/forge/1.20.1-{forge_version}/win_args.txt", "nogui"]


def _pump(stream, q):
    for line in iter(stream.readline, ""):
        q.put(line)
    q.put(None)


def server(server_dir: Path = BUILD / "server", timeout_s: int = 900, dev: bool = False,
           after_done=None) -> list[str]:
    """after_done(q) roda com o servidor no ar (q = fila de linhas do console) e retorna problemas."""
    with build_server.eula_accepted(server_dir):  # EULA aceita só durante o teste; arquivo restaurado depois
        return _server(server_dir, timeout_s, dev, after_done)


def _server(server_dir: Path, timeout_s: int, dev: bool, after_done=None) -> list[str]:
    flag = server_dir / "kubejs" / "config" / "dev.json"
    if dev:
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text('{"dev": true}\n')
        (server_dir / "kubejs" / "exported").mkdir(parents=True, exist_ok=True)  # JsonIO.write não cria pastas
    else:
        flag.unlink(missing_ok=True)
    proc = subprocess.Popen(server_cmd(server_dir, build_server.forge_version()), cwd=server_dir,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace")
    q: queue.Queue = queue.Queue()
    threading.Thread(target=_pump, args=(proc.stdout, q), daemon=True).start()
    problems, done, start = [], False, time.time()
    while time.time() - start < timeout_s:
        try:
            line = q.get(timeout=5)
        except queue.Empty:
            continue
        if line is None:
            break
        if "Done (" in line and "For help" in line:
            done = True
            print(f"servidor subiu em {time.time() - start:.0f}s")
            if dev:
                time.sleep(20)  # deixa o dump do registro terminar
            if after_done:
                problems += after_done(q)
            proc.stdin.write("stop\n")
            proc.stdin.flush()
            break
    try:
        proc.wait(timeout=180)
    except subprocess.TimeoutExpired:
        proc.kill()
        problems.append("servidor não parou com stop")
    if not done:
        problems.append("timeout/crash: servidor não chegou em Done")
    dump = server_dir / "kubejs" / "exported" / "registry_dump.json"
    if dev:
        if dump.exists() and dump.stat().st_mtime >= start:
            import shutil
            shutil.copy2(dump, BUILD / "registry_dump.json")
        else:
            problems.append("registry_dump.json não foi gerado")
    for log in (server_dir / "logs" / "latest.log", server_dir / "logs" / "kubejs" / "server.log",
                server_dir / "logs" / "kubejs" / "startup.log"):
        if log.exists() and log.stat().st_mtime >= start:
            problems += log_scan.scan(log.read_text(encoding="utf-8", errors="replace"))
    for crash in (server_dir / "crash-reports").glob("*.txt") if (server_dir / "crash-reports").exists() else []:
        if crash.stat().st_mtime >= start:
            problems.append(f"crash report: {crash.name}")
    return problems


DEV_INSTANCE = "EcosDoSelo-dev"
PRISM_EXE = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "PrismLauncher" / "prismlauncher.exe"
CLIENT_MARKERS = ("Sound engine started", "minecraft:textures/atlas/blocks.png-atlas")


def client_ready(log_text: str) -> bool:
    return all(m in log_text for m in CLIENT_MARKERS)


def _kill_instance_java(instance: str) -> None:
    ps = (r"Get-CimInstance Win32_Process | Where-Object { ($_.Name -match '^javaw?\.exe$') -and "
          f"($_.CommandLine -like '*{instance}*') }} | ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force }}")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True)


def client_died(log_started: bool, java_running: bool) -> bool:
    return log_started and not java_running


def _instance_java_running(instance: str) -> bool:
    ps = (r"@(Get-CimInstance Win32_Process | Where-Object { ($_.Name -match '^javaw?\.exe$') -and "
          f"($_.CommandLine -like '*{instance}*') }}).Count")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
    return out.stdout.strip() not in ("", "0")


RELEASE_INSTANCE = "EcosDoSelo-release"


def player_joined(line: str) -> bool:
    return "joined the game" in line


def client_launch_args(profile: str | None, instance: str = DEV_INSTANCE, server: str | None = None) -> list[str]:
    # Offline não baixa bibliotecas do Forge: a 1a abertura de uma instância nova precisa de --profile (conta real).
    account = ["--profile", profile] if profile else ["--offline", "EcosTeste"]
    join = ["--server", server] if server else []
    return [str(PRISM_EXE), "--launch", instance, *account, *join]


def join(pack_url: str, profile: str, timeout_s: int = 1200) -> list[str]:
    """Fluxo real dos amigos: servidor instalado do GitHub + instância Prism do zip; o jogador entra no servidor."""
    import shutil
    import build_prism
    from paths import PRISM
    build_server.build(BUILD / "server", pack_url=pack_url)
    build_prism.build(pack_url)
    inst = PRISM / "instances" / RELEASE_INSTANCE

    def after_done(q) -> list[str]:
        shutil.copytree(BUILD / "prism", inst, dirs_exist_ok=True)
        start = time.time()
        subprocess.Popen(client_launch_args(profile, RELEASE_INSTANCE, "localhost"))
        joined = False
        while time.time() - start < timeout_s and not joined:
            try:
                line = q.get(timeout=10)
            except queue.Empty:
                continue
            if line and player_joined(line):
                joined = True
                print(f"jogador entrou no servidor em {time.time() - start:.0f}s")
                time.sleep(30)
        problems = [] if joined else ["jogador não conseguiu entrar no servidor"]
        logs = inst / "minecraft" / "logs"
        for lg in (logs / "latest.log", logs / "kubejs" / "client.log"):
            if lg.exists() and lg.stat().st_mtime >= start:
                problems += [f"[cliente] {p}" for p in log_scan.scan(lg.read_text(encoding="utf-8", errors="replace"))]
        _kill_instance_java(RELEASE_INSTANCE)
        return problems

    return server(BUILD / "server", timeout_s=timeout_s, after_done=after_done)


def client(timeout_s: int = 1800, profile: str | None = None) -> list[str]:
    import shutil
    import build_prism
    from paths import PRISM
    inst = PRISM / "instances" / DEV_INSTANCE
    log = inst / "minecraft" / "logs" / "latest.log"
    with build_server.serve_pack() as url:
        staged = BUILD / "prism-dev"
        build_prism.build(url, out=staged, name=DEV_INSTANCE)
        shutil.copytree(staged, inst, dirs_exist_ok=True)
        start = time.time()
        subprocess.Popen(client_launch_args(profile))  # instância dev
        ready = False
        while time.time() - start < timeout_s:
            time.sleep(10)
            crashes_dir = inst / "minecraft" / "crash-reports"
            if crashes_dir.exists() and any(c.stat().st_mtime >= start for c in crashes_dir.glob("*.txt")):
                break
            log_started = log.exists() and log.stat().st_mtime >= start
            if client_died(log_started, _instance_java_running(DEV_INSTANCE)):
                time.sleep(5)
                if client_died(log_started, _instance_java_running(DEV_INSTANCE)):
                    print("processo do jogo encerrou antes do menu")
                    break
            if log_started:
                if client_ready(log.read_text(encoding="utf-8", errors="replace")):
                    ready = True
                    print(f"cliente chegou ao menu em {time.time() - start:.0f}s")
                    time.sleep(20)
                    break
    problems = [] if ready else ["timeout/crash: cliente não chegou ao menu"]
    for lg in (log, inst / "minecraft" / "logs" / "kubejs" / "client.log",
               inst / "minecraft" / "logs" / "kubejs" / "startup.log"):
        if lg.exists() and lg.stat().st_mtime >= start:
            problems += log_scan.scan(lg.read_text(encoding="utf-8", errors="replace"))
    _kill_instance_java(DEV_INSTANCE)
    crashes = inst / "minecraft" / "crash-reports"
    for crash in crashes.glob("*.txt") if crashes.exists() else []:
        if crash.stat().st_mtime >= start:
            problems.append(f"crash report: {crash.name}")
    return problems


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("target", choices=["server", "client", "join"])
    ap.add_argument("--url", help="URL do pack.toml publicado (modo join)")
    ap.add_argument("--dev", action="store_true")
    ap.add_argument("--profile", help="conta do Prism (necessário na 1a abertura da instância)")
    a = ap.parse_args()
    if a.target == "server":
        problems = server(dev=a.dev)
    elif a.target == "join":
        problems = join(a.url, a.profile)
    else:
        problems = client(profile=a.profile)
    for p in problems:
        print("PROBLEMA:", p)
    print(f"{len(problems)} problemas")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
