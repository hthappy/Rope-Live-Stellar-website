import os
import json
import hashlib
from pathlib import Path
import shutil
from datetime import datetime
import argparse
import fnmatch

class UpdateManager:
    def __init__(self, output_dir=None):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.api_dir = Path(output_dir) / 'api' if output_dir else self.base_dir / 'api'
        self.api_dir.mkdir(parents=True, exist_ok=True)
        
        # 需要扫描的目录
        self.scan_dirs = [
            "rope",     # 主程序目录
            "tools",    # 工具目录
        ]
        
        # 需要包含的根目录文件
        self.root_files = [
            "Rope.py",
            "uninstall.py",
        ]
        
        # 排除的文件和目录模式
        self.exclude_patterns = [
            "*.pyc",           # Python 编译文件
            "__pycache__",     # Python 缓存目录
            "*.log",           # 日志文件
            "temp/*",          # 临时文件
            "*.bak",           # 备份文件
            "models/*",        # 模型文件夹
            "dfl_models/*",    # DFL模型文件夹
            "*.enc",           # 加密文件
            "*.json",          # JSON配置文件
            "*.pth",           # 模型权重文件
            "*.onnx",          # ONNX模型文件
            ".last_update",    # 上次更新时间
            "deploy_update.py" # 部署更新脚本
        ]
    
    def calculate_file_hash(self, file_path):
        """计算文件的MD5哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def scan_files(self):
        """扫描所有需要检查的文件"""
        files_to_check = []
        
        # 扫描指定目录
        for dir_name in self.scan_dirs:
            dir_path = self.base_dir / dir_name
            if dir_path.exists():
                for root, dirs, files in os.walk(dir_path):
                    # 过滤掉不需要的目录
                    dirs[:] = [d for d in dirs if not any(
                        fnmatch.fnmatch(d, pattern) for pattern in self.exclude_patterns
                    )]
                    
                    # 过滤并添加文件
                    for file in files:
                        if not any(fnmatch.fnmatch(file, pattern) 
                                 for pattern in self.exclude_patterns):
                            full_path = Path(root) / file
                            rel_path = full_path.relative_to(self.base_dir)
                            files_to_check.append(str(rel_path))
        
        # 添加根目录文件
        for file in self.root_files:
            if (self.base_dir / file).exists():
                files_to_check.append(file)
        
        return sorted(files_to_check)  # 排序以保持一致性
    
    def generate_update_info(self, version, changelog):
        """生成更新信息"""
        update_info = {
            "version": version,
            "changelog": changelog,
            "release_date": datetime.now().isoformat(),
            "files": []
        }
        
        # 读取上一版本的文件哈希
        last_version_file = self.api_dir / "last_version.json"
        last_hashes = {}
        if last_version_file.exists():
            with open(last_version_file, encoding='utf-8') as f:
                last_info = json.load(f)
                for file_info in last_info.get('files', []):
                    last_hashes[file_info['path']] = file_info['hash']
        
        # 扫描所有文件
        files_to_check = self.scan_files()
        print(f"\n找到 {len(files_to_check)} 个文件需要检查:")
        
        # 只添加发生变化的文件
        for file_path in files_to_check:
            full_path = self.base_dir / file_path
            if full_path.exists():
                current_hash = self.calculate_file_hash(full_path)
                
                # 如果文件哈希值发生变化，或者是新文件
                if file_path not in last_hashes or last_hashes[file_path] != current_hash:
                    file_info = {
                        "path": file_path,
                        "hash": current_hash,
                        "size": os.path.getsize(full_path)
                    }
                    update_info["files"].append(file_info)
                    
                    # 复制文件到更新目录
                    update_file_dir = self.api_dir / "files" / os.path.dirname(file_path)
                    update_file_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(full_path, update_file_dir / os.path.basename(file_path))
                    print(f"添加更新文件: {file_path} ({file_info['size']/1024:.1f}KB)")
        
        # 保存当前版本信息
        with open(last_version_file, "w", encoding='utf-8') as f:
            json.dump(update_info, f, indent=2, ensure_ascii=False)
            
        return update_info
    
    def create_api_endpoints(self):
        """创建API端点文件"""
        # 创建 index.html 作为API文档
        api_doc = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>LiveFaceX Update API</title>
        </head>
        <body>
            <h1>LiveFaceX Update API</h1>
            <h2>Endpoints:</h2>
            <ul>
                <li>GET /api/version - 获取最新版本信息</li>
                <li>GET /api/files/{'{file_path}'} - 下载更新文件</li>
            </ul>
        </body>
        </html>
        """
        
        with open(self.api_dir / "index.html", "w", encoding='utf-8') as f:
            f.write(api_doc)

def main():
    parser = argparse.ArgumentParser(description='Generate update files')
    parser.add_argument('--output', '-o', 
                       default=r"D:\ai\livefacex-updates",
                       help='Output directory for update files')
    parser.add_argument('--version', '-v',
                       default="1.0.1",
                       help='Version number')
    args = parser.parse_args()
    
    manager = UpdateManager(args.output)
    
    changelog = """
    - 修复了xxx bug
    - 新增xxx功能
    - 优化了xxx性能
    """
    
    update_info = manager.generate_update_info(
        version=args.version,
        changelog=changelog
    )
    
    # 创建API文档
    manager.create_api_endpoints()
    
    print("Update API generated successfully!")
    print(f"Files generated in: {args.output}")
    print(f"Version info: {json.dumps(update_info, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    main() 