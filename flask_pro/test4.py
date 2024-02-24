from langchain.tools import DuckDuckGoSearchResults

search = DuckDuckGoSearchResults()

search.run("中国新闻")

try:
       print(search.run("中国新闻"))
except:
       pass