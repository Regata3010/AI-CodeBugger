# from langchain.prompts import PromptTemplate
# from langchain.schema.output_parser import StrOutputParser
# from langchain_core.runnables.history import RunnableWithMessageHistory
# from src.logger import logging
# from src.exception import CustomException
# import sys
# from dotenv import load_dotenv


# load_dotenv()


# try:
#     def conversational_agent(llm,memory):
#         logging.info("Process has Started..")
#         conversational_template = PromptTemplate(
#             input_variables=['code','question'],
#             template=(
#                 "You are an expert Python developer.\n"
#                 "Here is a Python code snippet:\n\n{code}\n\n"
#                 "Previous Conversation:\n{history}\n\n"
#                 "Now answer this question about the code:\n\n{question}"
#             )
#         )
        
#         base_chain = conversational_template | llm | StrOutputParser()
        
#         wrapped_chain = RunnableWithMessageHistory(
#             base_chain,
#             get_session_history= lambda session_id : memory,
#             input_messages_key="question",
#             history_messages_key="history"
#         )
        
#         return wrapped_chain

# except Exception as e:
#     logging.info("There has been an Error...")
#     raise CustomException(e,sys)
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from core.src.logger import logging
from core.src.exception import CustomException
import sys
import re
from dotenv import load_dotenv

load_dotenv()

class ConversationAnalyzer:
    """Analyzes code to determine appropriate conversational context"""
    
    @staticmethod
    def detect_code_type(code: str) -> str:
        """Detect code type for conversation context"""
        code_lower = code.lower()
        
        # Cybersecurity Detection
        if any(sec in code_lower for sec in ['encryption', 'hash', 'cipher', 'crypto', 'security', 'authentication', 'bcrypt', 'jwt']):
            return 'cybersecurity'
        
        # Machine Learning Detection
        elif any(ml in code_lower for ml in ['tensorflow', 'pytorch', 'sklearn', 'model', 'training', 'predict']):
            return 'machine_learning'
        
        # DevOps Detection
        elif any(devops in code_lower for devops in ['docker', 'kubernetes', 'aws', 'deployment', 'container']):
            return 'devops'
        
        # Financial Systems Detection
        elif any(fin in code_lower for fin in ['portfolio', 'trading', 'finance', 'stock', 'price', 'currency']):
            return 'financial_systems'
        
        # Web Framework Detection
        elif any(framework in code_lower for framework in ['flask', 'django', 'fastapi', 'app.route']):
            return 'flask_web'
        
        # Data Science Detection
        elif any(lib in code_lower for lib in ['pandas', 'numpy', 'matplotlib']):
            return 'data_science'
        
        # Database Detection
        elif any(db in code_lower for db in ['sqlite3', 'mysql', 'sql']):
            return 'database'
        
        # Algorithm Detection
        elif 'def ' in code and any(algo in code_lower for algo in ['sort', 'search', 'tree']):
            return 'algorithm'
        
        # Object Oriented Detection
        elif 'class ' in code and 'def __init__' in code:
            return 'object_oriented'
        
        else:
            return 'general'
    
    @staticmethod
    def assess_conversation_complexity(code: str) -> str:
        """Assess appropriate conversation depth"""
        lines = len([line for line in code.split('\n') if line.strip()])
        functions = code.count('def ')
        classes = code.count('class ')
        
        complexity_score = lines + (functions * 2) + (classes * 3)
        
        if complexity_score < 20:
            return 'beginner'
        elif complexity_score < 50:
            return 'intermediate'
        else:
            return 'advanced'

