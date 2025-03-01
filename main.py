import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import ImageGrab, Image
import keyboard
import os
import json
from ultralytics import YOLO
import numpy as np
import pyautogui

class SudokuSolver:
    """數獨解題器類別，使用優化的約束傳播和啟發式算法"""
    def __init__(self):
        self.rows = [set() for _ in range(9)]      # 跟踪每行已使用的數字
        self.cols = [set() for _ in range(9)]      # 跟踪每列已使用的數字
        self.boxes = [set() for _ in range(9)]     # 跟踪每個3x3方格已使用的數字
        self.empty_cells = []                      # 儲存所有空格子的位置

    def initialize_constraints(self, grid):
        """初始化約束條件和空格子列表"""
        for i in range(9):
            for j in range(9):
                if grid[i][j] != 0:
                    num = grid[i][j]
                    self.rows[i].add(num)
                    self.cols[j].add(num)
                    self.boxes[(i // 3) * 3 + j // 3].add(num)
                else:
                    self.empty_cells.append((i, j))
        
        # 按照可能的候選數字數量排序空格子（啟發式）
        self.empty_cells.sort(key=lambda pos: self._count_candidates(grid, pos))

    def _count_candidates(self, grid, pos):
        """計算一個空格子可能的候選數字數量"""
        i, j = pos
        box_idx = (i // 3) * 3 + j // 3
        used = self.rows[i] | self.cols[j] | self.boxes[box_idx]
        return sum(1 for num in range(1, 10) if num not in used)

    def is_valid(self, num, pos):
        """檢查在指定位置放置數字是否有效"""
        i, j = pos
        box_idx = (i // 3) * 3 + j // 3
        return (num not in self.rows[i] and
                num not in self.cols[j] and
                num not in self.boxes[box_idx])

    def solve(self, grid):
        """解決數獨"""
        self.initialize_constraints(grid)
        return self._backtrack(grid, 0)

    def _backtrack(self, grid, idx):
        """回溯算法"""
        if idx >= len(self.empty_cells):
            return True
        
        i, j = self.empty_cells[idx]
        box_idx = (i // 3) * 3 + j // 3
        
        # 使用約束條件快速找出候選數字
        candidates = [num for num in range(1, 10) if self.is_valid(num, (i, j))]
        
        for num in candidates:
            # 放置數字並更新約束
            grid[i][j] = num
            self.rows[i].add(num)
            self.cols[j].add(num)
            self.boxes[box_idx].add(num)
            
            # 繼續解下一個空格子
            if self._backtrack(grid, idx + 1):
                return True
            
            # 回溯
            grid[i][j] = 0
            self.rows[i].remove(num)
            self.cols[j].remove(num)
            self.boxes[box_idx].remove(num)
        
        return False

window_width = 330  # 縮小預設視窗寬度
window_height = 150  # 縮小預設視窗高度

class ScreenshotApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("sudoku解題器")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        
        # 添加速度調整滑塊的變數
        self.speed_scale_var = tk.DoubleVar(value=10.0)  # 預設值為10
        
        # 載入YOLO模型
        try:
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sudoku.pt')
            if not os.path.exists(model_path):
                model_path = 'sudoku.pt'  # 回退到當前目錄
            self.model = YOLO(model_path)
        except Exception as e:
            print("錯誤", f"模型載入失敗: {str(e)}")
            raise e
        
        # 主視窗大小和位置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - window_width - 20
        y = screen_height - window_height - 20
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 建立主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 操作按鈕
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=0, column=0, columnspan=4, pady=10)
        ttk.Button(button_frame, text="框選題目區域", command=self.start_selection).pack()

        # 區域展開狀態
        self.coord_expanded = False
        self.hotkey_expanded = False
        self.advanced_expanded = False  # 新增進階選項狀態
        
        # 建立展開/隱藏按鈕的容器框架
        expand_frame = ttk.Frame(self.main_frame)
        expand_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # 為按鈕創建內部框架以實現置中
        button_container = ttk.Frame(expand_frame)
        button_container.pack(expand=True)
        
        # 設定按鈕固定寬度並置中對齊
        button_width = 42  # 設定合適的按鈕寬度

        # 進階設定按鈕
        self.advanced_button = ttk.Button(button_container, text="▼ 進階設定",
                                      command=self.toggle_advanced_frame,
                                      width=button_width)
        self.advanced_button.pack(pady=2)
        
        # 進階設定框架
        self.advanced_frame = ttk.LabelFrame(self.main_frame, padding="5")
        self.advanced_frame.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.advanced_frame.grid_remove()  # 預設隱藏
        
        # 添加速度調整滑塊（1 到 100）
        ttk.Label(self.advanced_frame, text="自動填入速度調整:").grid(row=0, column=0, sticky=tk.W)
        # ttk.Scale 滑塊預設顯示在bar條的中間
        speed_scale = ttk.Scale(self.advanced_frame, from_=1.0, to=10.0,
                               variable=self.speed_scale_var,
                               orient=tk.HORIZONTAL,
                               command=self.update_speed_label)  # 添加回調函數
        speed_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # 添加當前值顯示標籤
        self.speed_label = ttk.Label(self.advanced_frame, text="")
        self.speed_label.grid(row=0, column=2, padx=5)
        
        # 設定預設值為10
        speed_scale.set(10.0)
        self.coord_button = ttk.Button(button_container, text="▼ 截圖區域座標",
                                    command=self.toggle_coord_frame,
                                    width=button_width)
        self.coord_button.pack(pady=2)
        
        # 座標輸入框和標籤
        self.coord_frame = ttk.LabelFrame(self.main_frame, padding="5")
        self.coord_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.coord_frame.grid_remove()  # 預設隱藏
        
        ttk.Label(self.coord_frame, text="起始 X:").grid(row=0, column=0, sticky=tk.W)
        self.start_x_var = tk.StringVar()
        self.start_x_entry = ttk.Entry(self.coord_frame, textvariable=self.start_x_var, width=10)
        self.start_x_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(self.coord_frame, text="起始 Y:").grid(row=0, column=2, sticky=tk.W)
        self.start_y_var = tk.StringVar()
        self.start_y_entry = ttk.Entry(self.coord_frame, textvariable=self.start_y_var, width=10)
        self.start_y_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(self.coord_frame, text="結束 X:").grid(row=1, column=0, sticky=tk.W)
        self.end_x_var = tk.StringVar()
        self.end_x_entry = ttk.Entry(self.coord_frame, textvariable=self.end_x_var, width=10)
        self.end_x_entry.grid(row=1, column=1, padx=5)
        
        ttk.Label(self.coord_frame, text="結束 Y:").grid(row=1, column=2, sticky=tk.W)
        self.end_y_var = tk.StringVar()
        self.end_y_entry = ttk.Entry(self.coord_frame, textvariable=self.end_y_var, width=10)
        self.end_y_entry.grid(row=1, column=3, padx=5)
        
        # 座標操作按鈕
        coord_button_frame = ttk.Frame(self.coord_frame)
        coord_button_frame.grid(row=2, column=0, columnspan=4, pady=5)
        ttk.Button(coord_button_frame, text="清除座標", command=self.clear_coordinates).pack(side=tk.LEFT, padx=5)
        ttk.Label(coord_button_frame, text="(未設定座標時預設全螢幕截圖)").pack(side=tk.LEFT, padx=5)
        
        # 熱鍵展開按鈕，使用相同的容器來確保一致的布局
        self.hotkey_button = ttk.Button(button_container, text="▼ 熱鍵設定",
                                    command=self.toggle_hotkey_frame,
                                    width=button_width)
        self.hotkey_button.pack(pady=2)
        
        # 熱鍵設定框架
        self.hotkey_frame = ttk.LabelFrame(self.main_frame, padding="5")
        self.hotkey_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.hotkey_frame.grid_remove()  # 預設隱藏
        
        # 修飾鍵選擇
        self.mod1_var = tk.StringVar(value="無")
        self.mod2_var = tk.StringVar(value="無")
        self.key_var = tk.StringVar(value="'")
        
        ttk.Label(self.hotkey_frame, text="組合鍵 1:").grid(row=0, column=0, sticky=tk.W)
        mod1_combo = ttk.Combobox(self.hotkey_frame, textvariable=self.mod1_var, width=8)
        mod1_combo['values'] = ['無', 'ctrl', 'shift', 'alt']
        mod1_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(self.hotkey_frame, text="組合鍵 2:").grid(row=0, column=2, sticky=tk.W)
        mod2_combo = ttk.Combobox(self.hotkey_frame, textvariable=self.mod2_var, width=8)
        mod2_combo['values'] = ['無', 'ctrl', 'shift', 'alt']
        mod2_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(self.hotkey_frame, text="主鍵:").grid(row=1, column=0, sticky=tk.W)
        key_combo = ttk.Combobox(self.hotkey_frame, textvariable=self.key_var, width=8)
        keys = ([f'F{i}' for i in range(1, 13)] + 
                [str(i) for i in range(10)] + 
                [chr(i) for i in range(ord('A'), ord('Z')+1)])
        key_combo['values'] = keys
        key_combo.grid(row=1, column=1, padx=5)
        
        # 熱鍵開關按鈕
        self.hotkey_active = False
        self.toggle_hotkey_button = ttk.Button(self.hotkey_frame, text="啟動熱鍵", command=self.toggle_hotkey)
        self.toggle_hotkey_button.grid(row=1, column=2, columnspan=2, padx=5, pady=5)
        
       # 選擇視窗相關變數
        self.selection_window = None
        self.canvas = None
        self.start_x = None
        self.start_y = None
        self.selection_rect = None
        
        # 載入設定
        self.load_settings()

    def update_speed_label(self, value):
        """更新速度顯示標籤"""
        self.speed_label.config(text=str(int(float(value))))
        
    def toggle_coord_frame(self):
        """切換座標框架的顯示狀態"""
        self.coord_expanded = not self.coord_expanded
        
        if self.coord_expanded:
            self.coord_frame.grid()
            self.coord_button.configure(text="▲ 截圖區域座標")
        else:
            self.coord_frame.grid_remove()
            self.coord_button.configure(text="▼ 截圖區域座標")
            
        # 強制更新視窗佈局
        self.root.update_idletasks()
        
        # 根據當前狀態更新視窗尺寸
        if self.coord_expanded or self.hotkey_expanded or self.advanced_expanded:
            new_height = self.root.winfo_reqheight()
            self.root.geometry(f"{window_width}x{new_height}")
        else:
            self.root.geometry(f"{window_width}x{window_height}")
        
        # 再次強制更新以確保正確顯示
        self.root.update()
                
    def toggle_hotkey_frame(self):
        """切換熱鍵框架的顯示狀態"""
        self.hotkey_expanded = not self.hotkey_expanded
        
        if self.hotkey_expanded:
            self.hotkey_frame.grid()
            self.hotkey_button.configure(text="▲ 熱鍵設定")
        else:
            self.hotkey_frame.grid_remove()
            self.hotkey_button.configure(text="▼ 熱鍵設定")
            
        # 強制更新視窗佈局
        self.root.update_idletasks()
        
        # 根據當前狀態更新視窗尺寸
        if self.coord_expanded or self.hotkey_expanded or self.advanced_expanded:
            new_height = self.root.winfo_reqheight()
            self.root.geometry(f"{window_width}x{new_height}")
        else:
            self.root.geometry(f"{window_width}x{window_height}")
        
        # 再次強制更新以確保正確顯示
        self.root.update()

    def toggle_advanced_frame(self):
        """切換進階設定框架的顯示狀態"""
        self.advanced_expanded = not self.advanced_expanded
        
        if self.advanced_expanded:
            self.advanced_frame.grid()
            self.advanced_button.configure(text="▲ 進階設定")
        else:
            self.advanced_frame.grid_remove()
            self.advanced_button.configure(text="▼ 進階設定")
            
        # 強制更新視窗佈局
        self.root.update_idletasks()
        
        # 根據當前狀態更新視窗尺寸
        if self.coord_expanded or self.hotkey_expanded or self.advanced_expanded:
            new_height = self.root.winfo_reqheight()
            self.root.geometry(f"{window_width}x{new_height}")
        else:
            self.root.geometry(f"{window_width}x{window_height}")
        
        # 再次強制更新以確保正確顯示
        self.root.update()

    def clear_coordinates(self):
        """清除所有座標設定"""
        self.start_x_var.set("")
        self.start_y_var.set("")
        self.end_x_var.set("")
        self.end_y_var.set("")
        
    def get_screenshot_area(self):
        """獲取截圖區域，如果未設定則返回全螢幕範圍"""
        try:
            if (self.start_x_var.get() and self.start_y_var.get() and 
                self.end_x_var.get() and self.end_y_var.get()):
                return (
                    int(self.start_x_var.get()),
                    int(self.start_y_var.get()),
                    int(self.end_x_var.get()),
                    int(self.end_y_var.get())
                )
            else:
                return (0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        except ValueError:
            return (0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        
    def get_hotkey_string(self):
        """取得當前熱鍵組合字串"""
        hotkey = []
        if self.mod1_var.get() != '無':
            hotkey.append(self.mod1_var.get())
        if self.mod2_var.get() != '無':
            hotkey.append(self.mod2_var.get())
        hotkey.append(self.key_var.get().lower())
        return '+'.join(hotkey)
        
    def toggle_hotkey(self):
        """切換熱鍵啟用狀態"""
        self.hotkey_active = not self.hotkey_active
        if self.hotkey_active:
            # 註冊熱鍵
            try:
                hotkey = self.get_hotkey_string()
                keyboard.add_hotkey(hotkey, self.take_screenshot)
                self.toggle_hotkey_button.configure(text="關閉熱鍵")
                self.save_settings()
            except Exception as e:
                print("錯誤", f"熱鍵註冊失敗: {str(e)}")
                self.hotkey_active = False
        else:
            # 取消熱鍵
            keyboard.unhook_all()
            self.toggle_hotkey_button.configure(text="啟動熱鍵")
            
    def save_settings(self):
        """儲存當前設定"""
        settings = {
            'hotkey': {
                'mod1': self.mod1_var.get(),
                'mod2': self.mod2_var.get(),
                'key': self.key_var.get()
            },
            'coordinates': {
                'start_x': self.start_x_var.get(),
                'start_y': self.start_y_var.get(),
                'end_x': self.end_x_var.get(),
                'end_y': self.end_y_var.get()
            },
            'ui': {
                'coord_expanded': self.coord_expanded,
                'hotkey_expanded': self.hotkey_expanded,
                'advanced_expanded': self.advanced_expanded
            },
            'advanced': {
                'speed_scale': self.speed_scale_var.get()
            }
        }
        try:
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"儲存設定失敗: {e}")
            
    def load_settings(self):
        """載入設定"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                # 載入熱鍵設定
                self.mod1_var.set(settings['hotkey']['mod1'])
                self.mod2_var.set(settings['hotkey']['mod2'])
                self.key_var.set(settings['hotkey']['key'])
                
                # 載入座標設定
                if 'coordinates' in settings:
                    self.start_x_var.set(settings['coordinates']['start_x'])
                    self.start_y_var.set(settings['coordinates']['start_y'])
                    self.end_x_var.set(settings['coordinates']['end_x'])
                    self.end_y_var.set(settings['coordinates']['end_y'])
                
                # 載入UI狀態
                if 'ui' in settings:
                    if settings['ui'].get('coord_expanded', False):
                        self.toggle_coord_frame()
                    if settings['ui'].get('hotkey_expanded', False):
                        self.toggle_hotkey_frame()
                    if settings['ui'].get('advanced_expanded', False):
                        self.toggle_advanced_frame()
                
                # 載入進階設定
                if 'advanced' in settings:
                    if 'speed_scale' in settings['advanced']:
                        self.speed_scale_var.set(settings['advanced']['speed_scale'])
                
                # 自動啟動熱鍵
                self.root.after(1000, self.toggle_hotkey)  # 延遲1秒後啟動熱鍵
                
        except Exception as e:
            print(f"載入設定失敗: {e}")
            
    def start_selection(self):
        """開啟選擇區域視窗"""
        self.root.iconify()  # 最小化主視窗
        
        # 建立全螢幕選擇視窗
        self.selection_window = tk.Toplevel()
        self.selection_window.attributes('-fullscreen', True, '-alpha', 0.3)
        self.selection_window.configure(bg='gray')
        
        # 建立畫布
        self.canvas = tk.Canvas(
            self.selection_window,
            highlightthickness=0,
            bg='gray'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 綁定滑鼠事件
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        # 綁定Esc鍵取消選擇
        keyboard.add_hotkey('esc', self.cancel_selection)
        
        # 顯示提示文字
        self.show_help_text()
        
    def show_help_text(self):
        help_text = "使用滑鼠拖曳選擇區域\nEsc: 取消"
        self.canvas.create_text(
            self.selection_window.winfo_screenwidth() // 2,
            50,
            text=help_text,
            fill="white",
            font=("微軟正黑體", 14),
            tag="help_text"
        )
        
    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        
    def on_mouse_drag(self, event):
        if self.start_x and self.start_y:
            # 清除之前的矩形
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
            
            # 繪製新的選取矩形
            self.selection_rect = self.canvas.create_rectangle(
                self.start_x, self.start_y,
                event.x, event.y,
                outline="white",
                width=2
            )
            
    def on_mouse_up(self, event):
        # 更新座標輸入框
        self.start_x_var.set(str(min(self.start_x, event.x)))
        self.start_y_var.set(str(min(self.start_y, event.y)))
        self.end_x_var.set(str(max(self.start_x, event.x)))
        self.end_y_var.set(str(max(self.start_y, event.y)))
        
        # 關閉選擇視窗
        self.selection_window.destroy()
        self.root.deiconify()  # 恢復主視窗
        
        # 儲存座標設定
        self.save_settings()
        
    def cancel_selection(self, event=None):
        self.selection_window.destroy()
        self.root.deiconify()  # 恢復主視窗

    def solve_sudoku(self, grid):
        """使用優化的約束傳播和啟發式算法解決數獨"""
        solver = SudokuSolver()
        return solver.solve(grid)
        
    def take_screenshot(self):
        try:
            # 暫時隱藏主視窗
            self.root.withdraw()
            self.root.update()
            
            # 獲取截圖區域
            x1, y1, x2, y2 = self.get_screenshot_area()
            
            # 獲取螢幕截圖
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            
            # 確保資料夾存在
            if not os.path.exists('tmp'):
                os.makedirs('tmp')

            # 保存截圖
            i = 1
            while True:
                filename = f'tmp/screenshot_{i}.png'
                if not os.path.exists(filename):
                    screenshot.save(filename)
                    # 將PIL Image轉換為numpy array以供YOLO使用
                    img_array = np.array(screenshot)
                    # 進行數字識別
                    try:
                        results = self.model(img_array)
                        if not results:
                            print("警告", "未能識別到任何數字，請確保截圖區域包含完整的數獨題目。")
                            return
                        # 顯示識別結果並直接解題
                        self.show_result(results, filename)
                    except Exception as e:
                        print("錯誤", f"數字識別失敗: {str(e)}")
                    break
                i += 1
                
        except Exception as e:
            print("錯誤", f"截圖失敗: {str(e)}")
        finally:
            self.root.deiconify()  # 恢復主視窗顯示


    def calculate_cell_center(self, i, j):
        """計算指定格子的中心點座標"""
        x1, y1, x2, y2 = self.get_screenshot_area()
        cell_width = (x2 - x1) / 9
        cell_height = (y2 - y1) / 9
        
        center_x = x1 + (cell_width * j) + (cell_width / 2)
        center_y = y1 + (cell_height * i) + (cell_height / 2)
        
        return int(center_x), int(center_y)

    def auto_fill_solution(self, initial_grid, solution_grid):
        """自動填入數獨解答"""
        # 暫時隱藏結果視窗
        self.root.iconify()
        
        # 設置pyautogui的安全設定
        #pyautogui.FAILSAFE = True
        current_value = self.speed_scale_var.get()  # 獲取當前滑塊值（1-10）
        # 設置延遲時間 範圍0.0005 ~ 0.3秒
        pyautogui.PAUSE = 0.3* (0.001/0.3) ** ( (current_value -1) / 9)
        
        try:
            # 依序填入每個需要填寫的格子
            for i in range(9):
                for j in range(9):
                    # 只填入非原始數字的位置
                    if initial_grid[i][j] == 0:
                        # 計算該格子的中心點座標
                        x, y = self.calculate_cell_center(i, j)
                        
                        # 移動滑鼠到格子中心並點擊
                        pyautogui.moveTo(x, y+2)
                        pyautogui.click()
                        
                        # 輸入數字
                        pyautogui.write(str(solution_grid[i][j]))
            
            print("完成", "答案已自動填入完成！")
        except Exception as e:
            print("錯誤", f"自動填入過程發生錯誤: {str(e)}")
        finally:
            self.root.deiconify()

    def show_result(self, results, image_path):
        """處理識別結果並自動填入答案"""
        # 創建9x9的網格來儲存數字
        sudoku_grid = [[0 for _ in range(9)] for _ in range(9)]
        
        # 從YOLO結果中獲取數字和位置
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # 獲取預測的類別（數字）和位置
                cls = int(box.cls[0])
                x, y = box.xywh[0][:2]  # 獲取中心點坐標
                
                # 計算在9x9網格中的位置
                grid_x = int(x * 9 / r.orig_shape[1])
                grid_y = int(y * 9 / r.orig_shape[0])
                
                if 0 <= grid_x < 9 and 0 <= grid_y < 9:
                    sudoku_grid[grid_y][grid_x] = cls
        
        # 保存初始網格狀態並創建求解用的網格
        solution_grid = [row[:] for row in sudoku_grid]
        
        # 嘗試解決數獨
        if self.solve_sudoku(solution_grid):
            # 直接進行自動填入
            self.auto_fill_solution(sudoku_grid, solution_grid)
        else:
            print("錯誤", "此數獨題目無解！")
    
    def import_from_image(self):
        """從本地圖片檔案導入數獨題目"""
        try:
            file_path = filedialog.askopenfilename(
                title="選擇數獨圖片",
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
            )
            if not file_path:
                return
                
            # 載入圖片
            img = Image.open(file_path)
            img_array = np.array(img)
            
            # 進行數字識別
            results = self.model(img_array)
            if not results:
                print("警告", "未能識別到任何數字，請確保圖片包含完整的數獨題目。")
                return
                
            # 顯示識別結果並直接解題
            self.show_result(results, file_path)

        except Exception as e:
            print("錯誤", f"圖片處理失敗: {str(e)}")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ScreenshotApp()
    app.run()
