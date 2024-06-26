# -*- coding: utf-8 -*-
import asyncio
import json
import re
import ollama
from flask import Flask, Response, stream_with_context, request, render_template, jsonify, session
from werkzeug.utils import secure_filename
import time
from openai import OpenAI
import os
from dotenv import load_dotenv
import ast
from langchain_community.tools import DuckDuckGoSearchResults
from user_agents import parse
import requests

# import logging
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()
import sys
from io import StringIO
from datetime import datetime
from flask_socketio import SocketIO, emit

output = StringIO()
original_stdout = sys.stdout
app = Flask(__name__)
# app.logger.setLevel(logging.WARNING)
app.secret_key = 'secret_key'  # 用于启用 flash() 方法发送消息

# 示例的 Markdown 文本（包含图片链接）
# ![示例图片](/static/data.png "这是一个示例图片")
socketio = SocketIO(app, async_mode='threading')

search = DuckDuckGoSearchResults()
template_answer = {'给我画一个♥心形':
                       ["""
Let me do that now!
```python
import matplotlib.pyplot as plt
import numpy as np

# Parameters for the heart shape
t = np.linspace(0, 2 * np.pi, 1000)
x = 16 * np.sin(t) ** 3
y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)

# Plotting
plt.figure(figsize=(6,6))
plt.plot(x, y, 'r')
plt.fill(x, y, 'r')
plt.axis('equal')
plt.axis('off')
plt.show()
```
    """]
    , '最近西安有啥新闻': ["""
```python
search_internet("西安新闻2024")
```
"""]}

# normal_prompt = r"""
# You have a virtual environment equipped with a python environment. The python code you
# give will be automatically run by the system, so you can freely achieve your goals through python
# code. The code running results will be returned to you after the execution is completed. You can use
# python code to view all information about the current environment, or use matplotlib to draw charts.
# But note that if you want to get the value of a variable, please use print() to print it out; the
# variables in the code you give will be stored in the environment and can be called directly next
# time.
#
# Process upload file:
# User can upload file in location: .\uploads\
# You can use python code to read and process it.
#
# Finish tag:
# When you think no further reply needed, please add ```status_complete``` at the end of response, if you think further
# response is needed, please add ```status_running``` at the end of response.
#
# Writing Python:
# If you want to get the value of a variable, please use print() to print it out.
# """
normal_prompt = r"""
When you write a python code, please use ``` to cover your code, like:
```
code
```
You can response like following format to search news in internet:

```
search_internet('news in...')
```
用中文回答我，请用中文回答我，请用中文回答我
"""

judge_prompt = """You are a task completion judge. I will tell you the goal and current completion status of this task. 
You need to output whether it is completed now in json format. If it is completed, output {"complete":true}. If not, 
output {"complete":false} """


def chat_single_openai(messages, mode="json"):
    if mode == "json":

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type": "json_object"},
            messages=messages,
            stream=True,
            max_tokens=4096
        )
        return response
        # return response.choices[0].message.content
    else:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            stream=True,
            messages=messages,
            max_tokens=4096
        )
        return response


def chat_single(messages, a):
    response = ollama.chat(model='llama3', messages=messages, stream=True)
    return response


def search_internet(news):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def async_task():
        # 你的异步代码
        print(search.run(news))

    loop.run_until_complete(async_task())
    loop.close()


# async def async_task(news):
#     # 你的异步代码
#     print(search.run(news))
#
# def search_internet(news):
#     # 使用 eventlet 来 "模拟" 异步操作
#     pool = eventlet.GreenPool()
#     pool.spawn(async_task,news)
#     pool.waitall()
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


# html_content = markdown2.markdown(markdown_text)

def extract_code(code_str):
    code_str = code_str.replace('python', '')
    # if 'python' in code_str.split('\n')[0]:
    #     return code_str.split("```python")[1].split("```")[0]
    # else:
    return code_str.split("```")[1].split("```")[0]


