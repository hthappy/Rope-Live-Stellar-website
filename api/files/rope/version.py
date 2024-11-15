import os
import json
import logging
import requests
import sys
from pathlib import Path
import webbrowser
import hashlib
import shutil
from tkinter import messagebox, ttk
import tkinter as tk
import threading
from datetime import datetime

VERSION_FILE = Path(__file__).parent / 'version.json'

def get_version():
    """获取当前版本号"""
    try:
        if VERSION_FILE.exists():
            with open(VERSION_FILE, 'r') as f:
                version_info = json.load(f)
                return version_info['version']
    except Exception as e:
        logging.error(f"Error reading version: {e}")
    return "1.0.0"  # 默认版本号

def update_version(new_version):
    """更新版本号"""
    try:
        version_info = {'version': new_version}
        with open(VERSION_FILE, 'w') as f:
            json.dump(version_info, f)
        return True
    except Exception as e:
        logging.error(f"Error updating version: {e}")
        return False

# 当前版本号
VERSION = get_version()

UPDATE_URL = "https://api.livefacex.com/version"  # 版本检查API
DOWNLOAD_URL = "https://api.livefacex.com/files"  # 文件下载基础URL

class VersionChecker:
    def __init__(self):
        self.current_version = VERSION
        self.latest_version = None
        self.update_info = None
        self.base_dir = Path(__file__).resolve().parent.parent
        self.temp_dir = self.base_dir / 'temp'
        
    def get_file_hash(self, file_path):
        """计算文件的 MD5 哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
        
    def check_for_updates(self):
        """检查更新"""
        try:
            response = requests.get(UPDATE_URL, timeout=5)
            if not response.ok:
                return False
                
            update_info = response.json()
            self.latest_version = update_info['version']
            self.update_info = update_info
            
            # 检查是否有需要更新的文件
            if 'files' in update_info:
                for file_info in update_info['files']:
                    local_path = self.base_dir / file_info['path']
                    if not local_path.exists():
                        return True
                    local_hash = self.get_file_hash(local_path)
                    if local_hash != file_info['hash']:
                        return True
            
            return self._compare_versions(self.current_version, self.latest_version)
            
        except Exception as e:
            logging.error(f"Check update error: {e}")
            return False
            
    def _compare_versions(self, current, latest):
        """比较版本号"""
        current_parts = [int(x) for x in current.split('.')]
        latest_parts = [int(x) for x in latest.split('.')]
        
        for i in range(max(len(current_parts), len(latest_parts))):
            current_part = current_parts[i] if i < len(current_parts) else 0
            latest_part = latest_parts[i] if i < len(latest_parts) else 0
            
            if latest_part > current_part:
                return True
            elif latest_part < current_part:
                return False
                
        return False

    def download_file(self, url, local_path, progress_callback=None):
        """下载文件并显示进度"""
        try:
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            downloaded = 0
            
            with open(local_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    downloaded += len(data)
                    f.write(data)
                    if progress_callback:
                        progress = (downloaded / total_size) * 100
                        progress_callback(progress)
                        
            return True
        except Exception as e:
            logging.error(f"Download error: {e}")
            return False

    def show_update_dialog(self):
        """显示更新提示对话框"""
        if not self.update_info:
            return
            
        message = f"""发现新版本 {self.latest_version}
        
当前版本：{self.current_version}
更新内容：
{self.update_info.get('changelog', '- 优化和bug修复')}

需要更新的文件：
{self._get_update_files_info()}

