# 數獨辨識解題器 Sudoku Recognition Solver

基於YOLO的數獨辨識系統，結合YOLO的（OCR）辨識與數獨求解算法，實現自動截圖辨識並填入解答。

## 🌟 特色功能

- 🖼️ 支援螢幕截圖或本地圖片輸入
- ⌨️ 可自訂快捷鍵與截圖區域
- 🚀 自動填入答案，速度可調
- 🎯 支援GPU加速推理
- 💾 自動保存使用者設定

## 🔧 環境需求

### 基本配置
- Python 3.8+
- CUDA
- Roboflow API金鑰

### 安裝步驟

1. 下載專案
```bash
git clone https://github.com/yourusername/sudoku-solver.git
cd sudoku-solver
```

2. 安裝依賴
```bash
# CPU版本
pip install -r requirements.txt

# GPU版本
CUDA Toolkit https://developer.nvidia.com/cuda-toolkit-archive
cuDNN https://developer.nvidia.com/rdp/cudnn-archive
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
或到 https://pytorch.org/ 下載對應版本
pip install -r requirements.txt
```

3. 配置Roboflow API
如果想加入更多數字圖片增強辨視泛化能力，推薦可使用這個線上模型
```python
# 在prediction.py中替換API金鑰
api_key = "YOUR_API_KEY_HERE"
```

## 📖 使用說明

### 快速開始

1. 執行主程式：
```bash
python main.py
```

2. 設定截圖區域：
   - 點擊「框選題目區域」按鈕
   - 使用滑鼠拖曳選擇數獨區域
   - 或直接輸入座標值

3. 配置快捷鍵：
   - 展開「熱鍵設定」
   - 選擇所需組合鍵
   - 點擊「啟動熱鍵」

4. 使用程式：
   - 按下設定的快捷鍵進行截圖
      預設快捷鍵為「‵」，請依照個人喜好修改設定
   - 等待辨識完成
   - 程式會自動填入答案
      如取消自動填入答案，可當截圖工具使用

### 進階設定

- 調整填入速度：
  - 展開「進階設定」
  - 使用滑塊調整速度（1-10）

- 匯入本地圖片：
  - 使用「檔案」選單
  - 選擇「開啟圖片」

## 🔄 訓練自己的模型

1. 準備數據集：
```bash
python split_dataset.py
```

2. 設定訓練參數（training.py）：
```python
model.train(
    data='./datasets/data.yaml',
    epochs=1000,
    batch=4,
    imgsz=480,
    device="0"  # GPU編號，使用CPU則設為"cpu"
)
```

3. 開始訓練：
```bash
python training.py
```

## 📁 專案結構

```
.
├── main.py           # 主程式與GUI介面
├── prediction.py     # 數字辨識模組
├── split_dataset.py  # 數據集分割工具
├── training.py       # 模型訓練腳本
├── sudoku.pt        # 預訓練模型
├── settings.json    # 使用者設定檔
└── datasets/        # 數據集目錄
    ├── data.yaml    # 數據集配置
    ├── train/       # 訓練數據
    └── valid/       # 驗證數據
```

## ⚙️ 系統要求

- 作業系統：Windows 10+
- 顯示器：支援1080p及以上解析度
- GPU：NVIDIA顯卡（可選，支援CUDA）

## 📝 技術文件

詳細的技術實現與開發文件請參考 [docs/README.md](docs/README.md)

## ⚖️ 授權協議

本專案採用 [MIT License](LICENSE) 授權

## 🤝 參與貢獻

1. Fork本專案
2. 建立您的特性分支 (git checkout -b feature/AmazingFeature)
3. 提交您的更改 (git commit -m 'Add some AmazingFeature')
4. 推送到分支 (git push origin feature/AmazingFeature)
5. 開啟一個Pull Request