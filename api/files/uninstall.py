import winreg
import shutil
import os

def clean_registry():
    # 清理注册表
    try:
        # 删除注册表项
        registry_path = r"SOFTWARE\LiveFaceX"
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, registry_path)
        print("注册表清理完成")
    except WindowsError as e:
        print(f"清理注册表时出错: {e}")

def clean_files():
    # 清理文件
    try:
        # 定义需要删除的文件和文件夹路径
        app_data_path = os.path.join(os.getenv('APPDATA'), 'LiveFaceX')
        program_files_path = os.path.join(os.getenv('PROGRAMFILES'), 'LiveFaceX')
        tools_path = os.path.join(program_files_path, 'tools')
        
        # 删除文件夹及其内容
        paths_to_clean = [app_data_path, program_files_path, tools_path]
        for path in paths_to_clean:
            if os.path.exists(path):
                shutil.rmtree(path)
                
        print("文件清理完成")
    except Exception as e:
        print(f"清理文件时出错: {e}")

def deactivate_license():
    """取消激活许可证"""
    try:
        # 读取许可证文件获取激活码
        license_file = os.path.join(os.getenv('PROGRAMFILES'), 'LiveFaceX', 'tools', 'license.enc')
        if os.path.exists(license_file):
            # 这里需要添加取消激活的API调用
            print("许可证已取消激活")
    except Exception as e:
        print(f"取消激活许可证时出错: {e}")

def main():
    print("开始卸载程序...")
    choice = input("是否要取消激活许可证？这将允许您在其他设备上使用。(y/n): ")
    if choice.lower() == 'y':
        deactivate_license()
    clean_registry()
    clean_files()
    print("卸载完成")

if __name__ == "__main__":
    main()