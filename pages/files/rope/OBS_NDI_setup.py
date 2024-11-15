import os
import subprocess
import psutil
import socket
import json
import time
from pathlib import Path
from obswebsocket import obsws, requests
from tkinter import messagebox

# 获取计算机名
computer_name = socket.gethostname()

# 配置文件路径
obs_config_path = os.path.expandvars(r"%AppData%\obs-studio\global.ini")
ndi_webcam_config_path = os.path.expandvars(r"%LOCALAPPDATA%\NDI\Application.Network.WebCam.v1.json")

def find_obs_path_from_process():
    try:
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            if proc.info['name'] == 'obs64.exe':
                obs_path = proc.info['exe']
                if obs_path:
                    proc.kill()
                    proc.wait()
                    return obs_path
    except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
        print(f"错误：无法访问 OBS 进程信息 - {e}")
    return None

def find_obs_path():
    # 首先尝试从进程获取路径
    obs_path = find_obs_path_from_process()
    if obs_path:
        return obs_path

    # 尝试从注册表获取路径（静默执行）
    try:
        import winreg
        for key_path in [r"SOFTWARE\OBS Studio", r"SOFTWARE\WOW6432Node\OBS Studio"]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    install_path, _ = winreg.QueryValueEx(key, "Default")
                    obs_path = os.path.join(install_path, "bin", "64bit", "obs64.exe")
                    if Path(obs_path).is_file():
                        return obs_path
            except FileNotFoundError:
                pass
    except Exception:
        pass

    # 常见路径查找
    common_paths = [
        r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
        r"C:\Program Files (x86)\obs-studio\bin\64bit\obs64.exe",
        r"D:\Program Files\obs-studio\bin\64bit\obs64.exe"
    ]
    
    for path in common_paths:
        if Path(path).is_file():
            return path

    print("错误：未找到 OBS 安装路径")
    return None

def update_obs_config():
    """
    更新 OBS 配置文件，强制启用 NDI 输出
    """
    try:
        # 读取现有配置
        if not os.path.exists(obs_config_path):
            print("错误：OBS 配置文件不存在")
            return False

        with open(obs_config_path, 'r', encoding='utf-8-sig') as file:
            lines = file.readlines()

        # 标记是否找到并更新了配置
        found_ndi_section = False
        found_main_output_enabled = False
        found_main_output_name = False
        
        # 更新配置
        for i, line in enumerate(lines):
            # 找到 NDIPlugin 部分
            if line.strip() == '[NDIPlugin]':
                found_ndi_section = True
                continue
            
            # 如果在 NDIPlugin 部分，更新相关配置
            if found_ndi_section:
                if line.startswith('MainOutputEnabled='):
                    lines[i] = 'MainOutputEnabled=true\n'
                    found_main_output_enabled = True
                elif line.startswith('MainOutputName='):
                    lines[i] = 'MainOutputName=Ai-Live\n'
                    found_main_output_name = True
                # 如果遇到新的section，结束NDIPlugin部分
                elif line.startswith('['):
                    found_ndi_section = False

        # 如果没有找到相关配置，在文件末尾添加
        if not found_ndi_section:
            lines.append('\n[NDIPlugin]\n')
            lines.append('MainOutputEnabled=true\n')
            lines.append('MainOutputName=Ai-Live\n')
        else:
            if not found_main_output_enabled:
                # 在NDIPlugin部分添加配置
                for i, line in enumerate(lines):
                    if line.strip() == '[NDIPlugin]':
                        lines.insert(i + 1, 'MainOutputEnabled=true\n')
                        break
            if not found_main_output_name:
                for i, line in enumerate(lines):
                    if line.strip() == '[NDIPlugin]':
                        lines.insert(i + 1, 'MainOutputName=Ai-Live\n')
                        break

        # 写回配置文件
        with open(obs_config_path, 'w', encoding='utf-8-sig') as file:
            file.writelines(lines)
            
        return True
        
    except Exception as e:
        print(f"错误：更新 OBS 配置失败 - {e}")
        return False

