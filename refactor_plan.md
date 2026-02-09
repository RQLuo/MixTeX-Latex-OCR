# MixTeX GUI 拆分方案（草案）

目标是把当前单文件 `mixtexgui/mixtex_ui.py` 拆成多模块，降低耦合，便于后续维护和迭代，同时保持功能不变。

## 拆分目标
- 将 UI、模型管理、OCR 推理、配置常量解耦。
- 依赖保持单向：`app` 组装，`ui` 调用 `model/ocr`，`model/ocr` 不依赖 `ui`。
- 行为不改，只做结构整理。

## 模块划分

### 1) `mixtexgui/app.py`
- 作用：程序入口、Tk 初始化、创建 `MixTeXApp`。
- 内容：
  - `if __name__ == "__main__":` 启动逻辑
  - root/app 初始化

### 2) `mixtexgui/ui.py`
- 作用：UI 组件、事件绑定、菜单/托盘、窗口拖拽、log 输出。
- 内容：
  - `MixTeXApp` 大部分 UI 逻辑
  - `start_move` / `do_move` / `show_menu` / `update_icon` / `log`
  - 菜单回调（触发下载、切换 OCR、展示 about/donate）
- 约束：UI 不直接管模型加载，只调用 `model`/`ocr` 接口。

### 3) `mixtexgui/model.py`
- 作用：模型文件检查、下载、加载。
- 内容：
  - `REQUIRED_MODEL_FILES`
  - `check_model_files()`
  - `_check_network()`
  - `_download_hf_file()`
  - `download_model()` / `download_model_worker()`
  - `load_model()`（返回 tokenizer / processor / onnx sessions）

### 4) `mixtexgui/ocr.py`
- 作用：推理流程与循环。
- 内容：
  - `mixtex_inference`
  - `pad_image`
  - `ocr_loop`
  - `check_repetition`
  - `convert_align_to_equations`
- 约束：函数接收 `model` 和 UI 传入的状态（如 `current_image`）。

### 5) `mixtexgui/config.py`
- 作用：集中放路径/常量/默认值。
- 内容：
  - `BASE_PATH`, `MODEL_DIR`
  - `REQUIRED_MODEL_FILES`
  - 默认 `max_length` / `num_layers` / `hidden_size` / `heads` 等

## 依赖关系
- `app.py` → `ui.py`
- `ui.py` → `model.py` / `ocr.py` / `config.py`
- `model.py` / `ocr.py` 不依赖 `ui.py`

## 建议的拆分顺序（低风险）
1. 抽出 `model.py`（模型检查/下载/加载）。
2. 抽出 `ocr.py`（推理流程）。
3. 最后拆 `ui.py` 与 `app.py`。

这样可以保持功能稳定，每一步都可独立验证。
