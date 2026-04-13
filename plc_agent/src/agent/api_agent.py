from typing import List
from concurrent.futures import ThreadPoolExecutor
import json

from client import OpenAIClient, BM25RetrievalInstruction, ZhipuAIQAClient, ClientManager
from ..tool.api_loader import APIDataLoader
from ..log.logging_config import setup_logger

logger = setup_logger("api_agent")

class ApiAgent:
    
    @classmethod
    def run_filter_relevant_functions_group(
        cls,
        task: dict,
        funcions_json_list: List[dict],
        openai_client: OpenAIClient,
    ) -> List[str]:
        
        group_size = 15
        groups = [funcions_json_list[i:i+group_size] for i in range(0, len(funcions_json_list), group_size)]

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(cls.run_filter_relevant_functions, task, group, openai_client) for group in groups
            ]
            results = [future.result() for future in futures]

        merged_results = []
        for result in results:
            if isinstance(result, list):
                merged_results.extend(result)
            else:
                logger.warning("输出不是一个合法函数列表。")

        logger.info(f"筛选出{len(merged_results)}个相关函数。")
        return merged_results

    @classmethod
    def run_filter_relevant_functions(
        cls,
        task: dict,
        functions_json_list: List[dict],
        openai_client: OpenAIClient
    ) -> List[dict]:
        requirement = str(task)

        messages = [
            {"role": "system", "content": ""},
            {"role": "user", "content": ""}
        ]

        try:
            response = openai_client.call(messages)
            filtered = json.loads(response)

            if isinstance(filtered, list):
                logger.info(f"✅ Filtered {len(filtered)} relevant functions.")
                return filtered
            else:
                logger.warning("⚠️ Output is not a valid function list.")
                return []
            
        except Exception as e:
            logger.error(f"LLM推荐失败: {e}")

    @classmethod
    def run_recommend_api(
        cls,
        task: dict,
        openai_client: OpenAIClient,
        zhipuai_client: ZhipuAIQAClient,
        local_api_retrieval: BM25RetrievalInstruction,
    ) -> List[str]:
        
        basic_instructions = []

        basic_instructions += local_api_retrieval.query_multi_channel(task['description'])
        logger.info(f"检索到基础api: {basic_instructions}")

        if basic_instructions:
            basic_instructions_list = APIDataLoader.query_api_brief(basic_instructions)

            basic_instructions = cls.run_filter_relevant_functions_group(task, basic_instructions_list, openai_client)

            basic_instructions = list(set(basic_instructions))

            logger.info(f"推荐的基本指令：{basic_instructions}")

            return basic_instructions
        


if __name__ == "__main__":
    task = {"title": "FIFO First-In-First-Out Queue", "description": "Write a function block FB to implement the functionality of a First-In-First-Out (FIFO) circular queue, where the maximum length and data type of the queue are variable. The circular queue should support the following operations:\n\n1. Enqueue operation: Add an element to the end of the queue when the queue is not full.\n2. Dequeue operation: Remove an element from the front of the queue when the queue is not empty and return the value of that element.\n3. Check if the queue is empty: Check if there are no elements in the queue.\n4. Check if the queue is full: Check if the queue has reached its maximum capacity.\n5. Get the number of elements in the queue: Return the current number of elements in the queue.\nStatus codes:\n16#0000: Execution of FB without error\n16#8001: The queue is empty\n16#8002: The queue is full", "type": "FUNCTION_BLOCK", "name": "FIFO", "input": [{"name": "enqueue", "type": "Bool", "description": "Enqueue operation, add an element to the end of the queue when the queue is not full"}, {"name": "dequeue", "type": "Bool", "description": "Dequeue operation, remove an element from the front of the queue when the queue is not empty and return the value of that element."}, {"name": "reset", "type": "Bool", "description": "Reset operation, reset head and tail pointers, elementCount output is set to zero, and isEmpty output is set to TRUE."}, {"name": "clear", "type": "Bool", "description": "Clear operation, reset head and tail pointers, the queue will be cleared and initialized with the initial value initialItem. ElementCount output is set to zero, and isEmpty output is set to TRUE."}, {"name": "initialItem", "type": "Variant", "description": "The value used to initialize the queue"}], "output": [{"name": "error", "type": "Bool", "description": "FALSE: No error occurred TRUE: An error occurred during the execution of FB"}, {"name": "status", "type": "Word", "description": "Status code"}, {"name": "elementCount", "type": "DInt", "description": "The number of elements in the queue"}, {"name": "isEmpty", "type": "Bool", "description": "TRUE when the queue is empty"}], "in/out": [{"name": "item", "type": "Variant", "description": "The value used to add to the queue or return from the queue"}, {"name": "buffer", "type": "Variant", "description": "Used as an array for the queue"}], "status_codes": {"16#0000": "No error in execution of FB", "16#8001": "The queue is empty", "16#8002": "The queue is full"}}
    ClientManager()
    openai_client = ClientManager().get_openai_client
    zhipuai_client = ClientManager().get_zhipuai_client

    ApiAgent.run_recommend_api(task=task, openai_client=openai_client)