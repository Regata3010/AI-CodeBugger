from langchain.prompts import PromptTemplate
import sys
from dotenv import load_dotenv
from langchain.schema.output_parser import StrOutputParser
from src.logger import logging
from src.exception import CustomException

load_dotenv()


try:
    def unittestchains(llm):
        logging.info("Process has Started...")
        unittest_template = PromptTemplate(
            input_variables=['code'],
            template = '''You are a Senior Python Developer. 
            Write Unit test code for the following python code:\n\n{code}'''
        )
        
        return unittest_template | llm | StrOutputParser()

except Exception as e:
    logging.info("There has been a Problem..")
    raise CustomException(e,sys)
   