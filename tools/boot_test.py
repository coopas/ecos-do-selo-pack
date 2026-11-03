"""Sobe servidor/cliente de verdade e analisa os logs."""
import argparse
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


def server(server_dir: Path = BUILD / "server", timeout_s: int = 900, dev: bool = False) -> list[str]:
    (server_dir / "eula.txt").write_text("eula=true\n")  # só no build local de teste
    flag = server_dir / "kubejs" / "config" / "dev.flag"
    if dev:
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text("dev\n")
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
    log = server_dir / "logs" / "latest.log"
    if log.exists():
        problems += log_scan.scan(log.read_text(encoding="utf-8", errors="replace"))
    for crash in (server_dir / "crash-reports").glob("*.txt") if (server_dir / "crash-reports").exists() else []:
        if crash.stat().st_mtime >= start:
            problems.append(f"crash report: {crash.name}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", choices=["server", "client"])
    ap.add_argument("--dev", action="store_true")
    a = ap.parse_args()
    if a.target == "server":
        problems = server(dev=a.dev)
    else:
        problems = client()  # noqa: F821 (Task 6)
    for p in problems:
        print("PROBLEMA:", p)
    print(f"{len(problems)} problemas")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
