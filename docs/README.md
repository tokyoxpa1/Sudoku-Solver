# 程式設計說明文件

## 系統架構

本專案實現了一個基於YOLO的數獨辨識與解題系統，主要包含以下模組：

### 1. 主程式 (main.py)
- GUI界面實現，使用tkinter構建
- 支援熱鍵截圖功能
- 提供自訂截圖區域
- 可調整自動填入速度
- 設定檔案儲存與載入

### 2. 預測模組 (prediction.py)
- 整合Roboflow API進行數字辨識
- 將API結果轉換為YOLO格式
- 支援批次處理圖片

### 3. 數據處理 (split_dataset.py)
- 數據集分割工具
- 自動創建訓練/驗證集目錄結構
- 隨機打亂並按比例分配數據

### 4. 訓練相關 (training.py)
- YOLOv8+模型訓練配置
- 自動下載預訓練模型
- 支援GPU加速訓練

## 代碼結構

```
.
├── main.py               # 主程式與GUI實現
├── prediction.py         # 數字辨識邏輯
├── split_dataset.py      # 數據集處理工具
├── training.py          # 模型訓練腳本
├── sudoku.pt            # 預訓練模型
└── datasets/            # 數據集目錄
    ├── train/           # 訓練數據
    └── valid/           # 驗證數據
```

## 核心功能實現

### 截圖功能
- 使用PIL的ImageGrab實現截圖
- 支援全螢幕與區域截圖
- 可通過熱鍵快速觸發

### 數獨求解
- 使用優化的約束傳播算法
- 實現啟發式搜索提升效率
- 支援自動填入解答

### 設定儲存
- 使用JSON格式保存配置
- 包含座標、熱鍵等信息
- 支援程式重啟後恢復設定

## API串接說明

### Roboflow API
- 需要設定API金鑰
- 使用InferenceHTTPClient進行請求
- 支援批次推理功能

### YOLO模型
- 使用ultralytics套件
- 支援CPU/GPU推理
- 可自動下載預訓練權重

## 注意事項

1. 首次使用需設定Roboflow API金鑰
2. 建議使用GPU加速推理
3. 自動填入速度可依需求調整
4. 支援CSV格式導出辨識結果

## 開發環境

- Python 3.8+
- PyTorch 1.12+
- CUDA 12+ (選配)
