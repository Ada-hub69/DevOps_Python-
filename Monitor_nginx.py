import paramiko


# ======================
# 服务器配置
# ======================
HOST = "192.168.170.5"
PORT = 22
USER = "root"
PASSWORD = "e=mc*2f=ma"   # 后面我们会改成 SSH key


def ssh_exec(command):
    """
    在远程服务器执行命令
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(  #类里面调用了方法，并且向里面传递了如下参数
            hostname=HOST,
            port=PORT,
            username=USER,
            password=PASSWORD,
            timeout=10
        )

        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        return output, error

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
