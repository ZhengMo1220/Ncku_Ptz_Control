# NCKU PTZ Control

以 PyQt5 撰寫的攝影機串流檢視與 PTZ（Pan / Tilt / Zoom）控制工具，透過 RTSP 讀取影像、透過 ONVIF 控制 PTZ 攝影機。

## 功能

- 從下拉選單選擇攝影機並讀取 RTSP 串流；串流中可直接切換攝影機
- 攝影機分為三類：
  - `Rot01`–`Rot20`：Rotation Replay 用攝影機（`10.30.3.1`–`20`）
  - `Sti01`–`Sti06`：Stitching 用攝影機（`10.30.3.21`–`26`）
  - `Ptz01`–`Ptz08`：PTZ 攝影機（`10.30.3.27`–`34`），可上下左右移動與縮放
- `Ptz01`、`Ptz02` 預設不可控制，可在 `config.json` 的 `no_control_cameras` 修改

## 環境需求

- Windows 10 / 11
- [Miniconda / Anaconda](https://docs.conda.io/)
- 電腦需與攝影機在同一個網段（預設 `10.30.3.x`）

## 安裝

```bash
git clone https://github.com/ZhengMo1220/Ncku_Ptz_Control.git
cd Ncku_Ptz_Control
install.bat
```

`install.bat` 會建立 conda 環境 `ptz`（Python 3.9）、安裝 `requirements.txt`，並由 `config.example.json` 複製出 `config.json`。

手動安裝：

```bash
conda create -n ptz python=3.9 -y
conda activate ptz
pip install -r requirements.txt
copy config.example.json config.json
```

## 設定攝影機帳號密碼

帳號密碼**不放在程式碼與 git 中**，請編輯 `config.json`：

```json
{
    "username": "攝影機帳號",
    "password": "攝影機密碼",
    "ip_prefix": "10.30.3.",
    "rtsp_port": 554,
    "rtsp_path": "stream0",
    "onvif_port": 80,
    "no_control_cameras": ["Ptz01", "Ptz02"]
}
```

## 執行

```bash
start.bat
```

1. 在下拉選單選擇攝影機，按「讀取串流」
2. 選到 `Ptz` 攝影機時，方向與縮放按鈕會啟用，可控制攝影機
3. 再按一次「停止串流」結束

## 打包成執行檔（選用）

```bash
conda activate ptz
pip install pyinstaller
packing.bat
```

產生的 `dist/Ptz_Control.exe` 可帶到現場電腦直接執行，**需將 `config.json` 放在 exe 同一個資料夾**。

## 修改介面

用 Qt Designer 編輯 `main_window.ui` / `ptz_control/ptz_control.ui` 後，執行 `compile.bat` 重新產生 `*_ui.py`。

## 專案結構

```
├── main.py                       # 程式進入點
├── main_window.ui / main_window_ui.py
├── ptz_control/
│   ├── camera_tab_control.py     # 攝影機分頁邏輯（串流、按鈕）
│   ├── ptz_control.py            # ONVIF PTZ 控制
│   └── ptz_control.ui / ptz_control_ui.py
├── utils/
│   ├── config.py                 # 讀取 config.json
│   ├── stream_thread.py          # RTSP 串流執行緒
│   ├── ui_utils.py / icons_utils.py
├── icons/
├── config.example.json           # 設定檔範本
├── install.bat / start.bat / packing.bat / compile.bat
└── requirements.txt
```

## 常見問題

| 問題 | 解法 |
|---|---|
| `start.bat` 顯示找不到 `ptz` 環境 / `No module named 'onvif'` | 執行 `install.bat` |
| 啟動時顯示「缺少設定檔」 | 複製 `config.example.json` 為 `config.json` 並填入帳號密碼 |
| 「無法開啟攝影機串流」 | 確認電腦與攝影機在同一網段、IP 與帳號密碼正確 |
| 「PTZ 控制連線失敗」 | 該攝影機未開啟 ONVIF 或離線；串流仍可觀看，只是不能控制 |