def len_str2list(result):
    # result=result.replace("None","").replace(" ","")
    try:
        # 尝试使用 ast.literal_eval 解析字符串
        result = ast.literal_eval(result)
        # 检查解析结果是否为列表
        return len(result)
    except (ValueError, SyntaxError):
        # 如果解析时发生错误，说明字符串不是有效的列表字符串
        try:
            dict_result = json.loads(result)
            return len(dict_result)
        except:

            return len(result)


def judge_list(result):
    try:
        # 尝试使用 ast.literal_eval 解析字符串
        result = ast.literal_eval(result)
        # 检查解析结果是否为列表
        return True
    except (ValueError, SyntaxError):
        # 如果解析时发生错误，说明字符串不是有效的列表字符串
        return False


def details_span(result):
    aa = f"""
<details>
    <summary>`运行结果 (点击展开) Length:{len_str2list(result)}`</summary>
       {str(result)}
</details>
    """

    return aa


def short_response(text_list):
    if len(str(text_list)) > 1000 and judge_list(text_list):
        if len_str2list(text_list) < 40:
            result = ast.literal_eval(text_list)
            short_suitable_types = [t[:35] for t in result]
            return str(short_suitable_types)
        else:
            return text_list[:1000]
    else:
        return text_list[:1000]


# 设置文件上传的目录和大小限制
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xlsx', 'csv'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        session['uploaded_indication'] = filename
        return jsonify({"filename": filename}), 200
    else:
        return jsonify({"error": "File type not allowed"}), 400


@app.route('/submit_email', methods=['POST'])
def submit_email():
    data = request.get_json().get('text')
    with open("./static/email.text", 'a', encoding='utf-8') as file:
        file.write('\n' + json.dumps(
            {"email": data, "time": str(datetime.now()), "os": session['os'], "device": session['device_type'],
             'browser': session['browser']}))
    return jsonify({"text": True}), 400


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "The file is too large. Maximum file size is 50MB."}), 413


@app.route('/')
def home():
    # 加载包含 Markdown 容器的前端页面
    # session['globals_dict'] ={}
    # session['locals_dict'] = locals()
    print("初始化")
    ip_ = request.headers.get('X-Real-IP')
    # session['ip_']=ip_
    session['uploaded_indication'] = None
    # if 'messages2' not in session:
    #     session['messages2'] = []
    #     session['messages2'].append({"role": "system",
    #                                  "content": normal_prompt
    #                                  })
    user_agent_string = request.headers.get('User-Agent')
    if user_agent_string:
        user_agent = parse(user_agent_string)

        # 获取操作系统和浏览器信息
        os = user_agent.os.family  # 操作系统
        browser = user_agent.browser.family  # 浏览器
        if user_agent.is_mobile:
            device_type = 'Mobile'
        elif user_agent.is_tablet:
            device_type = 'Tablet'
        elif user_agent.is_pc:
            device_type = 'Desktop'
        else:
            device_type = 'Unknown'
        session['os'] = os
        session['browser'] = browser
        session['device_type'] = device_type
    else:
        session['os'] = None
        session['browser'] = None
        session['device_type'] = None
    session['uploaded_indication'] = None
    return render_template('index.html')


