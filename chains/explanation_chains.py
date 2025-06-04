from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate
from src.logger import logging
from src.exception import CustomException
import sys
from dotenv import load_dotenv


load_dotenv()

try:
    def get_expalanationchains(llm):
        logging.info("Process has Started..")
        explanation_template = PromptTemplate(
            input_variables=['code'],
            template='''You're an experienced Python instructor.Explain the following code **line by line** in simple, beginner-friendly language:\n\n{code}'''
        )
        return explanation_template | llm | StrOutputParser()
    
except Exception as e:
    logging.info("There has been an Error..")
    raise CustomException(e,sys)