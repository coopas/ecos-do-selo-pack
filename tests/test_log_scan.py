from pathlib import Path

import log_scan

FIX = Path(__file__).parent / "fixtures"


def scan(name):
    return log_scan.scan((FIX / name).read_text())


def test_invalid_dist_detected():
    problems = scan("log_invalid_dist.txt")
    assert any("invalid dist" in p for p in problems)


def test_missing_dep_detected():
    problems = scan("log_missing_dep.txt")
    assert any("Missing or unsupported mandatory dependencies" in p for p in problems)


def test_kubejs_error_detected():
    problems = scan("log_kubejs_error.txt")
    assert any("KubeJS" in p for p in problems)


def test_clean_log_ok():
    assert scan("log_clean.txt") == []


def test_rhino_reflection_probe_ignored():
    assert scan("log_rhino_probe.txt") == []


def test_lone_distxform_still_reported():
    text = "[x] [main/ERROR] [net.minecraftforge.fml.loading.RuntimeDistCleaner/DISTXFORM]: Attempted to load class net/minecraft/client/Minecraft for invalid dist DEDICATED_SERVER\n"
    assert len(log_scan.scan(text)) == 1


def test_kubejs_own_log_error_detected():
    problems = scan("kubejs_server_error.txt")
    assert any("Error in 'ServerEvents.loaded'" in p for p in problems)


def test_kubejs_stacktrace_lines_not_repeated():
    text = "[18:43:04] [ERROR] ! Error in 'X': boom\n[18:43:04] [ERROR] !   at foo.Bar(Bar.java:1)\n"
    assert log_scan.scan(text) == ["[18:43:04] [ERROR] ! Error in 'X': boom"]
