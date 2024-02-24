import json

def complete_json(input_stream):
    """
    尝试补全一个不完整的JSON字符串，包括双引号和括号。

    参数:
    - input_stream: 一个可能不完整的JSON字符串

    返回:
    - 完整的JSON对象
    """
    brackets = {'{': '}', '[': ']'}
    quotes = {'"': '"'}
    stack = []
    in_string = False

    # 尝试解析JSON，如果失败则补全
    try:
        return json.loads(input_stream)
    except json.JSONDecodeError:
        pass  # 继续到补全逻辑

    # 逐字符遍历输入字符串
    for char in input_stream:
        if char in quotes and not in_string:
            # 进入字符串
            in_string = True
            stack.append(quotes[char])
        elif char in quotes and in_string:
            # 结束字符串
            in_string = False
            stack.pop()
        elif char in brackets and not in_string:
            # 进入对象或数组
            stack.append(brackets[char])
        elif stack and char == stack[-1] and not in_string:
            # 退出对象或数组
            stack.pop()

    # 补全字符串
    if in_string:
        input_stream += '"'
        stack.pop()

    # 根据栈中剩余的括号补全JSON
    while stack:
        input_stream += stack.pop()

    # 再次尝试解析补全后的JSON
    return json.loads(input_stream)
# # 示例输入
# input_json = '{ "content":"as'
#
# # 调用函数并打印结果
# completed_json = complete_json(input_json)
# print(completed_json)
import re

# 示例字符串
text =r"这是一个示例字符串，其中包含\\n已经被转义的换行符，和\n未被转义的换行符。"

# 正则表达式替换
# 使用负向前瞻断言来确保\n前面不是\
# (?<!\\) 是一个负向前瞻断言，确保\n前面不是反斜杠
# \n 是匹配换行符
# 替换为 \\n
replaced_text = re.sub(r'(?<!\\)\\n', r'\\\\n', text)

print(replaced_text)

#
# markdown_text = """
# {
#   "description": "示例代码，展示如何在处理JSON数据时在每个键和值之间添加换行，用于打印或显示目的。",
#   "code": "
#
# """
#
# print(complete_json(markdown_text))