import os
from dotenv import load_dotenv
import app.constant as constant
from app.constant import FILE_SETTINGS, ChatEnum, OpenEnum

# Load environment variables from .env file
load_dotenv()
os.environ[FILE_SETTINGS.OPENAI_API_KEY] = os.getenv(FILE_SETTINGS.OPENAI_API_KEY, "")


# fastapi-project/app/core/rag_agent.py
# This file contains the RAG agent logic for processing user queries against document contexts.
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger(__name__)

# Relevance Agent Prompt
relevance_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            constant.relevance_system_prompt,
        ),
        ("human", "CONTEXT:\n{context}\n\nQUESTION:\n{question}"),
    ]
)
# Response Agent Prompt
response_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            constant.response_system_prompt,
        ),
        ("human", "CONTEXT:\n{context}\n\nQUESTION:\n{question}\n\nANSWER:"),
    ]
)

# Relevance Agent (non-streaming)
relevance_llm = ChatOpenAI(model=OpenEnum.GPT_4.value, temperature=0)
# Response Agent (streaming)
response_llm = ChatOpenAI(model=OpenEnum.GPT_4.value, temperature=0.2, streaming=True)


async def is_question_relevant(context, question):
    prompt_str = relevance_prompt.format(context=context, question=question)
    result = await relevance_llm.ainvoke(prompt_str)
    output = result.content.strip().lower()
    logger.info(f"Relevance agent output: {output}")
    if output.startswith(ChatEnum.RELEVANT.value):
        return True
    return False


async def stream_rag_response(context, question):
    prompt_str = response_prompt.format(
        context=context,
        question=question,
        custom_prompt=constant.custom_prompt,  # <-- inject here!
    )
    async for chunk in response_llm.astream(prompt_str):
        yield chunk.content or ""
