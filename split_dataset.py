import os
import random
import shutil

def create_directory_structure():
    """創建所需的目錄結構"""
    directories = [
        'datasets/train/images',
        'datasets/train/labels',
        'datasets/valid/images',
        'datasets/valid/labels'
    ]
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)

def get_all_files():
    """獲取所有的圖片和標籤文件對"""
    files = []
    # 處理img目錄
    if os.path.exists('img'):
        for file in os.listdir('img'):
            if file.endswith('.png'):
                base_name = os.path.splitext(file)[0]
                img_path = os.path.join('img', file)
                label_path = os.path.join('img', base_name + '.txt')
                if os.path.exists(label_path):
                    files.append((img_path, label_path))
    return files

def split_dataset(files, train_ratio=0.8):
    """將文件分為訓練集和驗證集"""
    random.shuffle(files)  # 隨機打亂文件順序
    split_idx = int(len(files) * train_ratio)
    return files[:split_idx], files[split_idx:]

def copy_files(files, is_train=True):
    """將文件複製到相應的目錄"""
    base_dir = 'datasets/train' if is_train else 'datasets/valid'
    
    for img_path, label_path in files:
        # 複製圖片
        dst_img = os.path.join(base_dir, 'images', os.path.basename(img_path))
        shutil.copy2(img_path, dst_img)
        
        # 複製標籤
        dst_label = os.path.join(base_dir, 'labels', os.path.basename(label_path))
        shutil.copy2(label_path, dst_label)

def main():
    # 設置隨機種子以確保結果可重現
    random.seed(42)
    
    # 創建目錄結構
    create_directory_structure()
    
    # 獲取所有文件
    all_files = get_all_files()
    print(f"總共找到 {len(all_files)} 對圖片和標籤文件")
    
    # 分割數據集
    train_files, valid_files = split_dataset(all_files)
    print(f"訓練集: {len(train_files)} 對文件")
    print(f"驗證集: {len(valid_files)} 對文件")
    
    # 複製文件到相應目錄
    print("正在複製訓練集文件...")
    copy_files(train_files, is_train=True)
    print("正在複製驗證集文件...")
    copy_files(valid_files, is_train=False)
    
    print("數據集分割完成！")

if __name__ == "__main__":
    main()