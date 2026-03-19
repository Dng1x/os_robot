# 📦 EXE 打包说明

## 当前状态

**打包功能暂未实现**。API 接口 `/api/flow/package` 目前返回提示信息。

## 为什么未实现？

EXE 打包是一个复杂的功能，涉及：
1. 将流程数据和素材嵌入到可执行文件中
2. 打包 Python 运行时环境
3. 处理依赖库（OpenCV、PaddleOCR 等体积较大）
4. 生成的 EXE 文件可能很大（200MB+）

## 手动打包方案

### 方法1: 使用 PyInstaller（推荐）

```bash
# 1. 安装 PyInstaller
pip install pyinstaller

# 2. 进入后端目录
cd automation-tool/backend

# 3. 创建打包脚本
# 将流程 JSON 文件放在 backend/storage/flows/ 目录

# 4. 执行打包
pyinstaller --onefile \
    --name "MyAutomation" \
    --add-data "storage:storage" \
    main.py

# Windows 下使用:
pyinstaller --onefile --name "MyAutomation" --add-data "storage;storage" main.py

# 5. 生成的 EXE 在 dist/ 目录
```

### 方法2: 创建独立的执行脚本

创建一个 `run_flow.py`：

```python
"""
独立运行脚本
"""
import json
from executor import FlowExecutor

# 加载流程文件
with open('my_flow.json', 'r', encoding='utf-8') as f:
    flow_data = json.load(f)

# 执行流程
executor = FlowExecutor(flow_data)
result = executor.execute()

print("执行完成！")
print(result)
```

然后打包这个脚本：
```bash
pyinstaller --onefile --add-data "my_flow.json;." run_flow.py
```

### 方法3: 使用 Nuitka

Nuitka 可以生成更小、更快的可执行文件：

```bash
pip install nuitka
python -m nuitka --onefile --standalone run_flow.py
```

## 打包注意事项

### 1. 文件大小
- 基础 Python + 依赖: ~50MB
- OpenCV: ~100MB
- PaddleOCR + 模型: ~200MB
- **总计可能达到 300-500MB**

### 2. 素材处理
素材文件（图片）需要：
- 方式1: 嵌入到 EXE 中（`--add-data`）
- 方式2: 放在 EXE 旁边的文件夹中
- 方式3: 转换为 base64 嵌入 JSON

### 3. 依赖项
确保包含所有运行时依赖：
```bash
pyinstaller --onefile \
    --hidden-import=paddleocr \
    --hidden-import=cv2 \
    --hidden-import=pyautogui \
    run_flow.py
```

## 推荐的打包流程

### 步骤1: 准备流程文件
1. 在前端设计好流程
2. 导出为 JSON 文件
3. 将素材图片也一起准备好

### 步骤2: 创建执行脚本
```python
# standalone_runner.py
import json
import os
import sys

# 获取资源路径（支持打包后）
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 加载流程
flow_file = resource_path('flow.json')
with open(flow_file, 'r', encoding='utf-8') as f:
    flow_data = json.load(f)

# 更新素材路径
for asset in flow_data.get('assets', []):
    asset['path'] = resource_path(f"assets/{asset['name']}")

# 执行
from executor import FlowExecutor
executor = FlowExecutor(flow_data)
result = executor.execute()

input("按回车键退出...")
```

### 步骤3: 打包
```bash
pyinstaller --onefile \
    --name "MyAutomation" \
    --add-data "flow.json;." \
    --add-data "assets;assets" \
    --hidden-import=paddleocr \
    --hidden-import=cv2 \
    standalone_runner.py
```

### 步骤4: 测试
```bash
cd dist
./MyAutomation  # Linux/Mac
MyAutomation.exe  # Windows
```

## 优化打包大小

### 1. 不包含 OCR（如果不需要）
修改 `requirements.txt`，去掉：
```
paddleocr
paddlepaddle
```

### 2. 使用虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
pyinstaller ...
```

### 3. 排除不需要的文件
```bash
pyinstaller --onefile \
    --exclude-module matplotlib \
    --exclude-module PIL.ImageQt \
    run_flow.py
```

## 替代方案

### 1. 直接分发 Python 脚本
如果用户有 Python 环境，直接分发：
- 流程 JSON 文件
- 素材文件夹
- 执行脚本
- requirements.txt

### 2. 使用便携版 Python
打包一个便携版 Python + 脚本，无需安装。

### 3. Docker 容器
在 Linux 环境下可以使用 Docker：
```bash
docker build -t my-automation .
docker run my-automation
```

## 未来计划

我们计划在后续版本中实现：
- ✅ 一键打包功能
- ✅ 自动处理依赖
- ✅ 智能压缩
- ✅ 进度显示
- ✅ 打包配置选项

## 总结

**当前推荐方案**：
1. 使用 PyInstaller 手动打包
2. 创建独立的执行脚本
3. 包含流程 JSON 和素材文件

**优点**：
- 完全独立运行
- 无需 Python 环境
- 可分发给其他人

**缺点**：
- 文件较大（300-500MB）
- 打包过程稍复杂
- 需要手动处理

如有疑问，请参考 PyInstaller 官方文档：
https://pyinstaller.org/
