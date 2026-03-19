# 设计来源与未来目标
本项目由东北大学Ecal实验室搭建，由贾子熙教授负责核心思路与框架搭建，由实验室成员共同负责细节构建与版本维护
本项目旨在搭建一个多模态大模型驱动的视觉自动化系统，目前已基本完成所有基本功能和骨架部分，后续改进目标是进一步提高自动化程度并与ai agent平台联动实现一个智能视觉ai agent自动流水线


# 自动化工具后端

Python + FastAPI 实现的自动化脚本执行后端

## 功能特性

- ✅ RESTful API 接口
- ✅ 流程执行引擎
- ✅ 图像识别（OpenCV）
- ✅ OCR 文字识别（PaddleOCR）
- ✅ 窗口管理
- ✅ 鼠标键盘控制
- ✅ 变量系统
- ✅ 实时日志流

## 技术栈

- FastAPI 0.104.1
- pyautogui 0.9.54
- opencv-python 4.8.1.78
- paddleocr 2.7.0.3
- pygetwindow 0.0.9

## 安装依赖

```bash
cd backend
pip install -r requirements.txt --break-system-packages
```

> 注意：如果使用系统 Python，加 `--break-system-packages` 参数

## 启动服务

```bash
# 方法1: 直接运行
python main.py

# 方法2: 使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后：
- API 服务：http://localhost:8000
- API 文档：http://localhost:8000/docs
- 前端地址：http://localhost:5173

## API 接口

### 流程管理

- `POST /api/flow/save` - 保存流程
- `GET /api/flow/load/{flow_id}` - 加载流程
- `POST /api/flow/export` - 导出 JSON
- `POST /api/flow/import` - 导入 JSON
- `POST /api/flow/execute` - 执行流程
- `POST /api/flow/stop` - 停止执行
- `POST /api/flow/package` - 打包 EXE

### 素材管理

- `POST /api/asset/upload` - 上传素材
- `DELETE /api/asset/{asset_id}` - 删除素材
- `GET /api/asset/list` - 获取素材列表

### 日志管理

- `GET /api/log/stream` - 实时日志流（SSE）
- `POST /api/log/clear` - 清空日志

## 项目结构

```
backend/
├── main.py                  # FastAPI 主程序
├── requirements.txt         # 依赖清单
├── actions/                 # 动作执行模块
│   ├── recognition.py       # 识别类（找图、OCR、找窗口）
│   ├── operation.py         # 操作类（点击、输入、拖拽）
│   ├── logic.py             # 逻辑类（条件、循环、等待）
│   └── data.py              # 数据类（变量、剪贴板）
├── utils/                   # 工具函数
│   ├── logger.py            # 日志处理
│   ├── image_match.py       # 图像匹配
│   └── window_manager.py    # 窗口管理
├── executor/                # 流程执行器
│   └── flow_executor.py     # 流程解析和执行
├── models/                  # 数据模型
│   └── schemas.py           # Pydantic 模型
└── storage/                 # 存储目录
    ├── flows/               # 流程文件
    └── assets/              # 素材文件
```

## 支持的节点类型

### 识别类（4种）
- 找图 - OpenCV 模板匹配
- 找文字(OCR) - PaddleOCR 文字识别
- 找窗口 - 根据标题查找窗口
- 颜色识别 - 检测指定位置颜色

### 操作类（9种）
- 点击 - 鼠标单击
- 双击 - 鼠标双击
- 拖拽 - 鼠标拖动
- 滚动 - 鼠标滚轮
- 输入文字 - 键盘输入
- 快捷键 - 组合键
- 启动程序 - 运行程序
- 激活窗口 - 激活指定窗口
- 关闭窗口 - 关闭指定窗口

### 逻辑类（3种）
- 等待 - 延时等待
- 条件判断 - if/else 分支
- 结束 - 结束流程

### 数据类（6种）
- 变量 - 设置/读取变量
- 复制 - 复制到剪贴板
- 粘贴 - 从剪贴板粘贴
- 弹窗提示 - 显示消息框
- 日志记录 - 记录日志
- 截图 - 屏幕截图

## 开发说明

### 添加新的节点类型

1. 在对应的 actions 模块中添加执行函数
2. 在 `flow_executor.py` 的 `ACTION_MAP` 中注册
3. 在前端的 `nodeTypes.js` 中添加节点配置

### 执行流程

1. 前端发送流程数据到 `/api/flow/execute`
2. 后端创建 `FlowExecutor` 实例
3. 从开始节点开始执行
4. 根据连接线查找下一个节点
5. 执行完成后返回日志

### 变量系统

变量存储在执行上下文（context）中：
```python
context = {
    'found': True,
    'position': (100, 200),
    'text_content': 'Hello'
}
```

使用赋值等式访问：
```python
# 直接赋值
'my_pos = position'  # my_pos = (100, 200)

# 拆解元组
'x, y = position'  # x = 100, y = 200

# 取索引
'x = position[0]'  # x = 100
```

## 注意事项

1. **安全性**：目前使用 `eval()` 执行表达式，生产环境需要更安全的方案
2. **权限**：图像识别和鼠标控制需要屏幕录制权限
3. **性能**：OCR 识别较慢，首次加载模型需要时间
4. **跨平台**：部分功能（如窗口管理）在不同系统表现不同

## 常见问题

### Q: OCR 识别失败？
A: 确保已安装 PaddleOCR 和 PaddlePaddle，首次使用会下载模型

### Q: 找图不准确？
A: 调整匹配精度参数（0.5-1.0），精度越高越严格

### Q: 无法控制鼠标键盘？
A: 检查系统权限设置，macOS 需要辅助功能权限

### Q: API 跨域错误？
A: 确保前端运行在 http://localhost:5173

## 许可证

MIT License

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