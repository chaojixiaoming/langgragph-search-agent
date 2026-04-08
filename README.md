# LangGraph 智能搜索 Agent
基于 LangGraph + ReAct 框架实现的联网搜索问答机器人

## 功能
- 自动判断是否需要联网搜索
- 支持多轮对话记忆
- 条件路由决策
- 实时信息获取

## 技术栈
- LangGraph
- OpenAI GPT-3.5
- Tavily Search
- 记忆检测点

## 运行
pip install -r requirements.txt
python agent.py