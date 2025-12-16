
import paramiko
HOST='192.168.170.5'
PORT=22
USER='root'
PASSWORD='e=mc*2f=ma'
def ssh_execs(command):
    client=paramiko.SSHClient()
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
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        return output,error
    finally:
        client.close()
def is_mysql_running():
    output,error=ssh_execs("systemctl is-active mysqld")
    if error:
        print("远程链接错误",error)
        return False
    return output == "active"
def restart_nginx():
    output,error=ssh_execs("systemctl restart mysqld")
    if error:
        print("Mysql重启失败",error)
    else:
        print("Mysql重启成功！")
def main():
    print(f"正在检查远程服务器{HOST}的Mysql运行状况......")
    if is_mysql_running():
        print("mysql正在运行......")
    else:
        print("mysql没有在运行！")
        choice=input("是否进行mysql远程重启？（y/n）").strip().lower()
        if choice =='y':
            restart_nginx()
        else:
            print("已经取消重启")
if __name__=="__main__":
    main()