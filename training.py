from ultralytics import YOLO
#訓練模型 資料在dataset資料夾下
model = YOLO('sudoku.pt')

if __name__ == '__main__':
  # Train the model
  results = model.train(
    data='./datasets/data.yaml',
    epochs=1000, 
    batch=4, 
    imgsz=480,
    device="0",
  )

