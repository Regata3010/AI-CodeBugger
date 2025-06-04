from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema.output_parser import StrOutputParser
from src.logger import logging
from src.exception import CustomException
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    def get_optimized_chains(llm):
          logging.info("Process has Started..")
          optimized_template = PromptTemplate(
          input_variables=["code"],
          template='''You are a senior Python engineer. Refactor the code below to make it cleaner, more readable, 
                    and more efficient:\n\n{code}'''
          )
          return optimized_template | llm | StrOutputParser()


except Exception as e:
    logging.info("There has been an Error..")
    raise CustomException(e,sys)