def update_ndi_webcam_config():
    try:
        ndi_webcam_config = {
            "0": {
                "Source": f"{computer_name} (Ai-Live)",
                "AudioGain": 2147483647,
                "AudioChannels": -1,
                "VideoMode": 720,
                "AutoConnect": True,
                "ShowHelp": True
            },
            "1": {"Source": "", "AudioGain": 2147483647, "AudioChannels": -1, "VideoMode": 720, "AutoConnect": True, "ShowHelp": True},
            "2": {"Source": "", "AudioGain": 2147483647, "AudioChannels": -1, "VideoMode": 720, "AutoConnect": True, "ShowHelp": True},
            "3": {"Source": "", "AudioGain": 2147483647, "AudioChannels": -1, "VideoMode": 720, "AutoConnect": True, "ShowHelp": True},
            "SupData": {"SaveState": "interim"}
        }
        
        with open(ndi_webcam_config_path, 'w', encoding='utf-8') as file:
            json.dump(ndi_webcam_config, file, indent=4)
        return True
    except Exception as e:
        print(f"错误：更新 NDI Webcam 配置失败 - {e}")
        return False

def terminate_process(process_name):
    try:
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == process_name:
                psutil.Process(process.info['pid']).terminate()
                return True
        return True
    except Exception as e:
        print(f"错误：终止 {process_name} 进程失败 - {e}")
        return False

def start_application(app_path, is_obs=False):
    if app_path and Path(app_path).is_file():
        try:
            app_dir = os.path.dirname(app_path)
            current_dir = os.getcwd()
            os.chdir(app_dir)
            
            if is_obs:
                subprocess.Popen([
                    app_path,
                    '--safe-mode=false',
                    '--minimize-to-tray',
                    '--disable-shutdown-check',
                    '--disable-preview'
                ])
            else:
                subprocess.Popen(app_path)
                
            os.chdir(current_dir)
            return True
        except Exception as e:
            print(f"错误：启动 {app_path} 失败 - {e}")
            return False
    else:
        print(f"错误：无效的应用程序路径 - {app_path}")
        return False

def OBS_Source_Setup():
    """
    配置 OBS 场景和来源
    """
    try:
        # 读取配置文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, '..', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 连接 OBS WebSocket
        ws = obsws(
            host=config['obs']['host'],
            port=config['obs']['port'],
            password=config['obs']['password']
        )
        
        try:
            ws.connect()
            
            # 添加视频采集设备源
            source_settings = {
                "video_device_id": "OBS Virtual Camera:",
                "device": "OBS Virtual Camera",
                "resolution": "1920x1080",
                "fps": 30,
                "buffering": True,
                "active": True,
                "path": "video=OBS Virtual Camera:",
                "last_video_device_id": "OBS Virtual Camera:"
            }
            
            # 先删除现有源
            try:
                ws.call(requests.DeleteInput(inputName='AiLive换脸'))
            except:
                pass
            
            # 创建新的输入源
            ws.call(requests.CreateInput(
                sceneName='场景',
                inputName='AiLive换脸',
                inputKind='dshow_input',
                inputSettings=source_settings
            ))
            print("\n✨ OBS-NDI 设置完成！")
            return True
            
        except Exception as e:
            print(f"错误：设置 OBS 场景和来源失败 - {e}")
            return False
        
        finally:
            if ws:
                ws.disconnect()
                
    except Exception as e:
        print(f"错误：OBS WebSocket 连接失败 - {e}")
        return False
    
def main():
    print("\n")
    print("开始设置 OBS-NDI 虚拟摄像头，请稍候...")
    success = True
    # 获取 OBS 路径并关闭进程
    obs_path = find_obs_path()
    if not obs_path:
        return

    # 更新配置
    if not update_obs_config():
        success = False

    time.sleep(2)

    # 启动 OBS
    if not start_application(obs_path, is_obs=True):
        success = False

    # 等待 OBS 完全启动
    time.sleep(8)  # 增加等待时间确保 OBS 完全加载和 WebSocket 服务启动

    # 如果 OBS 启动成功，设置场景和来源
    if success:
        if not OBS_Source_Setup():
            success = False

    # 处理 NDI Webcam
    if not terminate_process("Webcam.exe"):
        success = False
        
    if not update_ndi_webcam_config():
        success = False

    # 启动 NDI Webcam
    ndi_webcam_path = r"C:\Program Files\NDI\NDI 6 Tools\Webcam\Webcam.exe"
    if os.path.exists(ndi_webcam_path):
        time.sleep(1)
        if not start_application(ndi_webcam_path):
            success = False
    else:
        print("错误：NDI Webcam 路径无效")
        success = False

    # 最终结果提示
    if success:
        messagebox.showinfo("成功", "OBS-NDI 虚拟摄像头设置完成！")
    else:
        messagebox.showerror("错误", "OBS-NDI 虚拟摄像头设置失败。")
