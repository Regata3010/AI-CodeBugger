from langchain.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
import os, sys
import zipfile, tempfile
from src.logger import logging
from src.exception import CustomException
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain.schema import Document
import warnings
from langchain.text_splitter import RecursiveCharacterTextSplitter
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")

load_dotenv()


try:
        def handle_zip(zip_file, question):
            logging.info("Process has Started..")
            with tempfile.TemporaryDirectory() as tmp_dir:
                zip_path = os.path.join(tmp_dir, "codebase.zip")
                with open(zip_path, "wb") as f:
                    f.write(zip_file.getbuffer())
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(tmp_dir)
                
                # Process Python files
                code_chunks = []
                for root, _, files in os.walk(tmp_dir):
                    for file in files:
                        if file.endswith(".py"):
                            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                                code = f.read()
                                splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
                                for chunk in splitter.split_text(code):
                                    code_chunks.append(chunk)
                                    
                                    
                embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
                vector_store = Chroma.from_documents(code_chunks,embeddings)
                
                retriever = vector_store.as_retriever(
                    search_type = "similarity_search_threshold",
                    search_kwargs = {"k":1,"threshold":0.8},
                )
                
                docs = [Document(page_content=chunk) for chunk in code_chunks]
                relevant_docs = retriever.invoke(question)
                context = "\n\n".join([doc.page_content for doc in relevant_docs])
                
                
                prompt = PromptTemplate.from_template(
                "You are an expert Python developer.\n\n"
                "Here are relevant parts of the codebase:\n{context}\n\n"
                "Question: {question}\n\n"
                "Answer clearly and in detail:"
            )

                llm = ChatOpenAI(temperature=0)
                chain = prompt | llm | StrOutputParser()
                answer = chain.invoke({"context": context, "question": question})
                return answer


except Exception as e:
    logging.info("There has been a Error..")
    raise CustomException(e,sys)