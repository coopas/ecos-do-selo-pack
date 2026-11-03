import boot_test
from paths import JAVA17


def test_server_cmd_uses_java17_and_forge_args(tmp_path):
    cmd = boot_test.server_cmd(tmp_path, "47.4.28")
    assert cmd[0] == str(JAVA17)
    assert "@user_jvm_args.txt" in cmd
    assert "@libraries/net/minecraftforge/forge/1.20.1-47.4.28/win_args.txt" in cmd
    assert cmd[-1] == "nogui"


def test_client_ready_needs_sound_and_atlas():
    assert not boot_test.client_ready("[x] Sound engine started\n")
    assert boot_test.client_ready("[x] Sound engine started\n[y] Created: 4096x2048x4 minecraft:textures/atlas/blocks.png-atlas\n")


def test_client_launch_args_offline_by_default():
    args = boot_test.client_launch_args(None)
    assert args[1:] == ["--launch", boot_test.DEV_INSTANCE, "--offline", "EcosTeste"]


def test_client_launch_args_with_profile():
    args = boot_test.client_launch_args("c9pas")
    assert args[1:] == ["--launch", boot_test.DEV_INSTANCE, "--profile", "c9pas"]


def test_client_died_when_log_exists_and_no_java():
    assert boot_test.client_died(log_started=True, java_running=False)


def test_client_not_died_before_log_or_while_running():
    assert not boot_test.client_died(log_started=False, java_running=False)
    assert not boot_test.client_died(log_started=True, java_running=True)
