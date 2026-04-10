import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取DeepSeek API密钥
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
if not deepseek_api_key or deepseek_api_key == "请输入您的DeepSeek API密钥":
    print("错误: 请在.env文件中设置DeepSeek API密钥")
    print("您可以在 https://platform.deepseek.com/ 申请API密钥")
    exit(1)

# 获取Tavily API密钥
tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key or tavily_api_key == "请输入您的Tavily API密钥":
    print("错误: 请在.env文件中设置Tavily API密钥")
    print("您可以在 https://tavily.com/ 申请API密钥")
    exit(1)
#