# 定义状态结构
class State:
    messages: list
    need_search: bool
    search_query: str
    search_results: str
    should_exit: bool