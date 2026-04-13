import os
from typing import List
import json

import requests
from dotenv import load_dotenv
import jieba
import rank_bm25
from rank_bm25 import BM25Okapi
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

from plc_agent.src.core.config_loader import (
    get_config,
    get_settings,
)
from plc_agent.src.core.models import (
    LLMConfig,
    RAGConfig,
    LocalRetrievalConfig,
)

load_dotenv()

url = "https://open.bigmodel.cn/api/llm-application/open/knowledge/retrieve"
api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
llm_model = os.getenv("MODEL_NAME")
knowledge_id = os.getenv("ST_CASE_KNOWLEDGE_ID")

settings = get_settings()

class OpenAIClient:
    def __init__(self, config: LLMConfig):
        self.client = OpenAI(api_key=settings.env.zhipu_api_key, base_url=settings.env.zhipu_base_url)
        self.model = settings.c

    def call(
        self,
        messages: List[dict],
        task_name: str = "default",
        role_name: str = "default"
    ) -> str:
        response = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
        )

        return response.choices[0].message.content


class ZhipuAIQAClient:
    def __init__(self):
        self.api_key = api_key

    """
        {
        "data": [
            {
            "text": "<string>",
            "score": 123,
            "metadata": {
                "_id": "<string>",
                "knowledge_id": "<string>",
                "doc_id": "<string>",
                "doc_name": "<string>",
                "doc_url": "<string>",
                "contextual_text": "<string>"
            }
            }
        ],
        "code": 123,
        "message": "<string>",
        "timestamp": 123
        }
    """

    def call_kbq(self, query: str, top_k) -> List[str]:
    
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "query": query,
            "knowledge_ids": [knowledge_id],
            "top_k": top_k
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()

        resp = resp.json()

        try:
            data = resp.get("data")
            results = []
            for i in range(top_k):
                result = data[i].get("text", "No result")
                results.append(result)
        except Exception as e:
            raise e
        
        return results


def read_jsonl(filename):
    """Reads a jsonl file and yields each line as a dictionary"""
    lines = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            lines.append(json.loads(line))
    return lines

class BM25RetrievalInstruction:
    def __init__(self, top_k: int):
        stop_path = config.INSTRUCIONS_DIR.joinpath("stopwords_english.txt")
        self.stopwords = set(open(stop_path, encoding="utf-8").read().splitlines())

        self.instructions = []
        instructions_path = config.INSTRUCIONS_DIR.joinpath("st_brief_keywords.jsonl")
        self.instructions.extend(read_jsonl(instructions_path))
        self.instruction_names = [api['instruction_name'] for api in self.instructions]

        self.channel_texts = {
            'keywords': [],
            'summary': [],
            'usage': []
        }

        for api in self.instructions:
            self.channel_texts["keywords"].append(self._tokenize(api["generated_keywords"]))
            self.channel_texts["summary"].append(self._tokenize(api["generated_brief"]["functional_summary"]))
            self.channel_texts["usage"].append(self._tokenize(api["generated_brief"]["usage_context"]))

            self.bm25_model = {
                "keywords": BM25Okapi(self.channel_texts["keywords"]),
                "summary": BM25Okapi(self.channel_texts["summary"]),
                "usage": BM25Okapi(self.channel_texts["usage"])
            }

            self.top_k = top_k
            self.instruction_score_threshold = 0.5

    def _tokenize(self, content: str) -> List[str]:
        if isinstance(content, list):
            content = ".".join(content)

        tokens = list(jieba.cut(content.lower()))
        return [t for t in tokens if t not in self.stopwords]
        
    def query_multi_channel(self, query: str) -> List[str]:
        import re
        
        def split_text(text: str) -> List[str]:
            return [line.strip() for line in re.split(r'[；;。\n]+', text) if line.strip()]
        
        matched_apis = set()

        for sentence in split_text(query):
            tokenized = self._tokenize(sentence)
            for channel, bm25 in self.bm25_model.items():
                scores = bm25.get_scores(tokenized)
                scored_items = [
                    (self.instruction_names[i], score)
                    for i, score in enumerate(scores)
                    if score > self.instruction_score_threshold
                ]
                top_hits = sorted(scored_items, key=lambda x: x[1], reverse=True)[:self.top_k]
                matched_apis.update([name for name, _ in top_hits])

        return list(matched_apis)


class ClientManager:
    _instance = None
    _openai_client: OpenAIClient = None
    _zhipuai_client: ZhipuAIQAClient = None
    _local_api_retrieval: BM25RetrievalInstruction = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ClientManager, cls).__new__(cls)
        return cls._instance
    
    def init_client(self):
        self._openai_client = OpenAIClient()
        self._zhipuai_client = ZhipuAIQAClient()
        self._local_api_retrieval = BM25RetrievalInstruction(top_k=2)

    def get_openai_client(self):
        if self._openai_client is None:
            raise Exception("OpenAIClient未初始化")
        return self._openai_client

    def get_zhipuai_client(self):
        if self._zhipuai_client is None:
            raise Exception("ZhipuAIQAClient未初始化")
        return self._zhipuai_client

    def get_local_api_retriever(self):
        if self._local_api_retriever is None:
            raise Exception("BM25RetrievalInstruction未初始化")
        return self._local_api_retriever




if __name__ == "__main__":
    results = call_kbq(query="输入一个变长 DInt 数组，输出最大值、最小值，以及它们各自的位置。", top_k=5)
    print(results)