
import os
# ===== 手动指定 Tk 路径（必须在 import tkinter 之前）=====
os.environ["TCL_LIBRARY"] = r"C:\Users\admin\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"
os.environ["TK_LIBRARY"] = r"C:\Users\admin\AppData\Local\Programs\Python\Python313\tcl\tk8.6"

import paramiko
import time
import requests
import threading
import tkinter as tk
from tkinter import ttk

# ========= 基本配置 =========
HOST = "8.138.152.168"
PORT = 22
USER = "root"

SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_ed25519")
SERVICE_NAME = "game-payment-service"

CHECK_INTERVAL = 60
MAX_RETRY = 5

# ========= 钉钉告警配置 =========
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=670618645233149d94833cd18e04510abba4e427003acd1a5fc563c0416db958"
DINGTALK_KEYWORD = "流失展示业务"

# ========= 全局状态 + 锁 =========
current_status = "未知"
last_check_time = "-"
last_action = "-"
state_lock = threading.Lock()


def send_dingtalk_alarm(message):
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"{DINGTALK_KEYWORD}\n{message}"
        }
    }
    try:
        requests.post(DINGTALK_WEBHOOK, json=payload, timeout=5)
    except:
        pass


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
        return stdout.read().decode().strip(), stderr.read().decode().strip()
    finally:
        client.close()


def check_service_status():
    out, err = ssh_exec(f"systemctl is-active {SERVICE_NAME}")
    if err:
        return "unknown"
    return out


def restart_service_with_retry():
    global current_status, last_action, last_check_time

    for _ in range(MAX_RETRY):
        ssh_exec(f"systemctl restart {SERVICE_NAME}")
        time.sleep(3)

        status = check_service_status()
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        if status == "active":
            # ✅ 重启成功：立即同步所有状态
            with state_lock:
                current_status = "active"
                last_check_time = now
                last_action = "重启成功"

            send_dingtalk_alarm(
                f"重启流水展示业务{SERVICE_NAME}成功,我要去蛋糕夫人家里继续做蛋糕啦！😄。"
            )
            return

    # ❌ 连续失败
    with state_lock:
        current_status = "failed"
        last_check_time = time.strftime("%Y-%m-%d %H:%M:%S")
        last_action = "重启失败"

    send_dingtalk_alarm(
        f"邪恶女巫阻止了我重启流水展示业务{SERVICE_NAME}！！！"
    )


def monitor_loop():
    global current_status, last_check_time, last_action

    while True:
        status = check_service_status()
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        with state_lock:
            current_status = status
            last_check_time = now

        if status != "active":
            with state_lock:
                last_action = "检测到停止，尝试重启"

            send_dingtalk_alarm(
                f"啊！目标服务单元{SERVICE_NAME}它停止啦！😭碧琪正在重启流水展示业务{SERVICE_NAME}！"
            )
            restart_service_with_retry()
        else:
            with state_lock:
                last_action = "运行正常"

        time.sleep(CHECK_INTERVAL)


# ========= GUI =========
def start_gui():
    root = tk.Tk()
    root.title("服务监控面板")
    root.geometry("400x220")

    ttk.Label(root, text="服务名称：").pack()
    ttk.Label(root, text=SERVICE_NAME, font=("Arial", 14)).pack()

    status_label = ttk.Label(root, font=("Arial", 12))
    status_label.pack(pady=5)

    time_label = ttk.Label(root)
    time_label.pack()

    action_label = ttk.Label(root)
    action_label.pack(pady=5)

    def refresh():
        with state_lock:
            status = current_status
            check_time = last_check_time
            action = last_action

        status_label.config(text=f"当前状态：{status}")
        time_label.config(text=f"上次检测：{check_time}")
        action_label.config(text=f"最近操作：{action}")

        root.after(1000, refresh)

    refresh()
    root.mainloop()


if __name__ == "__main__":
    threading.Thread(target=monitor_loop, daemon=True).start()
    start_gui()
