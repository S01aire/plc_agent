import json
from typing import List

from plc_agent.src.core.config_loader import get_config
from plc_agent.src.core.models import LocalRetrievalConfig

from plc_agent.src.log.logging_config import setup_logger


logger = setup_logger("APIDataLoader")

class APIDataLoader:
    api_detail_dict: dict = None

    @classmethod
    def init_load(cls, config: LocalRetrievalConfig):
        if cls.api_detail_dict is None:
            cls.api_detail_dict = {}
            try:
                for path in config.INSTRUCIONS_DIR:
                    with open(path, "r", encoding="utf-8") as fp:
                        for line in fp:
                            json_data = json.loads(line)
                            api_name = json_data["instruction_name"]
                            cls.api_detail_dict[api_name] = json_data
            except Exception as e:
                logger.error(f"加载API数据失败: {e}")

        

    @classmethod
    def query_api_brief(cls, api_names: List[str]) -> List[dict]:
        api_detail_dict = cls.api_detail_dict
        api_details = []
        for api in api_names:
            if api in api_detail_dict:
                api_details.append(
                    {
                        "instruction_name": api,
                        "generated_brief": api_detail_dict[api]["generated_brief"],
                        "generated_keywords": api_detail_dict[api]["generated_keywords"],
                    }
                )
        return api_details