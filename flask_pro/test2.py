import json
import re

from flask import Flask, Response, stream_with_context, request, render_template, flash, jsonify,session
from werkzeug.utils import secure_filename
import time
from openai import OpenAI
import os
from dotenv import load_dotenv
import ast
from langchain.tools import DuckDuckGoSearchResults

search = DuckDuckGoSearchResults()
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

chat_result="""
```python
soil_types = list_type_of_graph_name("http://example.com/soil")
print(soil_types)

```
"""
chat2="""
```python
import pandas as pd

# Read the Excel file
file_path = './uploads/bitcoin_trend.xlsx'
data = pd.read_excel(file_path)
data
```
"""
chat3="""
```python

search.run("中国新闻")



```
"""
import ast


import inspect
import sys
from io import StringIO
locals_dict = {}
globals_dict = globals()
output = StringIO()
original_stdout = sys.stdout

# 筛选出所有的函数
functions_dict = {}
def main(chat_result):
    def extract_code(code_str):
        return code_str.split("```python")[1].split("```")[0]
    code_str=extract_code(chat_result)
    plt_show=False
    if "plt.show()" in code_str:
        plt_show = True
        print("plt_show")
        filename = f"plot_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        # code_str = code_str.replace("plt.show()", "plt.draw()")
        # code_str+=f"plt.savefig('static/{filename}')"

        # print(code_str)
    else:
        lines = code_str.strip().split('\n')
        # last_line = [line for line in lines if '=' in line][-1]
        if "print" not in lines[-1] and "=" not in lines[-1]:
            code_str += f"""
try:
        print({lines[-1]})
except:
        pass
            """
    print(code_str)
    sys.stdout = output
    try:
        exec(code_str, globals())
    except Exception as e:
        # print(traceback.print_exc())
        print(f"An error occurred: {repr(e)}")
    code_result = output.getvalue().replace('\00', '')
    output.truncate(0)
    sys.stdout = original_stdout
    print(code_result)
    if chat_result==chat2:

        print(code_result)


    # print(len((code_result)))
# main(chat_result)
# main(chat2)
# main(chat2)
main(chat3)
# chat_response='{"complete":false}'
# try:
#     judge = json.loads(chat_response)
# except:
#     judge = (chat_response)
#
# if "complete" in judge:
#     if judge['complete'] != True:
#         print("Continue")