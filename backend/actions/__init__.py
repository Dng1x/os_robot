"""
动作执行模块包
"""
from actions.recognition import (
    execute_find_image,
    execute_find_text,
    execute_find_window,
    execute_check_color
)
from actions.operation import (
    execute_click,
    execute_double_click,
    execute_drag,
    execute_scroll,
    execute_type_text,
    execute_hotkey,
    execute_launch_program,
    execute_activate_window,
    execute_close_window
)
from actions.logic import (
    execute_wait,
    execute_condition,
    execute_end
)
from actions.data import (
    execute_variable,
    execute_clipboard_copy,
    execute_clipboard_paste,
    execute_message_box,
    execute_log,
    execute_screenshot
)

__all__ = [
    # Recognition
    'execute_find_image',
    'execute_find_text',
    'execute_find_window',
    'execute_check_color',
    # Operation
    'execute_click',
    'execute_double_click',
    'execute_drag',
    'execute_scroll',
    'execute_type_text',
    'execute_hotkey',
    'execute_launch_program',
    'execute_activate_window',
    'execute_close_window',
    # Logic
    'execute_wait',
    'execute_condition',
    'execute_end',
    # Data
    'execute_variable',
    'execute_clipboard_copy',
    'execute_clipboard_paste',
    'execute_message_box',
    'execute_log',
    'execute_screenshot'
]
