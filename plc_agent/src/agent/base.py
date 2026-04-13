import os

from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

from ..graph.state import AgentState

load_dotenv()

api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
model_name = os.getenv("MODEL_NAME")

class BaseAgent:
    def __init__(self):
        self.name = "base"
        self.system_prompt = ""
        self.llm = init_chat_model(
            model=model_name,
            model_provider="openai",
            api_key=api_key,
            base_url=base_url,
        )
        self.tools = []

    def node(self, state: AgentState):
        print(f"开始调用{self.name}节点...")

        try:
            messages = []
            input_messages = state.get("messages", [])
            if self.system_prompt:
                messages.append(SystemMessage(content=self.system_prompt))

            messages.extend(input_messages)

            if self.tools:
                llm_with_tools = self.llm.bind_tools(self.tools)
                response = self.llm.invoke(messages)
            else:
                response = self.llm.invoke(messages)
            
            return {"messages": [response]}

        except Exception as e:
            print(f"节点{self.name}调用失败:{type(e).__name__}: {e}")
            return {
                "messages": [AIMessage(content=f"处理出错: {str(e)}")]
            }