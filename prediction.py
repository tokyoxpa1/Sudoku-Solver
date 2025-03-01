import os
from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="這裡輸入API_KEY"
)

def convert_to_yolo(result):
    """Convert detection results to YOLO format."""
    img_width = result['image']['width']
    img_height = result['image']['height']
    
    yolo_annotations = []
    for pred in result['predictions']:
        # 歸一化座標
        x_center = pred['x'] / img_width
        y_center = pred['y'] / img_height
        width = pred['width'] / img_width
        height = pred['height'] / img_height
        class_id = pred['class_id']
        
        # YOLO格式: <class> <x_center> <y_center> <width> <height>
        yolo_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
        yolo_annotations.append(yolo_line)
    
    return yolo_annotations

def process_image(img_path):
    """處理單張圖片並保存YOLO格式的標註"""
    print(f"Processing {img_path}...")
    
    # 進行推理
    result = CLIENT.infer(img_path, model_id="digits-zv0yj/1")
    
    # 轉換為YOLO格式
    yolo_annotations = convert_to_yolo(result)
    
    # 保存到對應的txt文件
    txt_path = os.path.splitext(img_path)[0] + '.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(yolo_annotations))
    
    print(f"Saved annotations to {txt_path}")

def main():
    # 遍歷./img目錄下的所有PNG圖片
    img_dir = './img'
    for filename in os.listdir(img_dir):
        if filename.endswith('.png'):
            img_path = os.path.join(img_dir, filename)
            process_image(img_path)

if __name__ == '__main__':
    main()