from typing import Literal
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from state import AgentState
from tools import tools

# ----------------------
# 国内模型：使用免费开源模型
# ----------------------
model_name = "Qwen/Qwen-1.8B-Chat"  # 阿里通义千问开源版
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    trust_remote_code=True,
    device_map="auto"
)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=512,
    temperature=0.1
)

llm = HuggingFacePipeline(pipeline=pipe)
llm_with_tools = llm.bind_tools(tools)

# ----------------------
# AI 节点
# ----------------------
def agent_node(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# ----------------------
# 路由判断
# ----------------------
def should_continue(state: AgentState) -> Literal["call_tool", "__end__"]:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "call_tool"
    return END

# ----------------------
# 构建流程图
# ----------------------
def build_agent():
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("call_tool", ToolNode(tools))
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("call_tool", "agent")
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

# ----------------------
# 运行
# ----------------------
if __name__ == "__main__":
    agent = build_agent()
    config = {"configurable": {"thread_id": "session-1"}}

    print("国内模型智能搜索 Agent 已启动（输入 exit 退出）")
    while True:
        user_input = input("你：")
        if user_input.lower() == "exit":
            break
        result = agent.invoke(
            {"messages": [("user", user_input)]},
            config=config
        )
        print("AI：", result["messages"][-1].content)