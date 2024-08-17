import tkinter as tk
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item
import threading
from transformers import AutoTokenizer, AutoImageProcessor
import onnxruntime as ort
import numpy as np
from PIL import ImageGrab
import pyperclip
import time
import sys
import os
import csv

if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")
    
class MixTeXApp:
    def __init__(self, root):
        self.root = root
        self.root.title('MixTeX')
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
        self.root.wm_attributes('-topmost', 1)
        self.root.attributes('-alpha', 0.85)
        self.TRANSCOLOUR = '#a9abc6'
        self.root.wm_attributes("-transparentcolor", self.TRANSCOLOUR)

        self.icon = Image.open(os.path.join(base_path, "icon.png"))
        self.icon_tk = ImageTk.PhotoImage(self.icon)

        self.main_frame = tk.Frame(self.root, bg=self.TRANSCOLOUR)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.icon_label = tk.Label(self.main_frame, image=self.icon_tk, bg=self.TRANSCOLOUR)
        self.icon_label.pack(pady=10)

        self.text_frame = tk.Frame(self.main_frame, bg='white', bd=1, relief=tk.SOLID)
        self.text_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.text_box = tk.Text(self.text_frame, wrap=tk.WORD, bg='white', fg='black', height=6, width=30)
        self.text_box.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)

        self.icon_label.bind('<ButtonPress-1>', self.start_move)
        self.icon_label.bind('<B1-Motion>', self.do_move)
        self.icon_label.bind('<ButtonPress-3>', self.show_menu)
        self.data_collection_enabled = False  # 默认关闭数据收集
        self.data_folder = "data"
        self.metadata_file = os.path.join(self.data_folder, "metadata.csv")
        
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['file_name', 'text'])
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="设置", command=self.show_settings)
        self.menu.add_command(label="最小化", command=self.minimize)
        self.menu.add_command(label="关于", command=self.show_about)
        self.menu.add_command(label="打赏", command=self.show_donate)
        self.menu.add_command(label="退出", command=self.quit)

        self.create_tray_icon()

        self.model = self.load_model('onnx')

        self.ocr_thread = threading.Thread(target=self.ocr_loop, daemon=True)
        self.ocr_thread.start()

        self.donate_window = None

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.overrideredirect(True)
        settings_window.attributes('-alpha', 0.85)
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_height = self.root.winfo_height()
        settings_window.geometry(f"+{main_x}+{main_y + main_height}")
        frame = tk.Frame(settings_window, bg='white')
        frame.pack(fill=tk.BOTH, expand=True)
        self.data_collection_var = tk.BooleanVar(value=self.data_collection_enabled)
        data_collection_checkbox = tk.Checkbutton(frame, text="启用数据收集", 
                                                variable=self.data_collection_var, 
                                                command=self.toggle_data_collection,
                                                bg='white')
        data_collection_checkbox.pack(pady=10)
        context_menu = tk.Menu(settings_window, tearoff=0)
        context_menu.add_command(label="关闭", command=settings_window.destroy)
        def show_context_menu(event):
            context_menu.tk_popup(event.x_root, event.y_root)

        frame.bind('<Button-3>', show_context_menu)
        def start_move(event):
            settings_window.x = event.x
            settings_window.y = event.y

        def do_move(event):
            deltax = event.x - settings_window.x
            deltay = event.y - settings_window.y
            x = settings_window.winfo_x() + deltax
            y = settings_window.winfo_y() + deltay
            settings_window.geometry(f"+{x}+{y}")

        frame.bind('<ButtonPress-1>', start_move)
        frame.bind('<B1-Motion>', do_move)
        
    def save_data(self, image, text):
        file_name = f"{int(time.time())}.png"
        file_path = os.path.join(self.data_folder, file_name)
        image.save(file_path, 'PNG')
        with open(self.metadata_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([file_name, text])

    def toggle_data_collection(self):
        self.data_collection_enabled = self.data_collection_var.get()
    
    def minimize(self):
        self.root.withdraw()
        self.tray_icon.visible = True

    def show_about(self):
        about_text = "MixTeX\n版本: 1.1.2 \n作者: lrqlrqlrq \nQQ群：612725068 \nB站：https://space.bilibili.com/8922788 \nGithub: https://github.com/RQLuo/MixTeX"
        self.text_box.delete(1.0, tk.END)
        self.text_box.insert(tk.END, about_text)

    def show_donate(self):
        donate_text = "\n!!!感谢您的支持!!!\n"
        self.text_box.delete(1.0, tk.END)
        self.text_box.insert(tk.END, donate_text)

        donate_frame = tk.Frame(self.main_frame, bg='white')
        donate_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        donate_image = Image.open(os.path.join(base_path, "donate.png")).resize((400,400))
        donate_photo = ImageTk.PhotoImage(donate_image)

        image_label = tk.Label(donate_frame, image=donate_photo)
        image_label.image = donate_photo
        image_label.pack(expand=True, fill=tk.BOTH)

        close_button = tk.Button(donate_frame, text="☒", command=lambda: donate_frame.destroy())
        close_button.place(relx=1.0, rely=0.0, x=-15, y=5, width=12, height=12, anchor="ne")
    def quit(self):
        self.tray_icon.stop()
        self.root.quit()

    def create_tray_icon(self):
        menu = pystray.Menu(
            item('显示', self.show_window),
            item('退出', self.quit)
        )
        self.tray_icon = pystray.Icon("MixTeX", self.icon, "MixTeX", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self):
        self.root.deiconify()
        self.tray_icon.visible = False

    def load_model(self, path):
        try:
            tokenizer = AutoTokenizer.from_pretrained(path)
            feature_extractor = AutoImageProcessor.from_pretrained(path)
            encoder_session = ort.InferenceSession(f"{path}/encoder_model.onnx")
            decoder_session = ort.InferenceSession(f"{path}/decoder_model.onnx")
            self.log('\n===成功加载模型===\n')
        except Exception as e:
            self.log(f"Error loading models or tokenizer: {e}")
            exit(1)
        return (tokenizer, feature_extractor, encoder_session, decoder_session)

    def check_repetition(self, s, repeats=12):
        for pattern_length in range(1, len(s) // repeats + 1):
            for start in range(len(s) - repeats * pattern_length + 1):
                pattern = s[start:start + pattern_length]
                if s[start:start + repeats * pattern_length] == pattern * repeats:
                    return True
        return False

    def mixtex_inference(self, image, max_length):
        tokenizer, feature_extractor, encoder_session, decoder_session = self.model
        try:
            generated_text = ""
            inputs = feature_extractor(image, return_tensors="np").pixel_values
            encoder_outputs = encoder_session.run(None, {"pixel_values": inputs})[0]
            decoder_input_ids = tokenizer("<s>", return_tensors="np").input_ids.astype(np.int64)
            for _ in range(max_length):
                decoder_outputs = decoder_session.run(None, {
                    "input_ids": decoder_input_ids,
                    "encoder_hidden_states": encoder_outputs
                })[0]
                next_token_id = np.argmax(decoder_outputs[:, -1, :], axis=-1)
                decoder_input_ids = np.concatenate([decoder_input_ids, next_token_id[:, None]], axis=-1)
                generated_text += tokenizer.decode(next_token_id, skip_special_tokens=True)
                self.log(tokenizer.decode(next_token_id, skip_special_tokens=True), end="")
                if self.check_repetition(generated_text, 12):
                    self.log('\n===?!重复重复重复!?===\n')
                    break
                if next_token_id == tokenizer.eos_token_id:
                    self.log('\n===成功复制到剪切板===\n')
                    break
            return generated_text
        except Exception as e:
            self.log(f"Error during OCR: {e}")
            return ""

    def ocr_loop(self):
        while True:
            try:
                image = ImageGrab.grabclipboard()
                if image is not None and type(image) != list:
                    result = self.mixtex_inference(image.convert("RGB"), 512)
                    result = result.replace('\\[', '\\begin{align*}').replace('\\]', '\\end{align*}').replace('%', '\\%')
                    pyperclip.copy(result)
                    if self.data_collection_enabled:
                        self.save_data(image, result)
            except Exception as e:
                self.log(f"Error: {e}")
            time.sleep(0.1)

    def log(self, message, end='\n'):
        self.text_box.insert(tk.END, message + end)
        self.text_box.see(tk.END)

if __name__ == '__main__':
    root = tk.Tk()
    app = MixTeXApp(root)
    root.mainloop()
