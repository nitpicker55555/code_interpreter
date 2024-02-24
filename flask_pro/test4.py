chat3 = """
```python
import pandas as pd
import matplotlib.pyplot as plt

# Read the data from the Excel file
file_path = './uploads/bitcoin_trend.xlsx'
data = pd.read_excel(file_path)
# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(data['Date'], data['Price'], marker='o', linestyle='-')
plt.title('Bitcoin Price Trend')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()
```
"""


def extract_code(code_str):
    return code_str.split("```python")[1].split("```")[0]
exec(extract_code(chat3))