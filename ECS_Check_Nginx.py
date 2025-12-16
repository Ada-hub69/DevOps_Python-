import paramiko
import time
import os

HOST = '192.168.170.5'
PORT = 22
USER = 'root'

# 私钥路径（Windows / Linux 通用写法）
SSH_KEY_PATH = os.path.expanduser("C:/Users/admin/.ssh/id_ed25519")
def ssh_exec(command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=HOST,
            port=PORT,
            username=USER,
            key_filename=SSH_KEY_PATH,
            timeout=10
        )

        stdin, stdout, stderr = client.exec_command(command)
        stdout_data = stdout.read().decode().strip()
        stderr_data = stderr.read().decode().strip()
        return stdout_data, stderr_data

    finally:
        client.close()
def is_nginx_running():
    """
    远程检查 nginx 状态
    """
    output, error = ssh_exec("systemctl is-active nginx")

    if error:
        print("远程错误：", error)
        return False

    return output == "active"


def restart_nginx():
    """
    远程重启 nginx
    """
    output, error = ssh_exec("systemctl restart nginx")

    if error:
        print("❌ nginx 重启失败：", error)
    else:
        print("✅ nginx 已在远程服务器重启")


def main():
    print(f"🔍 正在检查远程服务器 {HOST} 的 nginx 状态...")

    if is_nginx_running():
        print("✅ nginx 正在运行")
    else:
        print("⚠ nginx 未运行")

        choice = input("是否远程重启 nginx？(y/n)：").strip().lower()
        if choice == "y":
            restart_nginx()
        else:
            print("⏹ 已取消重启")


if __name__ == "__main__":
    main()