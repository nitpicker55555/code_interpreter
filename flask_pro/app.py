import json

from flask import Flask, Response, stream_with_context, request, render_template, flash, jsonify
from werkzeug.utils import secure_filename
import time
from openai import OpenAI
import os
from dotenv import load_dotenv
import ast
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()
import sys
from io import StringIO
from datetime import datetime

output = StringIO()
original_stdout = sys.stdout
app = Flask(__name__)

app.secret_key = 'secret_key' # 用于启用 flash() 方法发送消息

# 示例的 Markdown 文本（包含图片链接）
# ![示例图片](/static/data.png "这是一个示例图片")
import inspect
locals_dict = {}
globals_dict = globals()



markdown_text = """
要编写一个Python程序来读取一个文件夹（目录）中的所有文件和子目录
```python
import matplotlib.pyplot as plt
import numpy as np

# 参数方程
t = np.linspace(0, 2 * np.pi, 1000)
x = 16 * np.sin(t) ** 3
y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)

plt.figure(figsize=(8, 7))
plt.plot(x, y, color='red')
plt.title('Heart Shape')
plt.axis('equal')  # 确保长宽比相等，这样心形看起来才正确
plt.show()

```

"""

normal_prompt = r"""
You have a virtual environment equipped with a python environment. The python code you 
give will be automatically run by the system, so you can freely achieve your goals through python 
code. The code running results will be returned to you after the execution is completed. You can use 
python code to view all information about the current environment, or use matplotlib to draw charts. 
But note that if you want to get the value of a variable, please use print() to print it out; the 
variables in the code you give will be stored in the environment and can be called directly next 
time.

Process upload file:
User can upload file in location: .\uploads\
You can use python code to read and process it.

Response format: Please always response in json format like: { "content":"", "complete":false/true } "content" is the 
content of your response, "complete" represents whether you think the reply has been completed, if no more response 
needed please set "complete" as true, otherwise set it as false. """
judge_prompt="""You are a task completion judge. I will tell you the goal and current completion status of this task. 
You need to output whether it is completed now in json format. If it is completed, output {"complete":true}. If not, 
output {"complete":false} """


def chat_single(messages, mode="json"):
    if mode == "json":

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type": "json_object"},
            messages=messages,
            stream=True,
        max_tokens = 4096
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


messages2 = []
messages2.append({"role": "system",
                  "content": normal_prompt
                  })



# html_content = markdown2.markdown(markdown_text)

def extract_code(code_str):
    return code_str.split("```python")[1].split("```")[0]
def len_str2list(result):
    try:
        # 尝试使用 ast.literal_eval 解析字符串
        result = ast.literal_eval(result)
        # 检查解析结果是否为列表
        return len(result)
    except (ValueError, SyntaxError):
        # 如果解析时发生错误，说明字符串不是有效的列表字符串
        try:
            dict_result=json.loads(result)
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

    aa=f"""
<details>
    <summary>`Code result ▲ Length:{len_str2list(result)}`</summary>
       {str(result)}
</details>
    """

    return aa
def short_response(text_list):
    if len(str(text_list))>1000 and judge_list(text_list):
        if len_str2list(text_list)<40:
            result = ast.literal_eval(text_list)
            short_suitable_types = [t[:35] for t in result]
            return str(short_suitable_types)
        else:
            return text_list[:1000]
    else:
        return text_list[:1000]
# 设置文件上传的目录和大小限制
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg','doc','docx','xlsx','csv'}
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
        return jsonify({"filename": filename}), 200
    else:
        return jsonify({"error": "File type not allowed"}), 400

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "The file is too large. Maximum file size is 50MB."}), 413

@app.route('/')
def home():
    # 加载包含 Markdown 容器的前端页面
    return render_template('index.html')

def auto_json():
    pass
