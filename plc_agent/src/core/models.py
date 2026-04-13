from pydantic import BaseModel, Field

class LLMConfig(BaseModel):
    model: str

class RAGConfig(BaseModel):
    model: str = "glm-4.6"
    top_k: int = 10
    knowledge_id: str = "2038892149235396608"
    url: str = "https://open.bigmodel.cn/api/llm-application/open/knowledge/retrieve"

class LocalRetrievalConfig(BaseModel):
    INSTRUCIONS_DIR: str = "/plc_agent/data/rag_data/instructions/"

class VerifierConfig(BaseModel):
    MATIEC_PATH: str = "/home/papakuma/plc_agent/matiec"
    evaluate_compiler: str = "matiec"

class Config(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    local_retrieval: LocalRetrievalConfig = Field(default_factory=LocalRetrievalConfig)
    verifier: VerifierConfig = Field(default_factory=VerifierConfig)



