#!/usr/bin/env python3

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import atexit
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from rope import Coordinator
from rope.license_utils import validate_activation_code, save_license_info, check_license
from datetime import datetime
import os
from pathlib import Path
import logging
import webbrowser
from rope.payment import PaymentAPI
import requests
from rope.version import version_checker

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def cleanup():
    try:
        tk.Tk().destroy()
    except:
        pass

atexit.register(cleanup)

def initialize_license_system():
    BASE_DIR = Path(__file__).resolve().parent
    TOOLS_DIR = BASE_DIR / 'tools'
    LICENSE_ENC_PATH = TOOLS_DIR / 'license.enc'

    os.makedirs(TOOLS_DIR, exist_ok=True)

def show_activation_dialog(root):
    logging.debug("Showing activation dialog")
    try:
        dialog = tk.Toplevel(root)
        dialog.title("软件激活")
        dialog.geometry("300x220")
        dialog.resizable(False, False)
        dialog.configure(bg='#F0F0E0')

        # 设置关闭窗口时退出程序
        dialog.protocol("WM_DELETE_WINDOW", lambda: sys.exit())

        try:
            style = ttk.Style()
            style.theme_use('clam')
            style.configure('TLabel', background='#F0F0E0')
            style.configure('TEntry', fieldbackground='white')
            style.configure('TButton', background='#E0E0D0')
            style.configure('TFrame', background='#F0F0E0')
            logging.debug("Style configuration completed")
        except Exception as e:
            logging.error(f"Error configuring style: {e}")

        main_frame = ttk.Frame(dialog, padding="20 20 20 20", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 保存对图像的引用
        dialog.image_refs = []  # 防止图像被垃圾回收

        def activate():
            try:
                activation_code = activation_code_entry.get().strip()
                logging.debug(f"Attempting to activate with code: {activation_code}")
                result = validate_activation_code(activation_code)
                if result:
                    generation_date, expiration_date = result
                    save_license_info(activation_code, generation_date, expiration_date)
                    remaining_days = (expiration_date - datetime.now()).days
                    messagebox.showinfo("成功", f"软件已成功激活，有效期至 {expiration_date.strftime('%Y-%m-%d')}，剩余 {remaining_days} 天。")
                    logging.debug("Activation successful")
                    dialog.quit()
                else:
                    messagebox.showerror("错误", "激活码无效或已过期")
                    logging.debug("Activation failed: Invalid or expired code")
            except requests.exceptions.ConnectionError:
                messagebox.showerror("错误", "网络连接失败，请检查网络设置")
            except Exception as e:
                messagebox.showerror("错误", "激活失败，请联系客服支持")

        ttk.Label(main_frame, text="请输入激活码:").pack(anchor=tk.W, pady=(0, 5))
        activation_code_entry = ttk.Entry(main_frame, width=40)
        activation_code_entry.pack(fill=tk.X, pady=(0, 10))

        activate_button = ttk.Button(main_frame, text="激活", command=activate)
        activate_button.pack(fill=tk.X, pady=(0, 10))

        info_label = ttk.Label(main_frame, text="开始激活前，请先购买激活码。", 
                                     wraplength=260, foreground='red')
        info_label.pack(fill=tk.X, pady=(5, 0), side=tk.BOTTOM)

        def open_purchase_page():
            try:
                # 使用 PaymentAPI 获取购买链接
                payment_api = PaymentAPI()
                order_data = {'plan': '1个月'}  # 默认使用1个月的计划
                order_result = payment_api.create_order(order_data)
                webbrowser.open(order_result['pay_url'])
            except Exception as e:
                logging.error(f"Error opening purchase page: {e}")
                messagebox.showerror("错误", f"打开购买页面时出错: {str(e)}")

        purchase_button = ttk.Button(main_frame, text="订阅购买", 
                                   command=open_purchase_page)
        purchase_button.pack(fill=tk.X, pady=(0, 0))

        dialog.update_idletasks()
        dialog.geometry("+{}+{}".format(
            (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2,
            (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        ))

        logging.debug("Activation dialog created, entering mainloop")
        dialog.grab_set()
        dialog.mainloop()
        logging.debug("Activation dialog mainloop ended")

    except Exception as e:
        logging.error(f"Error creating activation dialog: {e}")
        messagebox.showerror("错误", f"创建激活窗口时出错: {str(e)}")
        sys.exit(1)

    # 如果对话框被关闭而不是通过激活按钮退出，则退出程序
    if not check_license():
        sys.exit()

def print_startup_info():

    print("\n")
    print("软件已激活，开始你的表演吧！")

def main():
    logging.debug("Starting main function")
    initialize_license_system()
    if check_license():
        logging.debug("License check passed")
        print_startup_info()
        try:
            # 检查更新
            try:
                if version_checker.check_for_updates():
                    version_checker.show_update_dialog()
            except Exception as e:
                logging.error(f"Update check failed: {e}")
            
            # 直接调用 Coordinator.run()，不传递参数
            Coordinator.run()
            
        except tk.TclError as e:
            logging.error(f"Tkinter error: {e}")
            if "pyimage" in str(e):
                print("图像资源加载失败，请检查程序完整性")
            raise
        except Exception as e:
            logging.error(f"Error running Coordinator: {e}")
            raise
    else:
        logging.debug("License check failed, showing activation dialog")
        root = tk.Tk()
        root.withdraw()
        print("软件未激活或许可证无效。")
        show_activation_dialog(root)
        # 如果到达这里，说明激活成功或用户关闭了窗口
        if check_license():
            logging.debug("License check passed after activation")
            print("激活成功。正在启动主程序。")
            try:
                # 确保清理所有旧的 Tkinter 窗口和资源
                root.destroy()
                # 直接调用 Coordinator.run()，不传递参数
                Coordinator.run()
            except Exception as e:
                logging.error(f"Error running Coordinator: {e}")
                raise
        else:
            logging.debug("Activation failed or window was closed")
            print("激活失败或窗口被关闭，程序将退出。")
            sys.exit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Unhandled exception in main: {e}")
        # 确保所有 Tkinter 窗口都被正确清理
        try:
            for widget in tk.Tk().winfo_children():
                widget.destroy()
        except:
            pass
        
        # 运行目录下的启动.bat
        current_dir = os.path.dirname(os.path.abspath(__file__))
        bat_path = os.path.join(current_dir, "启动.bat")
        os.system(bat_path)
        sys.exit(1)