@app.route('/submit', methods=['POST', 'GET'])
def submit():
    # 加载包含 Markdown 容器的前端页面
    data = request.get_json().get('text')  # 获取JSON数据
    print(data)  # 输出查看，实际应用中你可能会做其他处理
    task=data




    def generate(data):

        messages2.append({"role": "user",
                          "content": data})
        compelete = False
        steps=0
        # while compelete!=True and steps<6:
        #     steps+=1

        while compelete!=True and steps<3:
            steps+=1
            chat_response = (chat_single(messages2, "json"))

            chat_result = ''
            for chunk in chat_response:
                if chunk.choices[0].delta.content is not None:
                    char = chunk.choices[0].delta.content
                    print(char, end="")
                    chat_result += char
                    yield char
            try:
                full_result=json.loads(chat_result)
            except:
                full_result=chat_result
            compelete=full_result['complete']
            print("complete: ",compelete)
            messages2.append({"role": "assistant",
                              "content": str(chat_result)})
            if "```python" in chat_result:
                yield "\n\n`Code running...`\n"

                code_str = extract_code(chat_result)
                plt_show = False
                if "plt.show()" in code_str:
                    plt_show = True
                    print("plt_show")
                    filename = f"plot_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                    code_str = code_str.replace("plt.show()", f"plt.savefig('static/{filename}')")
                    print(code_str)
                sys.stdout = output
                try:
                    exec(code_str, globals_dict)
                except Exception as e:
                    print(f"An error occurred: {e}")
                code_result = output.getvalue().replace('\00', '')
                output.truncate(0)
                sys.stdout = original_stdout

                if plt_show:
                    code_result = f'![matplotlib_diagram](/static/{filename} "matplotlib_diagram")'
                    yield code_result
                else:
                    code_result=code_result

                    yield details_span(code_result)

                send_result= "code_result:"+short_response(code_result)
                print(send_result)
            # messages2.append({"role": "user",
            #                   "content": send_result})
                generate(send_result)
        # else:
        #     messages_judge = []
        #     messages_judge.append({"role": "system",
        #                            "content": judge_prompt
        #                            })
        #     messages_judge.append({"role": "user",
        #                            "content": "Goal:" + task+" current_status:"+chat_result})
        #     chat_response = chat_single(messages_judge, "json")
        #     print(chat_response)
        #     yield f"\n`{chat_response}`\n"
                # try:
                #     judge = json.loads(chat_response)
                # except:
                #     judge = (chat_response)
                #
                # if "complete" in judge:
                #     if judge['complete']!=True:
                #         print("continue")
                #         messages2.append({"role": "user",
                #                           "content": "continue"})
                #     else:
                #         compelete=True
                # else:
                #     compelete = True

            # print("code_result: ",code_result)
            # messages2.append({"role": "user",
            #                   "content": send_result})
            # chat_response_code = (chat_single(messages2, ""))
            # chat_result = ''
            # for chunk in chat_response_code:
            #     if chunk.choices[0].delta.content is not None:
            #         char = chunk.choices[0].delta.content
            #         print(char, end="")
            #         chat_result += char
            #         yield char
            # messages2.append({"role": "assistant",
            #                   "content": chat_result})

    return Response(stream_with_context(generate(data)))


@app.route('/stream', methods=['POST', 'GET'])
def stream():
    # 生成逐字输出的HTML

    # data = request.get_json().get('text')  # 获取JSON数据
    # print(data)  # 输出查看，实际应用中你可能会做其他处理
    def generate():
        full_text = ''
        for char in markdown_text:
            full_text += char
            yield char
            time.sleep(0.001)  # 减小这个值以提高响应速度
        if "```python" in full_text:
            yield "\n\n`Code running...`\n"

            code_str = extract_code(full_text)
            plt_show = False
            if "plt.show()" in code_str:
                plt_show = True
                print("plt_show")
                filename = f"plot_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                code_str = code_str.replace("plt.show()", f"plt.savefig('static/{filename}')")
                print(code_str)
            sys.stdout = output
            try:
                exec(code_str, globals_dict)
            except Exception as e:
                print(f"An error occurred: {e}")
            code_result = output.getvalue().replace('\00', '')
            output.truncate(0)
            sys.stdout = original_stdout

            if plt_show:
                code_result = f'![matplotlib_diagram](/static/{filename} "matplotlib_diagram")'
                yield code_result
            else:
                code_result = code_result

                yield details_span(code_result)

    return Response(stream_with_context(generate()))


if __name__ == '__main__':
    app.run(debug=True)
