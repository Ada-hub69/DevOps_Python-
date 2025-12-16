import paramiko
import time

HOST = '192.168.170.5'
PORT = 22
USER = 'root'
PASSWORD = 'e=mc*2f=ma'
MYSQL_SERVICE = 'mysqld'

def ssh_exec(command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=HOST,
            port=PORT,
            username=USER,
            password=PASSWORD,
            timeout=10
        )
        stdin, stdout, stderr = client.exec_command(command)
        stdout_data = stdout.read().decode().strip()
        stderr_data = stderr.read().decode().strip()
        return stdout_data, stderr_data
    finally:
        client.close()

def restart_mysql():
    print(f"开始远程重启 MySQL（{HOST}）...")

    # 执行重启
    _, error = ssh_exec(f"systemctl restart {MYSQL_SERVICE}")
    if error:
        print("MySQL 重启命令执行失败：")
        print(error)
        return

    # 等待服务恢复
    time.sleep(3)

    # 检查状态
    status, _ = ssh_exec(f"systemctl is-active {MYSQL_SERVICE}")
    if status == "active":
        print("MySQL 重启成功 ✅")
    else:
        print("MySQL 重启失败 ❌")
        print("当前状态：", status)

def main():
    choice = input(
        f"是否确认远程重启 {HOST} 上的 MySQL？(y/n): "
    ).strip().lower()

    if choice == 'y':
        restart_mysql()
    else:
        print("已取消操作")

if __name__ == "__main__":
    main()