是否立即更新？"""

        if messagebox.askyesno("软件更新", message):
            self.start_update()
            
    def _get_update_files_info(self):
        """获取需要更新的文件信息"""
        if 'files' not in self.update_info:
            return "- 完整程序包"
            
        files_info = []
        for file_info in self.update_info['files']:
            local_path = self.base_dir / file_info['path']
            if not local_path.exists() or self.get_file_hash(local_path) != file_info['hash']:
                files_info.append(f"- {file_info['path']} ({file_info['size']/1024/1024:.1f}MB)")
        return "\n".join(files_info)

    def start_update(self):
        """开始更新过程"""
        try:
            # 创建临时目录
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建更新进度窗口
            update_window = tk.Toplevel()
            update_window.title("正在更新")
            update_window.geometry("300x150")
            
            # 进度条
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(
                update_window, 
                variable=progress_var,
                maximum=100
            )
            progress_bar.pack(pady=20, padx=10, fill=tk.X)
            
            # 状态标签
            status_label = ttk.Label(update_window, text="准备更新...")
            status_label.pack(pady=10)
            
            def update_progress(progress, filename=""):
                progress_var.set(progress)
                status_label.config(text=f"正在更新: {filename} ({progress:.1f}%)")
                update_window.update()

            def perform_update():
                try:
                    old_version = VERSION
                    
                    files_to_update = self.update_info.get('files', [])
                    total_files = len(files_to_update)
                    
                    for i, file_info in enumerate(files_to_update):
                        file_path = file_info['path']
                        file_url = f"{DOWNLOAD_URL}/files/{file_path}"
                        temp_path = self.temp_dir / file_path
                        
                        # 创建临时文件目录
                        temp_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # 下载文件
                        success = self.download_file(
                            file_url, 
                            temp_path,
                            lambda p: update_progress(p, file_path)
                        )
                        
                        if not success:
                            raise Exception(f"Failed to download {file_path}")
                            
                        # 验证文件哈希
                        if self.get_file_hash(temp_path) != file_info['hash']:
                            raise Exception(f"Hash mismatch for {file_path}")
                            
                        # 替换旧文件
                        target_path = self.base_dir / file_path
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(temp_path), str(target_path))
                        
                        update_progress((i + 1) / total_files * 100)
                    
                    # 更新版本号
                    if update_version(self.latest_version):
                        # 记录版本历史
                        log_version_history(old_version, self.latest_version)
                    
                    messagebox.showinfo("更新完成", 
                        f"软件已更新到版本 {self.latest_version}，请重启程序。")
                    sys.exit(0)
                    
                except Exception as e:
                    logging.error(f"Update error: {e}")
                    messagebox.showerror("更新失败", 
                        "更新过程中出现错误，请稍后重试或访问官网手动更新。")
                finally:
                    # 清时文件
                    shutil.rmtree(str(self.temp_dir), ignore_errors=True)
                    update_window.destroy()

            # 在新线程中执行更新
            threading.Thread(target=perform_update, daemon=True).start()
            
        except Exception as e:
            logging.error(f"Update error: {e}")
            messagebox.showerror("更新失败", 
                "启动更新失败，请稍后重试或访问官网手动新。")

    def verify_update(self, file_info):
        """验证更新包的安全性"""
        try:
            # 验证签名
            signature = file_info.get('signature')
            if not self.verify_signature(signature):
                return False
            
            # 验证证书
            cert = file_info.get('certificate')
            if not self.verify_certificate(cert):
                return False
            
            return True
        except Exception as e:
            logging.error(f"Update verification failed: {e}")
            return False

    def download_patch(self, current_version, target_version):
        """下载增量更新包"""
        patch_url = f"{DOWNLOAD_URL}/patches/{current_version}-{target_version}.patch"
        # ... 下载和应用补丁的逻辑

    def backup_files(self):
        """备份当前文件"""
        backup_dir = self.base_dir / 'backup'
        # ... 备份逻辑

    def rollback(self):
        """回滚到上一版本"""
        # ... 回滚逻辑

def log_version_history(old_version, new_version):
    """记录版本更新历史"""
    try:
        history_file = Path(__file__).parent / 'version_history.json'
        history = []
        
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
                
        history.append({
            'date': datetime.now().isoformat(),
            'old_version': old_version,
            'new_version': new_version
        })
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
            
    except Exception as e:
        logging.error(f"Error logging version history: {e}")

# 创建全局实例
version_checker = VersionChecker() 