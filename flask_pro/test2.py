chat_result="""
```python
soil_types = list_type_of_graph_name("http://example.com/soil")
print(soil_types)

```
"""
chat2="""
```python
import pandas as pd

# 读取上传的CSV文件
file_path = './uploads/risk.csv'
data = pd.read_csv(file_path)
correlation = data.corr()
data = data.replace(',', '', regex=True)
data = data.apply(pd.to_numeric, errors='coerce')

# 重新计算不同列之间的相关性
correlation = data.corr()
import matplotlib.pyplot as plt
import seaborn as sns

# 绘制热图
plt.figure(figsize=(12, 10))
heatmap = sns.heatmap(correlation, annot=True, cmap="YlGnBu")
plt.title('Correlation Heatmap')
plt.show()
```
"""
chat3="""
```python
id_list1=list_id_of_type("http://example.com/buildings","building")
print(id_list1)
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
functions_dict = {name: obj for name, obj in globals_dict.items() if inspect.isfunction(obj)}
def main(chat_result):
    def extract_code(code_str):
        return code_str.split("```python")[1].split("```")[0]
    code_str=extract_code(chat_result)
    plt_show=False
    if "plt.show()" in code_str:
        plt_show=True
        print("plt_show")
        code_str=code_str.replace("plt.show()","plt.savefig('static/mat.png')")
    sys.stdout = output
    try:
        exec(code_str, functions_dict)
    except Exception as e:
        print(f"An error occurred: {e}")

    code_result = output.getvalue().replace('\00', '')
    output.truncate(0)
    sys.stdout = original_stdout
    if chat_result==chat2:

        print(code_result[:20])


    print(len((code_result)))
# main(chat_result)
# main(chat2)
main(chat2)
# chat_response='{"complete":false}'
# try:
#     judge = json.loads(chat_response)
# except:
#     judge = (chat_response)
#
# if "complete" in judge:
#     if judge['complete'] != True:
#         print("Continue")