def send_data(data):
    # 假设这个函数在某些事件发生时被触发，并向所有客户端发送信息
    socketio.emit('text', {'data': data})


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    # 加载包含 Markdown 容器的前端页面
    data = request.get_json().get('text')  # 获取JSON数据
    messages = request.get_json().get('messages')  # 获取JSON数据
    processed_response = []
    print(len(messages))
    upload_index = session['uploaded_indication']

    def generate(data):

        compelete = False
        template = False
        steps = 0  # 纯文字返回最多两次
        whole_step = 0  # 总返回数,可以调整数值来限制未来的返回数
        true_step = 0  # 总返回数
        stop_step = False  # 强制该轮停止

        if "User upload a file in:" in data:
            chat_response = "文件上传完成！告诉我你想做什么？"
            compelete = True

            yield chat_response
        else:
            if upload_index != None:
                messages[0]['content'] += f"\n用户上传了文件，地址: .\\uploads\\{session['uploaded_indication']}"
                # data+=f".(用户上传的文件地址: .\\uploads\\{session['uploaded_indication']})"
            # session['messages2'].append({"role": "user",
            #                              "content": data})

        while compelete != True and steps < 2 and whole_step <= 5 and stop_step != True:
            # print(messages)
            print(whole_step, "whole_step")
            whole_step += 1
            true_step += 1
            # chat_response = str(datetime.now())+"   "+str(len(messages)) #test

            if data in template_answer and true_step == 1:
                chat_response = template_answer[data]
                template = True
                # stop_step=True
                # time.sleep(2)
            else:
                template = False

                chat_response = (chat_single(messages, ""))
            content_str = ''
            chat_result = ''
            chunk_num = 0
            if template:
                print(true_step, len(chat_response))

                for chunk in chat_response[true_step - 1]:
                    if chunk_num == 0:
                        char = "\n" + chunk
                        # char = "\n"+chunk #test
                    else:
                        char = chunk
                        # char =  chunk #test
                    chunk_num += 1
                    chat_result += char
                    time.sleep(0.001)
                    if true_step == 1:
                        template = False
                        # chat_response = (chat_single(messages, ""))
                        # stop_step=True

                    yield char
            else:
                for chunk in chat_response:
                    # if chunk is not None:
                    if chunk['message']['content'] is not None:
                        if chunk_num == 0:
                            # char = "\n"+chunk.choices[0].delta.content
                            char = "\n" + chunk['message']['content']
                            # char = "\n"+chunk #test
                        else:
                            char = chunk['message']['content']
                            # char =  chunk.choices[0].delta.content
                            # char =  chunk #test
                        chunk_num += 1

                        print(char, end="", flush=True)
                        chat_result += char

                        yield char
                    # try:
                    #     json_str = complete_json(chat_result)
                    #     new_content = json_str['content']
                    #     if new_content != content_str:
                    #         char_content = new_content[len(content_str):]
                    #         content_str = new_content
                    #         print(char_content, end="")
                    #
                    #         yield char_content
                    # except:
                    #     pass
            full_result = (chat_result)
            processed_response.append({'role': 'assistant', 'content': chat_result})
            messages.append({'role': 'assistant', 'content': chat_result})

            compelete = False
            print("complete: ", compelete)

            if "```" in full_result and ".env" not in full_result and "pip install" not in full_result:
                yield "\n\n`Code running...`\n"

                # code_str = re.sub(r'(?<!\\)\\n', r'\\\\n', extract_code(full_result['content']))
                code_str = extract_code(full_result)
                plt_show = False
                if "plt.show()" in code_str:
                    plt_show = True
                    print("plt_show")
                    filename = f"plot_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                    code_str = code_str.replace("import matplotlib.pyplot as plt",
                                                "import matplotlib.pyplot as plt\nfrom matplotlib.font_manager import FontProperties\nfont = FontProperties(fname=r'static\msyh.ttc')\n")
                    code_str = code_str.replace("plt.show()", f"plt.savefig('static/{filename}')")

                    print(code_str)
                else:
                    lines = code_str.strip().split('\n')
                    # last_line = [line for line in lines if '=' in line][-1]
                    if "print" not in lines[-1] and "=" not in lines[-1] and "#" not in lines[
                        -1] and "search_internet" not in lines[-1]:
                        code_str += f"""
try:
        print({lines[-1]})
except:
        pass
                            """
                    # var_name = last_line.split('=')[0].strip()
                print(code_str)
                sys.stdout = output
                try:
                    exec(code_str, globals())
                except Exception as e:
                    print(f"An error occurred: {repr(e)}")
                code_result = output.getvalue().replace('\00', '')
                output.truncate(0)
                sys.stdout = original_stdout

                if plt_show and "An error occurred: " not in code_result:
                    code_result = f'![matplotlib_diagram](/static/{filename} "matplotlib_diagram")'
                    whole_step = 5  # 确保图返回结果只会被描述一次
                    yield code_result
                else:
                    code_result = code_result

                    yield details_span(code_result)

                send_result = "code_result:" + short_response(code_result)
                print(send_result)
                messages.append({"role": "user",
                                 "content": send_result})
                processed_response.append({'role': 'user', 'content': send_result})
                compelete = False
                final_conv = send_result

            else:
                steps += 1
                if steps < 2 and whole_step < 5:
                    messages.append({"role": "user",
                                     "content": "ok"})
                    processed_response.append({"role": "user",
                                               "content": "ok"})
                    final_conv = 'ok'

        send_data(processed_response)
        data_with_response = {
            'len': str(len(messages)),
            'time': str(datetime.now()),
            # 'ip': str(session['ip_']),
            # 'location': query_ip_location(session['ip_']),
            'user': str(data),
            # 'os': str(session['os']),
            # 'browser': str(session['browser']),
            # 'device': str(session['device_type']),
            'answer': str(processed_response)
            # 'answer': response_str
        }

        formatted_data = json.dumps(data_with_response, indent=2, ensure_ascii=False)

        # 写入文本文件
        with open('static\data1.txt', 'a', encoding='utf-8') as file:
            file.write(formatted_data)

    return Response((generate(data)), content_type='application/octet-stream')


