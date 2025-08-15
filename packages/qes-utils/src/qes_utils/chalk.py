from simple_chalk import chalk, green

# 支持的颜色映射
SUPPORTED_COLORS = {
    'red': chalk.red,
    'green': chalk.green,
    'blue': chalk.blue,
    'yellow': chalk.yellow,
    'cyan': chalk.cyan,
    'magenta': chalk.magenta,
    'white': chalk.white,
    'black': chalk.black,
    'gray': chalk.gray,
    'grey': chalk.gray,
}


def print_colorfully(text: str, color: str = 'green') -> str:
    """
    Prints the given text in the specified color using chalk.

    Args:
        text (str): The text to colorize
        color (str): The color name (e.g., 'red', 'blue', 'yellow', 'green', 'cyan', 'magenta')

    Returns:
        str: The colorized text string
    """
    if text is None or text == '':
        return ''

    try:
        # 使用字典映射动态获取颜色方法
        color_func = SUPPORTED_COLORS.get(color.lower())
        if color_func is None:
            # 如果颜色不存在，使用默认绿色
            print(
                f"Warning: Color '{color}' not found, using default green. Supported colors: {list(SUPPORTED_COLORS.keys())}")
            color_func = chalk.green
        return color_func(text)
    except Exception as e:
        # 异常处理，返回原始文本
        print(f"Error applying color '{color}': {e}")
        return text

# 常用颜色的便捷函数


def print_success(text: str, **kwargs) -> str:
    """打印成功信息（绿色）"""
    return print(print_colorfully(text, 'green'), **kwargs)


def print_error(text: str) -> str:
    """打印错误信息（红色）"""
    return print_colorfully(text, 'red')


def print_warning(text: str) -> str:
    """打印警告信息（黄色）"""
    return print_colorfully(text, 'yellow')


def print_info(text: str) -> str:
    """打印信息（蓝色）"""
    return print_colorfully(text, 'blue')
