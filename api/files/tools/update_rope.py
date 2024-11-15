import subprocess
import sys
import os

def update_repository():
    try:
        # 获取脚本所在目录的上级目录（项目根目录）
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(root_dir)
        
        # 从环境变量获取 token
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            print("错误：未设置 GITHUB_TOKEN 环境变量")
            return False
        
        # 设置 Git 配置
        subprocess.run(['git', 'config', '--global', '--unset', 'credential.helper'], 
                      capture_output=True, encoding='utf-8', errors='ignore')
        subprocess.run(['git', 'config', '--system', '--unset', 'credential.helper'], 
                      capture_output=True, encoding='utf-8', errors='ignore')
        subprocess.run(['git', 'config', '--local', '--unset', 'credential.helper'], 
                      capture_output=True, encoding='utf-8', errors='ignore')
        
        # 使用环境变量中的 token 设置远程仓库 URL
        remote_url = f"https://x-access-token:{github_token}@github.com/hthappy/AI-Live.git"
        subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url], 
                      capture_output=True, encoding='utf-8', errors='ignore')
        
        # 获取更新
        fetch_result = subprocess.run(['git', 'fetch', '--quiet'], 
                                    capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if fetch_result.returncode != 0:
            print(f"获取更新失败: {fetch_result.stderr}")
            return False
        
        # 检查是否有更新    
        result = subprocess.run(['git', 'rev-list', 'HEAD...origin/main', '--count'], 
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode != 0:
            print(f"检查更新失败: {result.stderr}")
            return False
            
        update_count = int(result.stdout.strip())
        
        # 无论是否有更新，都强制与远程保持一致
        if update_count > 0:
            print("程序正在更新，请稍候...")
        
        reset_result = subprocess.run(['git', 'reset', '--hard', 'origin/main'], 
                                    capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if reset_result.returncode != 0:
            print(f"更新失败: {reset_result.stderr}")
            return False
            
        clean_result = subprocess.run(['git', 'clean', '-fd'], 
                                    capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if clean_result.returncode != 0:
            print(f"清理失败: {clean_result.stderr}")
            return False
            
        if update_count > 0:
            print("更新完成！详情日志：https://ailive.ai-yy.com/help/readme/geng-xin-ri-zhi")
            return True
            
        return False
        
    except Exception as e:
        print(f"更新过程中出现错误: {str(e)}")
        return False

if __name__ == "__main__":
    update_repository()
