import pyshark
import threading
import json
import os
import sys
import time

def get_base_dir():
    """获取程序运行时的根目录"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的程序
        return os.path.dirname(sys.executable)
    else:
        # 如果是开发环境
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 使用绝对路径获取配置文件
config_path = os.path.join(get_base_dir(), 'config', 'config.json')

try:
    with open(config_path, 'r', encoding='utf-8') as file:
        json_data = file.read()
        data = json.loads(json_data)
except FileNotFoundError:
    print(f"错误：找不到配置文件 {config_path}")
    data = {"tshark": {"display_filter": "", "interface": ""}}
except json.JSONDecodeError:
    print(f"错误：配置文件格式不正确 {config_path}")
    data = {"tshark": {"display_filter": "", "interface": ""}}

# 获取配置值
display_filter = data.get("tshark", {}).get("display_filter", "")
interface = data.get("tshark", {}).get("interface", "")

# 获取 WIRESHARK_PATH
try:
    tshark_path = os.path.join(os.environ['WIRESHARK_PATH'], 'tshark.exe')
except KeyError:
    tshark_path = ""

class RTMPInfoFound(Exception):
    pass

def get_rtmp_info():
    server = None
    code = None
    event = threading.Event()
    packet_count = 0
    capture = None

    def packet_callback(packet):
        nonlocal server, code, packet_count
        try:
            packet_count += 1
            if packet_count % 100 == 0:
                print(f"已处理 {packet_count} 个数据包...")
            
            packet_str = str(packet)
            if not server:
                server = filter_strings(packet_str, "rtmp://")
            if not code:
                code = filter_strings(packet_str, "stream-")
            if server and code:
                print(f"在第 {packet_count} 个数据包中找到完整的 RTMP 信息")
                print(f"服务器: {server}")
                code = code.replace("'", "")   #推流码清除''单引号
                print(f"推流码: {code}") 
                event.set()
                raise RTMPInfoFound()  # 抛出异常以停止捕获
        except RTMPInfoFound:
            raise
        except Exception as e:
            print(f"处理数据包时出错: {e}")

    def filter_strings(input_str, target_str):
        words = input_str.split()
        for word in words:
            if target_str in word:
                return word
        return None

    try:
        print("请使用直播伴侣开启直播，准备捕获数据包...")
        capture = pyshark.LiveCapture(interface=interface, display_filter=display_filter,
                                      tshark_path=tshark_path)
        capture.apply_on_packets(packet_callback, timeout=60)
    except Exception as e:
        if not (server and code):  # 只有在没有找到完整信息时才打印错误
            print(f"捕获过程中出错: {e}")
    finally:
        if capture:
            capture.close()
    return server, code

if __name__ == "__main__":
    print("启动 RTMP 嗅探器...")
    print(f"使用的网络接口: {interface}")
    print(f"使用的显示过滤器: {display_filter}")
    print(f"使用的 tshark 路径: {tshark_path}")
    
    start_time = time.time()
    server, code = get_rtmp_info()
    end_time = time.time()
    
    print(f"耗时: {end_time - start_time:.2f} 秒")
    
    if server and code:
        print("成功获取 RTMP 信息:")
        print(f"服务器: {server}")
        print(f"推流码: {code}")
    elif server:
        print(f"仅获取到服务器信息: {server}")
        print("未能获取到推流码信息。")
    elif code:
        print(f"仅获取到推流码信息: {code}")
        print("未能获取到服务器信息。")
    else:
        print("未能获取到 RTMP 信息。请确保抖音直播伴侣已打开并尝试开始直播。")
