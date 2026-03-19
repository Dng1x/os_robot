// 积木块类别定义
export const NODE_CATEGORIES = {
  trigger: { id: 'trigger', name: '触发类', color: '#ff6b6b' },
  recognition: { id: 'recognition', name: '识别类', color: '#4c6ef5' },
  operation: { id: 'operation', name: '操作类', color: '#51cf66' },
  logic: { id: 'logic', name: '逻辑类', color: '#ffa94d' },
  data: { id: 'data', name: '数据类', color: '#a78bfa' },
  auxiliary: { id: 'auxiliary', name: '辅助类', color: '#06b6d4' }
};

// 积木块类型定义
export const NODE_TYPES_CONFIG = [
  // 触发类
  {
    id: 'start',
    category: 'trigger',
    name: '开始',
    icon: '▶',
    description: '流程的起点',
    params: [
    ],
    outputs: ['next']
  },
  {
    id: 'timer_trigger',
    category: 'trigger',
    name: '定时触发',
    icon: '⏰',
    description: '按时间间隔触发',
    params: [
      { name: 'interval', label: '间隔时间(秒)', type: 'number', default: 60 },
      { name: 'repeat', label: '重复次数', type: 'number', default: 0, help: '0表示无限' }
    ],
    outputs: ['next']
  },
  {
    id: 'file_watch',
    category: 'trigger',
    name: '文件监听',
    icon: '📁',
    description: '监听文件变化',
    params: [
      { name: 'path', label: '监听路径', type: 'text', default: '' },
      { name: 'pattern', label: '文件模式', type: 'text', default: '*.*' }
    ],
    outputs: ['next']
  },

  // 识别类
  {
    id: 'find_image',
    category: 'recognition',
    name: '找图',
    icon: '🖼',
    description: '在屏幕上查找图片',
    params: [
      { name: 'image', label: '目标图片', type: 'image', required: true },
      { name: 'confidence', label: '匹配精度', type: 'slider', default: 0.8, min: 0.5, max: 1.0, step: 0.05 },
      { name: 'region', label: '搜索区域', type: 'region', default: null },
      { name: 'timeout', label: '超时时间(秒)', type: 'number', default: 5 },
    ],
    outputs: ['success', 'failure'],
    variables: [
      { name: 'found', type: 'bool', description: '是否找到图片（True/False）' },
      { name: 'position', type: 'tuple', description: '图片中心坐标 (x, y)，未找到时为None' }
    ],
    outputHint: '输出说明：找到→成功出口(found=True)，未找到→失败出口(found=False)。可用连线区分或用变量判断'
  },
  {
    id: 'find_text',
    category: 'recognition',
    name: '找文字(OCR)',
    icon: '📝',
    description: '识别屏幕上的文字',
    params: [
      { name: 'text', label: '目标文字', type: 'text', required: true },
      { name: 'region', label: '识别区域', type: 'region', default: null },
      { name: 'language', label: '语言', type: 'select', options: ['中文', '英文', '中英混合'], default: '中英混合' }
    ],
    outputs: ['success', 'failure'],
    variables: [
      { name: 'found', type: 'bool', description: '是否找到文字（True/False）' },
      { name: 'position', type: 'tuple', description: '文字中心坐标 (x, y)' },
      { name: 'text_content', type: 'string', description: '识别到的完整文字内容' }
    ],
    outputHint: '输出变量：found (布尔), position (坐标), text_content (字符串)\n使用示例：is_found = found, text_pos = position, content = text_content'
  },
  {
    id: 'find_window',
    category: 'recognition',
    name: '找窗口',
    icon: '🪟',
    description: '根据标题查找窗口',
    params: [
      { name: 'title', label: '窗口标题', type: 'text', required: true },
      { name: 'match_mode', label: '匹配模式', type: 'select', options: ['完全匹配', '包含', '正则'], default: '包含' }
    ],
    outputs: ['success', 'failure'],
    variables: [
      { name: 'found', type: 'bool', description: '是否找到窗口（True/False）' },
      { name: 'window_handle', type: 'object', description: '窗口句柄对象' }
    ],
    outputHint: '输出变量：found (布尔), window_handle (窗口对象)\n使用示例：win_found = found, win = window_handle'
  },
  {
    id: 'check_color',
    category: 'recognition',
    name: '颜色识别',
    icon: '🎨',
    description: '检测指定位置的颜色',
    params: [
      { name: 'position', label: '检测位置', type: 'position', required: true },
      { name: 'color', label: '目标颜色', type: 'color', default: '#FF0000' },
      { name: 'tolerance', label: '容差', type: 'number', default: 10, min: 0, max: 255 }
    ],
    outputs: ['success', 'failure'],
    variables: [
      { name: 'matched', type: 'bool', description: '颜色是否匹配（True/False）' },
      { name: 'actual_color', type: 'string', description: '实际检测到的颜色值 (如 #FF5533)' }
    ],
    outputHint: '输出变量：matched (布尔), actual_color (颜色字符串)\n使用示例：color_match = matched, detected = actual_color'
  },

  // 操作类
  {
    id: 'click',
    category: 'operation',
    name: '点击',
    icon: '👆',
    description: '鼠标单击',
    params: [
      { name: 'position_type', label: '位置类型', type: 'select', options: ['使用变量', '固定坐标'], default: '使用变量' },
      { name: 'position_var', label: '位置变量', type: 'text', default: 'position', help: '前一节点输出的位置变量名' },
      { name: 'offset_x', label: 'X偏移', type: 'number', default: 0, help: '相对偏移量（像素）' },
      { name: 'offset_y', label: 'Y偏移', type: 'number', default: 0, help: '相对偏移量（像素）' },
      { name: 'fixed_x', label: '固定X坐标', type: 'number', default: 0, help: '仅固定坐标模式有效' },
      { name: 'fixed_y', label: '固定Y坐标', type: 'number', default: 0, help: '仅固定坐标模式有效' },
      { name: 'button', label: '按钮', type: 'select', options: ['左键', '右键', '中键'], default: '左键' },
      { name: 'clicks', label: '点击次数', type: 'number', default: 1 }
    ],
    outputs: ['next']
  },
  {
    id: 'double_click',
    category: 'operation',
    name: '双击',
    icon: '👆👆',
    description: '鼠标双击',
    params: [
      { name: 'position_type', label: '位置类型', type: 'select', options: ['使用变量', '固定坐标'], default: '使用变量' },
      { name: 'position_var', label: '位置变量', type: 'text', default: 'position', help: '前一节点输出的位置变量名' },
      { name: 'offset_x', label: 'X偏移', type: 'number', default: 0 },
      { name: 'offset_y', label: 'Y偏移', type: 'number', default: 0 },
      { name: 'fixed_x', label: '固定X坐标', type: 'number', default: 0, help: '仅固定坐标模式有效' },
      { name: 'fixed_y', label: '固定Y坐标', type: 'number', default: 0, help: '仅固定坐标模式有效' }
    ],
    outputs: ['next']
  },
  {
    id: 'drag',
    category: 'operation',
    name: '拖拽',
    icon: '✊',
    description: '拖动鼠标',
    params: [
      { name: 'from_type', label: '起点类型', type: 'select', options: ['使用变量', '固定坐标'], default: '使用变量' },
      { name: 'from_var', label: '起点变量', type: 'text', default: 'position' },
      { name: 'from_x', label: '起点X', type: 'number', default: 0, help: '仅固定坐标模式' },
      { name: 'from_y', label: '起点Y', type: 'number', default: 0, help: '仅固定坐标模式' },
      { name: 'to_type', label: '终点类型', type: 'select', options: ['使用变量', '固定坐标', '相对偏移'], default: '固定坐标' },
      { name: 'to_var', label: '终点变量', type: 'text', default: '' },
      { name: 'to_x', label: '终点X/X偏移', type: 'number', default: 0 },
      { name: 'to_y', label: '终点Y/Y偏移', type: 'number', default: 0 },
      { name: 'duration', label: '持续时间(秒)', type: 'number', default: 0.5 }
    ],
    outputs: ['next']
  },
  {
    id: 'scroll',
    category: 'operation',
    name: '滚动',
    icon: '📜',
    description: '滚动鼠标滚轮',
    params: [
      { name: 'direction', label: '方向', type: 'select', options: ['向上', '向下'], default: '向下' },
      { name: 'amount', label: '滚动量', type: 'number', default: 200 }
    ],
    outputs: ['next']
  },
  {
    id: 'type_text',
    category: 'operation',
    name: '输入文字',
    icon: '⌨',
    description: '键盘输入文字',
    params: [
      { name: 'text', label: '输入内容', type: 'text', required: true },
      { name: 'interval', label: '输入间隔(秒)', type: 'number', default: 0.05 }
    ],
    outputs: ['next']
  },
  {
    id: 'hotkey',
    category: 'operation',
    name: '快捷键',
    icon: '⌘',
    description: '执行快捷键',
    params: [
      { name: 'keys', label: '按键组合', type: 'text', required: true, help: '如: ctrl+c' }
    ],
    outputs: ['next']
  },
  {
    id: 'launch_program',
    category: 'operation',
    name: '启动程序',
    icon: '🚀',
    description: '运行程序',
    params: [
      { name: 'path', label: '程序路径', type: 'file', required: true },
      { name: 'args', label: '启动参数', type: 'text', default: '' }
    ],
    outputs: ['next']
  },
  {
    id: 'activate_window',
    category: 'operation',
    name: '激活窗口',
    icon: '🔼',
    description: '将窗口调到前台',
    params: [
      { name: 'window', label: '窗口', type: 'text', help: '窗口标题或句柄变量' }
    ],
    outputs: ['next']
  },
  {
    id: 'close_window',
    category: 'operation',
    name: '关闭窗口',
    icon: '❌',
    description: '关闭指定窗口',
    params: [
      { name: 'window', label: '窗口', type: 'text' }
    ],
    outputs: ['next']
  },

  // 逻辑类
  {
    id: 'condition',
    category: 'logic',
    name: '条件判断',
    icon: '❓',
    description: '根据条件分支',
    params: [
      { name: 'condition', label: '条件', type: 'text', required: true, help: '如: {变量名} == "值"' }
    ],
    outputs: ['true', 'false']
  },
  {
    id: 'loop_fixed',
    category: 'logic',
    name: '重复N次',
    icon: '🔁',
    description: '固定次数循环',
    params: [
      { name: 'count', label: '重复次数', type: 'number', required: true, default: 10 }
    ],
    outputs: ['loop_body', 'next']
  },
  {
    id: 'loop_while',
    category: 'logic',
    name: '重复直到',
    icon: '🔄',
    description: '条件循环',
    params: [
      { name: 'condition', label: '终止条件', type: 'text', required: true }
    ],
    outputs: ['loop_body', 'next']
  },
  {
    id: 'loop_foreach',
    category: 'logic',
    name: '遍历列表',
    icon: '📋',
    description: '逐项处理',
    params: [
      { name: 'items', label: '数据源', type: 'text', required: true, help: '变量名或列表' }
    ],
    outputs: ['loop_body', 'next'],
    variables: ['item', 'index']
  },
  {
    id: 'wait',
    category: 'logic',
    name: '等待',
    icon: '⏱',
    description: '暂停执行',
    params: [
      { name: 'duration', label: '等待时间(秒)', type: 'number', required: true, default: 1 }
    ],
    outputs: ['next']
  },
  {
    id: 'retry',
    category: 'logic',
    name: '重试',
    icon: '🔃',
    description: '失败后重试',
    params: [
      { name: 'max_attempts', label: '最大次数', type: 'number', default: 3 },
      { name: 'interval', label: '间隔时间(秒)', type: 'number', default: 1 }
    ],
    outputs: ['retry_body', 'success', 'failure']
  },
  {
    id: 'try_catch',
    category: 'logic',
    name: '异常处理',
    icon: '🛡',
    description: '捕获异常',
    params: [
    ],
    outputs: ['try_body', 'catch_body', 'next']
  },
  {
    id: 'end',
    category: 'logic',
    name: '结束',
    icon: '⏹',
    description: '结束流程',
    params: [],
    outputs: []
  },

  // 数据类
  {
    id: 'variable',
    category: 'data',
    name: '变量',
    icon: '💾',
    description: '存取变量',
    params: [
      { name: 'mode', label: '模式', type: 'select', options: ['设置变量', '读取变量'], default: '设置变量' },
      { name: 'assignment', label: '赋值等式', type: 'textarea', required: true, help: '示例：my_pos = position 或 x_coord = position[0]', placeholder: '新变量名 = 源变量名' },
      { name: 'read_var', label: '读取变量名', type: 'text', default: '', help: '要读取的变量名（仅读取模式）' }
    ],
    outputs: ['next'],
    outputHint: '赋值示例：\n• click_pos = position （直接赋值）\n• x = position[0] （取坐标X）\n• y = position[1] （取坐标Y）\n• result = found （取布尔值）'
  },
  {
    id: 'clipboard_copy',
    category: 'data',
    name: '复制',
    icon: '📋',
    description: '复制到剪贴板',
    params: [
      { name: 'content', label: '内容', type: 'text', required: true }
    ],
    outputs: ['next']
  },
  {
    id: 'clipboard_paste',
    category: 'data',
    name: '粘贴',
    icon: '📄',
    description: '从剪贴板粘贴',
    params: [
    ],
    outputs: ['next'],
    variables: [
      { name: 'clipboard_content', type: 'string', description: '剪贴板中的文本内容' }
    ],
    outputHint: '输出变量：clipboard_content (字符串)\n使用示例：paste_text = clipboard_content'
  },
  {
    id: 'string_process',
    category: 'data',
    name: '字符串处理',
    icon: '✂',
    description: '处理文本',
    params: [
      { name: 'operation', label: '操作', type: 'select', options: ['拼接', '截取', '替换', '分割'], default: '拼接' },
      { name: 'input', label: '输入文本', type: 'text', required: true },
      { name: 'param', label: '参数', type: 'text', default: '' }
    ],
    outputs: ['next'],
    variables: ['result']
  },

  // 辅助类
  {
    id: 'message_box',
    category: 'auxiliary',
    name: '弹窗提示',
    icon: '💬',
    description: '显示消息框',
    params: [
      { name: 'message', label: '提示内容', type: 'text', required: true },
      { name: 'title', label: '标题', type: 'text', default: '提示' }
    ],
    outputs: ['next']
  },
  {
    id: 'log',
    category: 'auxiliary',
    name: '日志记录',
    icon: '📊',
    description: '记录日志',
    params: [
      { name: 'message', label: '日志内容', type: 'text', required: true },
      { name: 'level', label: '级别', type: 'select', options: ['信息', '警告', '错误'], default: '信息' }
    ],
    outputs: ['next']
  },
  {
    id: 'screenshot',
    category: 'auxiliary',
    name: '截图',
    icon: '📷',
    description: '保存截图',
    params: [
      { name: 'path', label: '保存路径', type: 'text', required: true },
      { name: 'region', label: '截图区域', type: 'region', default: null }
    ],
    outputs: ['next']
  }
];

// 连接线类型
export const EDGE_TYPES = {
  NORMAL: 'default',
  SUCCESS: 'success',
  FAILURE: 'failure',
  LOOP: 'loop'
};

// 连接线样式配置
export const EDGE_STYLES = {
  success: {
    stroke: '#51cf66',
    strokeWidth: 2,
    strokeDasharray: '5,5'
  },
  failure: {
    stroke: '#ff6b6b',
    strokeWidth: 2,
    strokeDasharray: '5,5'
  },
  loop: {
    stroke: '#4a90e2',
    strokeWidth: 2
  },
  default: {
    stroke: '#b1b1b7',
    strokeWidth: 2
  }
};
