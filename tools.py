from langchain_community.tools.tavily_search import TavilySearchResults

# 联网搜索工具
search_tool = TavilySearchResults(max_results=2)
tools = [search_tool]