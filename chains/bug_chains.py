from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema.output_parser import StrOutputParser
from src.logger import logging
from src.exception import CustomException
import sys
from dotenv import load_dotenv
import streamlit as st


load_dotenv()
openai_key = st.secrets["OPENAI_API_KEY"]


try:
   def get_bugchains(llm):
        logging.info("Process has Started..")
        bug_template = PromptTemplate(
        input_variables=["code"],
        template='''You are a Python expert. Review the following code and list any bugs, errors, or bad practices with explanations:\n\n{code}'''
    )
        return bug_template | llm | StrOutputParser()
    
except Exception as e:
    logging.info("There has been an Error..")
    raise CustomException(e,sys)