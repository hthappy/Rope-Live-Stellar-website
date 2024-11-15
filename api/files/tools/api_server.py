from flask import Flask, send_from_directory, jsonify
from pathlib import Path

app = Flask(__name__)

# API根目录
API_DIR = Path(__file__).resolve().parent.parent / 'api'

@app.route('/api/version')
def get_version():
    """获取版本信息"""
    try:
        with open(API_DIR / 'version.json') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/files/<path:file_path>')
def download_file(file_path):
    """下载更新文件"""
    try:
        return send_from_directory(API_DIR / 'files', file_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 