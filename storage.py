# import streamlit as st
# from dotenv import load_dotenv
# from chains.bug_chains import get_bugchains
# from chains.optimize_chains import get_optimized_chains
# from chains.explanation_chains import get_expalanationchains
# from chains.conversational import conversational_agent
# from chains.unittest import unittestchains
# from src.logger import logging
# from src.exception import CustomException
# from langchain_openai import ChatOpenAI
# from google.cloud import firestore
# from langchain_google_firestore import FirestoreChatMessageHistory
# from chains.githubhandler import handle_github_repo
# import sys
# import difflib
# import warnings
# warnings.filterwarnings("ignore", category=UserWarning, module="langchain")


# load_dotenv()
# openai_key = st.secrets["OPENAI_API_KEY"]

# #Firestore Creds
# PROJECT_ID = "regata-2ca53"
# SESSION_ID = "user_prompt"
# COLLECTION_NAME = "chat_history_chains"

# logging.info("Initializing Firestore History...")
# client = firestore.Client(project=PROJECT_ID)


# chat_history_chains = FirestoreChatMessageHistory(
#     session_id=SESSION_ID,
#     collection=COLLECTION_NAME,
#     client=client,
# )

# # memory = ConversationBufferMemory(
# #     memory_key = "history",
# #     chat_memory = chat_history_chains,
# #     return_messages = True
# # )

# memory = chat_history_chains


# #hasnt been used yet we need to work on it
# def get_diff_view(code_before, code_after):
#     differ = difflib.unified_diff(
#         code_before.splitlines(),
#         code_after.splitlines(),
#         fromfile="Original",
#         tofile="Optimized",
#         lineterm=""
#     )
#     return "\n".join(differ)


# st.set_page_config(page_title="🧠 AI Code Review Assistant", layout="wide")
# st.title("🧠 AI Code Review & Optimizer")
# st.markdown("Paste your Python code and let AI help debug, improve, and explain it.")

# st.markdown("### 📂 Upload Your Code")

# uploaded_file = st.file_uploader("Upload a Zip File", type="zip", key="zip_upload")
# st.markdown("---")
# # zip_file = st.file_upload("Upload Your Zip File",type=["zip"],key="zip_upload")
# # with st.expander("🧠 Ask Anything About Your Codebase", expanded=False):
# #     zip_file = st.file_uploader("Upload your zipped codebase", type="zip",key="zip_upload")

# #     user_question = st.text_input("What do you want to know about your codebase?")
# #     if st.button("📬 Ask") and zip_file and user_question:
# #         handle_zip(zip_file, user_question)
# with st.expander("🔗 Ask Questions from GitHub Repo", expanded=False):
#     github_url = st.text_input("Enter GitHub Repo URL (public)", key="gh_url")
#     github_question = st.text_input("What do you want to know about this repo?", key="gh_q")

#     if st.button("🚀 Analyze GitHub Repo") and github_url and github_question:
#         with st.spinner("Cloning and analyzing..."):
#             answer = handle_github_repo(github_url, github_question)
#             st.markdown(f"**🧠 Assistant:** {answer}")


# code_input = ""

# if uploaded_file is not None:
#     code_input = uploaded_file.read().decode("utf-8")
#     st.success("✅ File uploaded successfully!")
# else:
#     code_input = st.text_area("✍️ Or Paste your Python code below:", height=300)
    

# analysis_type = st.multiselect("Choose Analysis Type: ", 
#                                        ['Bug Detection','Code Optimization','Code Explanation','Unit Test Generation'])

# model_choice = st.selectbox("Choose your Model",['gpt-4o','gpt-3.5-turbo','o3-mini'])
# st.caption("💡 GPT-4o is fastest & smartest. GPT-3.5 is cheaper and fast. o3-mini is the newest smallest reasoning model.")
# llm = ChatOpenAI(temperature=0,model=model_choice)

# bug_chain = get_bugchains(llm)
# optimized_chain = get_optimized_chains(llm)
# explanation_chain = get_expalanationchains(llm)
# unit_test_chains = unittestchains(llm)
# conversational_chains = conversational_agent(llm,memory)
    
# # Trigger analysis
# analyze = st.button("🚀 Analyze My Code")

# # Guard: Ensure this block always runs AFTER UI is fully rendered
# if analyze:
#     if code_input.strip() == "":
#         st.warning("⚠️ Please enter or upload some code.")
#     elif len(analysis_type) == 0:
#         st.warning("⚠️ Please select at least one analysis type.")
#     else:
#         try:
#             with st.spinner("Analyzing your code..."):
#                 # Dynamically run selected chains
#                 if "Bug Detection" in analysis_type:
#                     output = bug_chain.invoke({"code": code_input})
#                     st.subheader("🐞 Bug Report")
#                     st.code(output)

#                 if "Code Optimization" in analysis_type:
#                     output = optimized_chain.invoke({"code": code_input})
#                     st.subheader("⚡ Optimized Code")
#                     # st.code(output)
                    
#                     st.subheader("💣 Optimized Code Comparison")
#                     col1,col2 = st.columns(2)
                    
#                     with col1:
#                         st.markdown("**📥 Original Code**")
#                         st.code(code_input, language='python')

#                     with col2:
#                         st.markdown("**📤 Optimized Code**")
#                         st.code(output, language='python')
                        
#                     diff_result = get_diff_view(code_input,output)
#                     with st.expander("🧾 View Code Differences (Unified Diff)", expanded=False):
#                         st.code(diff_result, language="diff")
                    
#                     st.download_button(
#                         label = "Download your Updated py file.",
#                         data = output,
#                         file_name="optimized_code.py",
#                         mime = "text/x-python" 
#                     )

#                 if "Code Explanation" in analysis_type:
#                     output = explanation_chain.invoke({"code": code_input})
#                     st.subheader("📘 Explanation")
#                     st.markdown(output)
                    
#                 if "Unit Test Generation" in analysis_type:
#                     output = unit_test_chains.invoke({"code":code_input})
#                     st.subheader("Unit Test")
#                     st.markdown(output)
                    

#             st.success("✅ Analysis Complete!")


#         except Exception as e:
#             logging.info("There has been an Error..")
#             raise CustomException(e,sys)

# try:
#     with st.expander("💬 Chat with your Code Assistant", expanded=False):
#         # try:
#         #     stored_data = memory.chat_memory.messages  
#         #     if stored_data:
#         #         st.markdown("**🕘 Chat History:**")
#         #         for msg in stored_data:
#         #             role = "🧑 You" if msg.type == "human" else "🤖 Assistant"
#         #             st.markdown(f"**{role}:** {msg.content}")
#         #     else:
#         #         st.markdown("_No previous chat history found._")
#         # except Exception as e:
#         #     st.warning("⚠️ Couldn't load chat history.")
#         #     logging.warning(f"[Chat History] Issue: {str(e)}")

#         user_message = st.text_input("Ask something about your code:")
#         if st.button("📩 Send") and user_message:
#             response = conversational_chains.invoke(
#                 {"code": code_input, "question": user_message},
#                 config={"configurable": {"session_id": SESSION_ID}}
#             )
#             st.markdown(f"**🧠 Assistant:** {response}")

# except Exception as e:
#     logging.error("Major failure inside chat UI block")
#     raise CustomException(e, sys)
