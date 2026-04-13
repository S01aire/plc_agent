

from plc_agent.src.agent.client import ZhipuAIQAClient

model = ZhipuAIQAClient()

query = "输入一个变长 DInt 数组，输出最大值、最小值，以及它们各自的位置。"

print("test")
print(model.call_kbq(query=query, top_p=0.7))
