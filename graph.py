from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
import json
from tool import tools
from config import deepseek_api_key
from langchain_openai import ChatOpenAI
from state import State
# 配置语言模型 - 使用DeepSeek（兼容OpenAI API格式）
llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0,
    api_key=deepseek_api_key,
    base_url="https://api.deepseek.com/v1"
)



# 搜索工具
def search_tool(query):
    """网络搜索工具，使用Tavily搜索API"""
    try:
        # 使用TavilySearch工具执行搜索
        results = tools[0].invoke(query)

        # 构建搜索结果
        search_results = []
        search_results.append("搜索结果:")

        for i, result in enumerate(results[:3], 1):  # 只取前3个结果
            title = result.get('title', '无标题')
            snippet = result.get('snippet', '无描述')
            url = result.get('url', '无链接')
            search_results.append(f"{i}. {title}")
            search_results.append(f"   描述: {snippet}")
            search_results.append(f"   链接: {url}")
            search_results.append("")

        if not search_results:
            return f"未找到关于'{query}'的信息"

        return "\n".join(search_results)
    except Exception as e:
        return f"搜索失败: {str(e)}"


# 初始节点
def initialize_state(state):
    return {
        "messages": state.get("messages", []),
        "need_search": False,
        "search_query": "",
        "search_results": ""
    }


# 分析节点 - 判断是否需要搜索
def analyze_query(state):
    messages = state["messages"]

    # 构建分析提示
    prompt = f"""
    你是一个决策助手，需要判断用户的问题是否需要联网搜索来回答。

    请分析最后一条用户消息，如果问题涉及以下情况，请返回需要搜索：
    1. 最新的新闻、事件或数据
    2. 实时信息或当前状态
    3. 具体的事实性信息，如天气、股价、体育比赛结果等
    4. 可能随时间变化的信息

    如果问题是基于常识、历史事实或不需要实时信息的问题，则不需要搜索。

    用户消息: {messages[-1]["content"]}

    请返回JSON格式：
    {{
        "need_search": true/false,
        "search_query": "搜索关键词（如果需要搜索）"
    }}
    """

    response = llm.invoke(prompt)
    try:
        decision = json.loads(response.content)
        return {
            "need_search": decision.get("need_search", False),
            "search_query": decision.get("search_query", "")
        }
    except:
        return {"need_search": False, "search_query": ""}


# 搜索节点
def perform_search(state):
    if state["need_search"] and state["search_query"]:
        results = search_tool(state["search_query"])
        return {"search_results": results}
    return {"search_results": ""}


# 回答节点
def generate_answer(state):
    messages = state["messages"]
    search_results = state["search_results"]

    # 构建回答提示
    prompt = f"""
    请根据对话历史和搜索结果（如果有）回答用户的问题。

    对话历史：
    {"\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])}

    搜索结果：
    {search_results}

    请直接回答用户的问题，不要添加任何引言或开场白。
    """

    response = llm.invoke(prompt)
    return {"messages": add_messages(messages, [{"role": "assistant", "content": response.content}])}


# 条件路由
def route_decision(state):
    if state["need_search"]:
        return "search"
    return "answer"


# 构建图
def build_graph():
    graph = StateGraph(State)

    # 添加节点
    graph.add_node("initialize", initialize_state)
    graph.add_node("analyze", analyze_query)
    graph.add_node("search", perform_search)
    graph.add_node("answer", generate_answer)

    # 添加边
    graph.set_entry_point("initialize")
    graph.add_edge("initialize", "analyze")
    graph.add_conditional_edges("analyze", route_decision, {"search": "search", "answer": "answer"})
    graph.add_edge("search", "answer")
    graph.add_edge("answer", END)

    # 添加记忆
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


# 主对话循环
def main():
    print("=== LangGraph + ReAct 联网搜索问答机器人 ===")
    print("输入 'exit' 退出对话")

    # 构建图
    app = build_graph()

    # 对话ID
    thread_id = "user_session_1"

    while True:
        user_input = input("\n用户: ")

        if user_input.lower() == "exit":
            print("再见！")
            break

        # 运行图
        config = {"configurable": {"thread_id": thread_id}}
        result = app.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config
        )

        # 输出回答
        print(f"\n助手: {result['messages'][-1].content}")


if __name__ == "__main__":
    main()