# Dynamic conversational templates
DYNAMIC_CONVERSATIONAL_TEMPLATES = {
    'cybersecurity': {
        'beginner': '''You are a friendly cybersecurity mentor helping developers understand security concepts.

Code context:
{code}

Previous conversation:
{history}

Your expertise includes:
- Explaining security vulnerabilities in simple terms
- Teaching secure coding practices
- Helping understand cryptographic concepts
- Providing security best practices

User question: {question}

Respond in a helpful, educational manner focusing on security concepts and best practices.''',
        
        'advanced': '''You are a principal security architect providing expert cybersecurity guidance.

Code context:
{code}

Previous conversation:
{history}

Your expertise includes:
- Advanced threat modeling and vulnerability assessment
- Enterprise security architecture and compliance
- Cryptographic implementation analysis
- Security testing and penetration testing methodologies

User question: {question}

Provide expert-level security analysis with advanced insights and industry best practices.'''
    },
    
    'machine_learning': {
        'beginner': '''You are a patient ML engineer helping developers understand machine learning concepts.

Code context:
{code}

Previous conversation:
{history}

Your expertise includes:
- Explaining ML algorithms and model behavior
- Teaching data preprocessing and feature engineering
- Helping with model training and evaluation
- Providing ML best practices and debugging tips

User question: {question}

Respond in an educational manner, breaking down complex ML concepts into understandable explanations.''',
        
        'advanced': '''You are a principal ML architect providing expert machine learning guidance.

Code context:
{code}

Previous conversation:
{history}

Your expertise includes:
- Advanced ML model architecture and optimization
- Production ML system design and MLOps
- Model performance analysis and debugging
- Research-level ML techniques and innovations

User question: {question}

Provide expert-level ML guidance with advanced technical insights and production considerations.'''
    },
    
    'data_science': {
        'beginner': '''You are a friendly data scientist helping developers understand data analysis concepts.

Code context:
{code}

Previous conversation:
{history}

Your expertise includes:
- Explaining pandas and numpy operations
- Teaching data manipulation and analysis techniques
- Helping with data visualization and statistics
- Providing data science best practices

User question: {question}

Respond in a clear, educational manner with practical data science guidance.''',
        
        'advanced': '''You are a principal data scientist providing expert data analysis guidance.

Code context:
{code}

Previous conversation:
{history}

Your expertise includes:
- Advanced statistical analysis and methodology
- Production data pipeline architecture
- Data quality and governance strategies
- Research methodologies and experimental design

User question: {question}

Provide expert-level data science insights with advanced analytical perspectives.'''
    },
    
    'flask_web': {
        'beginner': '''You are a friendly web development mentor helping developers understand Flask concepts.

Code context:
{code}

Previous conversation:
{history}

Your expertise includes:
- Explaining Flask routes and HTTP concepts
- Teaching web security and best practices
- Helping with database integration and APIs
- Providing web development guidance

User question: {question}

Respond in a helpful manner, explaining web development concepts clearly.''',
        
        'advanced': '''You are a principal web architect providing expert Flask development guidance.

Code context:
{code}

Previous conversation:
{history}

Your expertise includes:
- Advanced Flask architecture and design patterns
- Production web application deployment and scaling
- Web security and performance optimization
- Enterprise web development practices

User question: {question}

Provide expert-level web development insights with architectural and production considerations.'''
    },
    
    'database': {
        'beginner': '''You are a database expert helping developers understand database concepts.

Code context:
{code}

Previous conversation:
{history}

Your expertise includes:
- Explaining SQL queries and database operations
- Teaching database design and optimization
- Helping with data integrity and transactions
- Providing database best practices

User question: {question}

Respond with clear explanations of database concepts and practical guidance.''',
        
        'advanced': '''You are a principal database architect providing expert database guidance.

Code context:
{code}

Previous conversation:
{history}

Your expertise includes:
- Advanced database design and optimization
- Production database administration and scaling
- Database security and performance tuning
- Enterprise data architecture

User question: {question}

Provide expert-level database insights with advanced technical and architectural guidance.'''
    },
    
    'algorithm': {
        'beginner': '''You are a computer science teacher helping developers understand algorithmic concepts.

Code context:
{code}

Previous conversation:
{history}

Your expertise includes:
- Explaining algorithm logic and complexity
- Teaching data structures and optimization
- Helping with mathematical concepts and proofs
- Providing algorithmic problem-solving guidance

User question: {question}

Respond with clear explanations of algorithmic concepts and problem-solving approaches.''',
        
        'advanced': '''You are a computer science researcher providing expert algorithmic guidance.

Code context:
{code}

Previous conversation:
{history}

Your expertise includes:
- Advanced algorithm design and analysis
- Complexity theory and optimization techniques
- Research-level algorithmic innovations
- Production algorithm implementation and scaling

User question: {question}

Provide expert-level algorithmic insights with theoretical depth and practical optimization guidance.'''
    },
    
    'general': {
        'beginner': '''You are a friendly Python mentor helping developers understand programming concepts.

Code context:
{code}

Previous conversation:
{history}

Your expertise includes:
- Explaining Python syntax and concepts
- Teaching programming best practices
- Helping with debugging and problem-solving
- Providing clear, educational guidance

User question: {question}

Respond in a helpful, educational manner with clear explanations and practical advice.''',
        
        'advanced': '''You are a senior Python engineer providing expert development guidance.

Code context:
{code}

Previous conversation:
{history}

Your expertise includes:
- Advanced Python patterns and techniques
- Software architecture and design principles
- Production system development and optimization
- Enterprise development practices

User question: {question}

Provide expert-level Python guidance with advanced technical insights and professional best practices.'''
    }
}

try:
    def get_dynamic_conversational_agent(llm, memory, code):
        """Generate dynamic conversational agent based on code analysis"""
        
        # Analyze the code for context
        analyzer = ConversationAnalyzer()
        code_type = analyzer.detect_code_type(code)
        complexity = analyzer.assess_conversation_complexity(code)
        
        # Select appropriate template
        template_category = DYNAMIC_CONVERSATIONAL_TEMPLATES.get(code_type, DYNAMIC_CONVERSATIONAL_TEMPLATES['general'])
        template_text = template_category.get(complexity, template_category['beginner'])
        
        # Create dynamic conversational template
        conversational_template = PromptTemplate(
            input_variables=['code', 'question'],
            template=template_text
        )
        
        base_chain = conversational_template | llm | StrOutputParser()
        
        wrapped_chain = RunnableWithMessageHistory(
            base_chain,
            get_session_history=lambda session_id: memory,
            input_messages_key="question",
            history_messages_key="history"
        )
        
        return wrapped_chain
    
    def conversational_agent(llm, memory, code=None, use_dynamic=True):
        """
        Get conversational agent - supports both static and dynamic modes
        
        Args:
            llm: Language model instance
            memory: Conversation memory
            code: Code context (required for dynamic mode)
            use_dynamic: Whether to use dynamic prompting (default: True)
        """
        if use_dynamic and code:
            return get_dynamic_conversational_agent(llm, memory, code)
        else:
            # Fallback to original static template
            conversational_template = PromptTemplate(
                input_variables=['code', 'question'],
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
                get_session_history=lambda session_id: memory,
                input_messages_key="question",
                history_messages_key="history"
            )
            
            return wrapped_chain

except Exception as e:
    raise CustomException(e, sys)