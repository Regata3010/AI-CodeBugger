from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from src.logger import logging
from src.exception import CustomException
import sys
from dotenv import load_dotenv


load_dotenv()


try:
    def conversational_agent(llm,memory):
        logging.info("Process has Started..")
        conversational_template = PromptTemplate(
            input_variables=['code','question'],
            template=(
                "You are an expert Python developer.\n"
                "Here is a Python code snippet:\n\n{code}\n\n"
                "Previous Conversation:\n{history}\n\n"
                "Now answer this question about the code:\n\n{question}"
            )
        )
        
        base_chain = conversational_template | llm | StrOutputParser()
        
        wrapped_chain = RunnableWithMessageHistory(
            base_chain,
            get_session_history= lambda session_id : memory,
            input_messages_key="question",
            history_messages_key="history"
        )
        
        return wrapped_chain

except Exception as e:
    logging.info("There has been an Error...")
    raise CustomException(e,sys)