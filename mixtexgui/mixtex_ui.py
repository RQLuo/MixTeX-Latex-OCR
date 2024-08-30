# Renqing Luo
# Commercial use prohibited
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
import re

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
        self.data_folder = "data"
        self.metadata_file = os.path.join(self.data_folder, "metadata.csv")
        self.use_dollars_for_inline_math = False
        self.convert_align_to_equations_enabled = False
        self.ocr_paused = False
        self.annotation_window = None
        self.current_image = None
        self.output = None
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['file_name', 'text', 'feedback'])

        # Create the menu
        self.menu = tk.Menu(self.root, tearoff=0)
        settings_menu = tk.Menu(self.menu, tearoff=0)
        settings_menu.add_checkbutton(label="$ 公式 $", onvalue=1, offvalue=0, command=self.toggle_latex_replacement, variable=tk.BooleanVar(value=self.use_dollars_for_inline_math))
        settings_menu.add_checkbutton(label="$$ 单行公式 $$", onvalue=1, offvalue=0, command=self.toggle_convert_align_to_equations, variable=tk.BooleanVar(value=self.convert_align_to_equations_enabled))
        self.menu.add_cascade(label="设置", menu=settings_menu)
        self.menu.add_command(label="反馈标注", command=self.show_feedback_options)
        self.menu.add_command(label="最小化", command=self.minimize)
        self.menu.add_command(label="关于", command=self.show_about)
        self.menu.add_command(label="打赏", command=self.show_donate)
        self.menu.add_command(label="退出", command=self.quit)

        self.create_tray_icon()

        self.model = self.load_model('onnx')

        self.ocr_thread = threading.Thread(target=self.ocr_loop, daemon=True)
        self.ocr_thread.start()

        self.donate_window = None
        self.root.bind("<F2>", self.toggle_ocr)

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

    def save_data(self, image, text, feedback):
        file_name = f"{int(time.time())}.png"
        file_path = os.path.join(self.data_folder, file_name)
        image.save(file_path, 'PNG')
        
        rows = []
        with open(self.metadata_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        updated = False
        for row in rows[1:]:
            if row[1] == text:
                row[2] = feedback
                updated = True
                break
        
        if not updated:
            rows.append([file_name, text, feedback])
        
        with open(self.metadata_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    def toggle_latex_replacement(self):
        self.use_dollars_for_inline_math = not self.use_dollars_for_inline_math

    def toggle_convert_align_to_equations(self):
        self.convert_align_to_equations_enabled = not self.convert_align_to_equations_enabled

    def minimize(self):
        self.root.withdraw()
        self.tray_icon.visible = True

    def show_about(self):
        about_text = "MixTeX\n版本: 3.2.4b \n作者: lrqlrqlrq \nQQ群：612725068 \nB站：bilibili.com/8922788 \nGithub:github.com/RQLuo"
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
            decoder_session = ort.InferenceSession(f"{path}/decoder_model_merged.onnx")
            self.log('\n===成功加载模型===\n')
        except Exception as e:
            self.log(f"Error loading models or tokenizer: {e}")
            exit(1)
        return (tokenizer, feature_extractor, encoder_session, decoder_session)

    def show_feedback_options(self):
        feedback_menu = tk.Menu(self.menu, tearoff=0)
        feedback_menu.add_command(label="完美", command=lambda: self.handle_feedback("Perfect"))
        feedback_menu.add_command(label="普通", command=lambda: self.handle_feedback("Normal"))
        feedback_menu.add_command(label="失误", command=lambda: self.handle_feedback("Mistake"))
        feedback_menu.add_command(label="错误", command=lambda: self.handle_feedback("Error"))
        feedback_menu.add_command(label="标注", command=self.add_annotation)
        feedback_menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def handle_feedback(self, feedback_type):
        image = self.current_image
        text = self.output
        if image and text:
            if self.check_repetition(text):
                self.log("反馈已记录: Repeat")
            else:
                self.save_data(image, text, feedback_type)
                self.log(f"反馈已记录: {feedback_type}")
        else:
            self.log("反馈无法记录: 缺少图片或者推理输出")

    def add_annotation(self):
        if self.annotation_window is not None:
            return  # If there's already an annotation window, do nothing

        self.annotation_window = tk.Toplevel(self.root)
        self.annotation_window.wm_attributes("-alpha", 0.85)
        self.annotation_window.overrideredirect(True)
        self.annotation_window.wm_attributes('-topmost', 1)

        self.update_annotation_position()

        entry = tk.Entry(self.annotation_window, width=45, font=('Arial', 11))
        entry.pack(padx=10, pady=10)
        entry.focus_set()

        confirm_button = tk.Button(self.annotation_window, text="确认",
                                   command=lambda: self.confirm_annotation(entry))
        confirm_button.pack(pady=(0, 10))

        # Close the window on moving the main window
        self.root.bind('<Configure>', lambda e: self.update_annotation_position())

    def confirm_annotation(self, entry):
        annotation = entry.get()
        image = self.current_image
        text = self.output
        if annotation and image and text:
            self.handle_feedback(f"Annotation: {annotation}")
            self.log(f"标注已添加: {annotation}")
        else:
            self.log("反馈无法记录: 缺少图片或推理输出或输入标注。")
        self.close_annotation()

    def update_annotation_position(self):
        if self.annotation_window:
            x = self.root.winfo_x() + 10
            y = self.root.winfo_y() + self.root.winfo_height() + 10
            self.annotation_window.geometry(f"+{x}+{y}")

    def close_annotation(self):
        if self.annotation_window:
            self.annotation_window.destroy()
        self.annotation_window = None

    def check_repetition(self, s, repeats=12):
        for pattern_length in range(1, len(s) // repeats + 1):
            for start in range(len(s) - repeats * pattern_length + 1):
                pattern = s[start:start + pattern_length]
                if s[start:start + repeats * pattern_length] == pattern * repeats:
                    return True
        return False

    def mixtex_inference(self, max_length, num_layers, hidden_size, num_attention_heads, batch_size):
        tokenizer, feature_extractor, encoder_session, decoder_session = self.model
        try:
            generated_text = ""
            head_size = hidden_size // num_attention_heads
            inputs = feature_extractor(self.current_image, return_tensors="np").pixel_values
            encoder_outputs = encoder_session.run(None, {"pixel_values": inputs})[0]
            decoder_inputs = {
                "input_ids": tokenizer("<s>", return_tensors="np").input_ids.astype(np.int64),
                "encoder_hidden_states": encoder_outputs,
                "use_cache_branch": np.array([True], dtype=bool),
                **{f"past_key_values.{i}.{t}": np.zeros((batch_size, num_attention_heads, 0, head_size), dtype=np.float32) 
                for i in range(num_layers) for t in ["key", "value"]}
            }
            for _ in range(max_length):
                decoder_outputs = decoder_session.run(None, decoder_inputs)
                next_token_id = np.argmax(decoder_outputs[0][:, -1, :], axis=-1)
                generated_text += tokenizer.decode(next_token_id, skip_special_tokens=True)
                self.log(tokenizer.decode(next_token_id, skip_special_tokens=True), end="")
                if self.check_repetition(generated_text, 21):
                    self.log('\n===?!重复重复重复!?===\n')
                    self.save_data(self.current_image, generated_text, 'Repeat')
                    break
                if next_token_id == tokenizer.eos_token_id:
                    self.log('\n===成功复制到剪切板===\n')
                    break
                
                decoder_inputs.update({
                    "input_ids": next_token_id[:, None],
                    **{f"past_key_values.{i}.{t}": decoder_outputs[i*2+1+j] 
                    for i in range(num_layers) for j, t in enumerate(["key", "value"])}
                })
            if self.convert_align_to_equations_enabled:
                generated_text = self.convert_align_to_equations(generated_text)
            return generated_text
        except Exception as e:
            self.log(f"Error during OCR: {e}")
            return ""

    def convert_align_to_equations(self, text):
        text = re.sub(r'\\begin\{align\*\}|\\end\{align\*\}', '', text).replace('&','')
        equations = text.strip().split('\\\\')
        converted = []
        for eq in equations:
            eq = eq.strip().replace('\\[','').replace('\\]','').replace('\n','')
            if eq:
                converted.append(f"$$ {eq} $$")
        return '\n'.join(converted)

    def pad_image(self, img, out_size):
        x_img, y_img = out_size
        background = Image.new('RGB', (x_img, y_img), (255, 255, 255))
        width, height = img.size
        if width < x_img and height < y_img:
            x = (x_img - width) // 2
            y = (y_img - height) // 2
            background.paste(img, (x, y))
        else:
            scale = min(x_img / width, y_img / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)
            x = (x_img - new_width) // 2
            y = (y_img - new_height) // 2
            background.paste(img_resized, (x, y))
        return background

    def ocr_loop(self):
        while True:
            if not self.ocr_paused:
                try:
                    image = ImageGrab.grabclipboard()
                    if image is not None and type(image) != list:
                        self.current_image = self.pad_image(image.convert("RGB"), (448,448))
                        result = self.mixtex_inference(512, 3, 768, 12, 1)
                        result = result.replace('\\[', '\\begin{align*}').replace('\\]', '\\end{align*}').replace('%', '\\%')
                        self.output = result
                        if self.use_dollars_for_inline_math:
                            result = result.replace('\\(', '$').replace('\\)', '$')
                        pyperclip.copy(result)
                except Exception as e:
                    self.log(f"Error: {e}")
                time.sleep(0.1)

    def toggle_ocr(self, event=None):
        self.ocr_paused = not self.ocr_paused
        self.root.after(0, self.update_icon)

    def update_icon(self):
        if self.ocr_paused:
            new_icon = Image.open(os.path.join(base_path, "icon_gray.png"))
        else:
            new_icon = Image.open(os.path.join(base_path, "icon.png"))
        self.icon = new_icon
        self.icon_tk = ImageTk.PhotoImage(self.icon)
        self.icon_label.config(image=self.icon_tk)
        self.tray_icon.icon = self.icon
        
    def log(self, message, end='\n'):
        self.text_box.insert(tk.END, message + end)
        self.text_box.see(tk.END)

if __name__ == '__main__':
    root = tk.Tk()
    app = MixTeXApp(root)
    root.mainloop()