def query_ip_location(ip):
    try:
        ip = ip.replace(" ", "")
        url = f"http://ip-api.com/json/{ip}"  # 使用ip-api.com提供的API
        response = requests.get(url)
        data = json.loads(response.text)

        if data["status"] == "success":
            country = data["country"]
            city = data["city"]
            region = data["regionName"]
            isp = data["isp"]
            res = str(region + "  " + city + "  " + isp)
            return res
        else:
            return ip
    except:
        return ip


@app.route('/stream', methods=['POST', 'GET'])
def stream():
    # 生成逐字输出的HTML

    # data = request.get_json().get('text')  # 获取JSON数据
    # print(data)  # 输出查看，实际应用中你可能会做其他处理
    def generate():
        full_text = ''
        content_str = ""
        code_indicator = False
        for char in markdown_text:
            full_text += char
            yield char
            print(char, end="")
            time.sleep(0.001)
        # yield "\n```\n"
        # json_response=json.loads(full_text)
        # yield f"\n`{str(json_response['complete'])}`\n"
        # yield "json_response['complete']"
        if "```" in full_text:
            yield "\n\n`Code running...`\n"

            # code_str = re.sub(r'(?<!\\)\\n', r'\\\\n', extract_code(json_response['content']))
            code_str = extract_code(full_text)
            print(code_str, "code")
            plt_show = False
            if "plt.show()" in code_str:
                plt_show = True
                print("plt_show")

                filename = f"plot_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                code_str = code_str.replace("import matplotlib.pyplot as plt",
                                            "import matplotlib.pyplot as plt\nfrom matplotlib.font_manager import FontProperties\nfont = FontProperties(fname=r'static\msyh.ttc')\n")
                code_str = code_str.replace("plt.show()", f"plt.savefig('static/{filename}')")

            # elif "search.run" in code_str:
            #     code_str="search = DuckDuckGoSearchResults()\n"+code_str
            else:
                lines = code_str.strip().split('\n')
                # last_line = [line for line in lines if '=' in line][-1]
                if "print" not in lines[-1] and "=" not in lines[-1] and "#" not in lines[-1]:
                    # if "search.run" in code_str:
                    #     code_str=code_str.replace("search.run","print(search.run")+")"
                    # else:
                    code_str += f"""
try:
                   print({lines[-1]})
except:
                   pass
                                        """
                # var_name = last_line.split('=')[0].strip()
            print(code_str, "code_after_process")
            sys.stdout = output
            try:
                exec(code_str, globals())
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                print(f"An error occurred: {repr(e)}")
            code_result = output.getvalue().replace('\00', '')
            output.truncate(0)
            sys.stdout = original_stdout

            if plt_show and "An error occurred: " not in code_result:
                code_result = f'![matplotlib_diagram](/static/{filename} "matplotlib_diagram")'
                yield code_result
            else:
                code_result = code_result

                yield details_span(code_result)

    return Response(stream_with_context(generate()))


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True)
