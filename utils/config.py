"""讀取攝影機設定檔 (config.json)。

帳號密碼不寫在程式碼中，而是放在與 main.py（或打包後的 .exe）同一層的 config.json。
第一次使用請複製 config.example.json 為 config.json 並填入實際帳號密碼。
"""
import json
import os
import sys

CONFIG_FILENAME = "config.json"


def app_dir():
    """程式所在資料夾：開發時為 main.py 所在處，打包後為 .exe 所在處。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config():
    path = os.path.join(app_dir(), CONFIG_FILENAME)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"找不到設定檔：{path}\n請複製 config.example.json 為 config.json 並填入攝影機帳號密碼。"
        )
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    cfg.setdefault("rtsp_port", 554)
    cfg.setdefault("rtsp_path", "stream0")
    cfg.setdefault("onvif_port", 80)
    cfg.setdefault("ip_prefix", "10.30.3.")
    cfg.setdefault("no_control_cameras", ["Ptz01", "Ptz02"])
    return cfg


def rtsp_url(cfg, camera_ip):
    return (f"rtsp://{cfg['username']}:{cfg['password']}@{camera_ip}:"
            f"{cfg['rtsp_port']}/{cfg['rtsp_path']}")
