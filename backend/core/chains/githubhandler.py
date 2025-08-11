from langchain.prompts import PromptTemplate
import os,sys
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema.output_parser import StrOutputParser
from core.src.logger import logging
from core.src.exception import CustomException
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import zipfile,tempfile
from pathlib import Path
import requests


load_dotenv()


try:
    def handle_github_repo(repo_url : str , question: str):
        logging.info("Process Has Started..")
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                
                zip_url = repo_url.rstrip('/') + "/archive/refs/heads/main.zip"
                logging.info(f"Downloading ZIP from: {zip_url}")

               
                response = requests.get(zip_url)
                response.raise_for_status()

                zip_path = os.path.join(tmpdir, "repo.zip")
                with open(zip_path, "wb") as f:
                    f.write(response.content)

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)

                
                repo_name = repo_url.rstrip("/").split("/")[-1]
                extracted_path = os.path.join(tmpdir, f"{repo_name}-main")
                logging.info(f"Extracted to: {extracted_path}")
            except Exception as e:
                raise CustomException(f"Failed to download or extract repo ZIP: {e}", sys)

           
            for root, _, files in os.walk(extracted_path):
                for file in files:
                    logging.info(f"Found file: {os.path.join(root, file)}")

            
            py_files = list(Path(extracted_path).rglob("*.py"))
            py_files = [str(p) for p in py_files]
            logging.info(f"Python files found by pathlib: {py_files}")

            if not py_files:
                raise CustomException("No Python files found in the repository.", sys)
        
            code_chunks = []
            splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)

            for file_path in py_files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                    code_chunks.extend(splitter.split_text(code))

            if not code_chunks:
                logging.info("There has been a problem with the GitHub handler")
                raise CustomException("No Python files found in the repository after splitting.", sys)
            
            docs = [Document(page_content=chunk) for chunk in code_chunks]
            
            
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            vector_store = Chroma.from_documents(docs,embeddings)
            
            retriever = vector_store.as_retriever(
                        search_type = "similarity_score_threshold",
                        search_kwargs = {"k":2,"score_threshold":0.8},
                    )
                    
            # docs = [Document(page_content=chunk) for chunk in code_chunks]
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
    logging.info("There has been an error..")
    raise CustomException(e,sys)