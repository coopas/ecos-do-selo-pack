import boot_test
from paths import JAVA17


def test_server_cmd_uses_java17_and_forge_args(tmp_path):
    cmd = boot_test.server_cmd(tmp_path, "47.4.28")
    assert cmd[0] == str(JAVA17)
    assert "@user_jvm_args.txt" in cmd
    assert "@libraries/net/minecraftforge/forge/1.20.1-47.4.28/win_args.txt" in cmd
    assert cmd[-1] == "nogui"
