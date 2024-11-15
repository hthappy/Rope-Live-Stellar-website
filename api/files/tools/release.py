import os
import subprocess
from update_manager import UpdateManager
from pathlib import Path

def release_update(version, changelog):
    """发布新版本"""
    # 1. 生成更新文件
    manager = UpdateManager()
    update_info = manager.generate_update_info(version, changelog)
    
    # 2. 复制文件到 pages 目录
    updates_repo = Path("../livefacex-updates")  # 更新仓库路径
    
    # 3. Git 操作
    os.chdir(updates_repo)
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"Update to version {version}"])
    subprocess.run(["git", "push", "origin", "main"])
    
    print(f"Version {version} released successfully!")

if __name__ == "__main__":
    version = "1.0.1"
    changelog = """
    - 修复了xxx bug
    - 新增xxx功能
    """
    
    release_update(version, changelog) 