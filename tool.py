from langchain_tavily import TavilySearch
from config import tavily_api_key

# 配置搜索工具
tavily_search = TavilySearch(max_results=2, tavily_api_key=tavily_api_key)
tools = [tavily_search]