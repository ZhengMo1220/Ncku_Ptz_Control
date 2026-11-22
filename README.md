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
- [Git](https://git-scm.com/download/win)
- [Miniconda / Anaconda](https://docs.conda.io/)
- 電腦需與攝影機在同一個網段（預設 `10.30.3.x`）

> 以下指令請在 **Anaconda Prompt** 或 **命令提示字元（cmd）** 執行。
> 若使用 PowerShell，執行 `.bat` 時前面要加 `.\`（例如 `.\install.bat`）。
> `.bat` 檔也可以直接在檔案總管中雙擊執行。

## 安裝

### 方法 A：使用 install.bat（建議）

```bat
git clone https://github.com/ZhengMo1220/Ncku_Ptz_Control.git
cd Ncku_Ptz_Control
install.bat
```

`install.bat` 會：

1. 建立 conda 環境 `ptz`（Python 3.9）
2. 安裝 `requirements.txt` 中的套件
3. 由 `config.example.json` 複製出 `config.json`

> 若 conda 顯示 `Terms of Service have not been accepted`（conda 25.5 以後的版本），
> 先執行 `conda tos accept`，再重新執行 `install.bat`。

### 方法 B：手動安裝

```bat
conda create -n ptz python=3.9 -y
conda activate ptz
pip install -r requirements.txt
copy config.example.json config.json
```

## 設定攝影機帳號密碼（必要）

帳號密碼**不放在程式碼與 git 中**。請用記事本開啟 `config.json`，把 `YOUR_CAMERA_USERNAME` / `YOUR_CAMERA_PASSWORD` 改成攝影機實際的帳號密碼：

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

尚未填寫就啟動時，程式會跳出「設定檔尚未填寫」提示。

## 執行

```bat
start.bat
```

1. 在下拉選單選擇攝影機，按「讀取串流」
2. 選到 `Ptz` 攝影機時，方向與縮放按鈕會啟用，可控制攝影機
3. 再按一次「停止串流」結束

## 打包成執行檔（選用）

```bat
conda activate ptz
pip install pyinstaller
packing.bat
```

產生的 `dist\Ptz_Control.exe`（約 95 MB）可帶到現場電腦直接執行，不需安裝 Python。
**需將 `config.json` 複製到 exe 同一個資料夾**，否則會顯示「缺少設定檔」。

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
| 啟動時顯示「缺少設定檔」 | 複製 `config.example.json` 為 `config.json` 並填入帳號密碼（exe 版要放在 exe 旁邊） |
| 啟動時顯示「設定檔尚未填寫」 | `config.json` 仍是範本內容，請填入攝影機實際帳號密碼 |
| PowerShell 顯示 `install.bat` 無法辨識 | 改用 `.\install.bat`，或在 cmd / Anaconda Prompt 執行 |
| conda 顯示 `Terms of Service have not been accepted` | 執行 `conda tos accept` 後重試 |
| 「無法開啟攝影機串流」 | 確認電腦與攝影機在同一網段、IP 與帳號密碼正確 |
| 「PTZ 控制連線失敗」 | 該攝影機未開啟 ONVIF 或離線；串流仍可觀看，只是不能控制 |
