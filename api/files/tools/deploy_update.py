import os
from update_manager import UpdateManager
import shutil
from pathlib import Path
import json

class CloudflareDeployer:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.pages_dir = self.base_dir / 'pages'  # Cloudflare Pages 目录
        self.api_dir = self.pages_dir / 'api'
        self.files_dir = self.pages_dir / 'files'
        
    def setup_directories(self):
        """创建必要的目录结构"""
        self.pages_dir.mkdir(exist_ok=True)
        self.api_dir.mkdir(exist_ok=True)
        self.files_dir.mkdir(exist_ok=True)
        
        # 创建 _redirects 文件用于路由
        redirects = """
/version    /api/version.json   200
/files/*    /files/:splat      200
        """
        with open(self.pages_dir / '_redirects', 'w') as f:
            f.write(redirects.strip())
            
    def deploy_update(self, version, changelog):
        """部署更新"""
        # 生成更新信息
        manager = UpdateManager()
        update_info = manager.generate_update_info(version, changelog)
        
        # 保存版本信息
        with open(self.api_dir / 'version.json', 'w', encoding='utf-8') as f:
            json.dump(update_info, f, indent=2, ensure_ascii=False)
            
        # 复制更新文件
        for file_info in update_info['files']:
            src_path = self.base_dir / file_info['path']
            dst_path = self.files_dir / file_info['path']
            
            if src_path.exists():
                # 创建目标目录
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                # 复制文件
                shutil.copy2(src_path, dst_path)
                print(f"文件已复制: {file_info['path']}")
            
        print("更新文件准备完成，请手动提交到 GitHub 仓库")
        
def main():
    deployer = CloudflareDeployer()
    
    # 设置版本信息
    changelog = """
    - 修复了xxx bug
    - 新增xxx功能
    - 优化了xxx性能
    """
    
    # 创建目录结构
    deployer.setup_directories()
    
    # 部署更新
    deployer.deploy_update("1.0.1", changelog)
    
    print("\n部署步骤：")
    print("1. 所有文件已准备好在 'pages' 目录中")
    print("2. 将 'pages' 目录提交到你的 GitHub 仓库")
    print("3. Cloudflare Pages 会自动部署更新")

if __name__ == "__main__":
    main() 