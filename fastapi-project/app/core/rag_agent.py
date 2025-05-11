import os
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")


from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
import asyncio
import logging

logger = logging.getLogger(__name__)

custom_prompt = """
You are an intelligent assistant tasked with answering questions based on a provided document. The document may contain technical content (e.g., code, algorithms, technical specifications) or non-technical content (e.g., reports, manuals, general text). Use the following context from the document to answer the user’s question:

--------------------
{context}
--------------------

User Question: {question}

Instructions:
1. If the question is relevant to the document’s context, provide a precise, accurate, and concise answer. Adapt the response style to the document’s nature:
   - For technical content, include technical details, code snippets, or explanations as needed.
   - For non-technical content, use clear, accessible language suitable for the content.
2. If the question is unrelated to the document’s context (e.g., general knowledge, personal questions like "How are you?"), respond with: "The question is not related to the document’s context."
3. If no relevant information is found in the context to answer the question, respond with: "I can’t find an answer relevant to the provided document."

Your Answer:
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", custom_prompt),
    ("human", "{question}")
])

# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
# print(llm.invoke("Are you there?"))


class RAGAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.2,
            streaming=True
        )

    def build_qa_chain(self, retriever):
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
        )

    async def rag_answer_stream(self, retriever, question):
        logger.info(f"[RAG] Starting rag_answer_stream for question: {question}")
        chain = self.build_qa_chain(retriever)
        callback = AsyncIteratorCallbackHandler()
        task = asyncio.create_task(
            chain.acall({"query": question}, callbacks=[callback])
        )
        answer = ""
        try:
            async for token in callback.aiter():
                answer += token
                logger.info(f"[RAG] Yielding token: {token}")
                yield f'{{"response": "{answer}"}}\n'
            logger.info(f"[RAG] rag_answer_stream complete for question: {question}")
        except Exception as ex:
            logger.error(f"[RAG] Error in rag_answer_stream: {ex}")
            raise
        finally:
            await task
            logger.info(f"[RAG] rag_answer_stream finished for question: {question}")
