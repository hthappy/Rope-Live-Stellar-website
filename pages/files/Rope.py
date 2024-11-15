#!/usr/bin/env python3

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import atexit
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from rope import Coordinator
from rope.license_utils import validate_activation_code, save_license_info, get_machine_code, check_license
from datetime import datetime
import os
from pathlib import Path
import logging

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
        dialog.geometry("300x240")
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
            except Exception as e:
                logging.error(f"Error during activation: {e}")
                messagebox.showerror("错误", f"激活过程中出现错误: {str(e)}")

        ttk.Label(main_frame, text="激活码:").pack(anchor=tk.W, pady=(0, 5))
        activation_code_entry = ttk.Entry(main_frame, width=40)
        activation_code_entry.pack(fill=tk.X, pady=(0, 10))

        activate_button = ttk.Button(main_frame, text="激活", command=activate)
        activate_button.pack(fill=tk.X, pady=(0, 10))

        machine_code_label = ttk.Label(main_frame, text="开始激活前，请获取您的机器码。", 
                                     wraplength=260, foreground='red')
        machine_code_label.pack(fill=tk.X, pady=(5, 0), side=tk.BOTTOM)

        def display_machine_code():
            try:
                machine_code = get_machine_code()
                dialog.clipboard_clear()
                dialog.clipboard_append(machine_code)
                machine_code_label.config(text=f"您的机器码已复制，请发送给软件作者。\n {machine_code}")
            except Exception as e:
                logging.error(f"Error displaying machine code: {e}")
                messagebox.showerror("错误", f"获取机器码时出错: {str(e)}")

        get_machine_code_button = ttk.Button(main_frame, text="获取机器码", 
                                           command=display_machine_code)
        get_machine_code_button.pack(fill=tk.X, pady=(0, 0))

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
