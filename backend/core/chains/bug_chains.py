# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# from langchain.schema.output_parser import StrOutputParser
# from src.logger import logging
# from src.exception import CustomException
# import sys
# from dotenv import load_dotenv
# import streamlit as st


# load_dotenv()
# openai_key = st.secrets["OPENAI_API_KEY"]


# try:
#    def get_bugchains(llm):
#         logging.info("Process has Started..")
#         bug_template = PromptTemplate(
#         input_variables=["code"],
#         template='''You are a Python expert. Review the following code and list any bugs, errors, or bad practices with explanations:\n\n{code}'''
#     )
#         return bug_template | llm | StrOutputParser()
    
# except Exception as e:
#     logging.info("There has been an Error..")
#     raise CustomException(e,sys)
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema.output_parser import StrOutputParser
from core.src.logger import logging
from core.src.exception import CustomException
import sys
import re
import ast
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
# openai_key = st.secrets["OPENAI_API_KEY"]

class CodeAnalyzer:
    """Analyzes code to determine type and complexity for dynamic prompting"""
    
    @staticmethod
    def detect_code_type(code: str) -> str:
        """Detect the type of code to apply appropriate analysis"""
        code_lower = code.lower()
        
        # Web Framework Detection
        if any(framework in code_lower for framework in ['flask', 'django', 'fastapi']):
            if 'flask' in code_lower or 'app.route' in code_lower:
                return 'flask_web'
            elif 'django' in code_lower or 'models.model' in code_lower:
                return 'django_web'
            elif 'fastapi' in code_lower or '@app.get' in code_lower:
                return 'fastapi_web'
            else:
                return 'web_general'
        
        # Data Science Detection
        elif any(lib in code_lower for lib in ['pandas', 'numpy', 'matplotlib', 'sklearn']):
            return 'data_science'
        
        # Database Detection
        elif any(db in code_lower for db in ['sqlite3', 'mysql', 'postgresql', 'sql']):
            return 'database'
        
        # Algorithm Detection
        elif ('def ' in code and any(algo in code_lower for algo in ['sort', 'search', 'tree', 'graph', 'algorithm'])):
            return 'algorithm'
        
        # Object Oriented Detection
        elif 'class ' in code and 'def __init__' in code:
            return 'object_oriented'
        
        # Security/Crypto Detection
        elif any(sec in code_lower for sec in ['hashlib', 'crypto', 'password', 'authentication']):
            return 'security'
        
        # File Operations
        elif any(file_op in code_lower for file_op in ['open(', 'file', 'read(', 'write(']):
            return 'file_operations'
        
        else:
            return 'general'
    
    @staticmethod
    def assess_complexity(code: str) -> str:
        """Assess code complexity level"""
        lines = len([line for line in code.split('\n') if line.strip()])
        functions = code.count('def ')
        classes = code.count('class ')
        imports = len([line for line in code.split('\n') if line.strip().startswith(('import ', 'from '))])
        
        complexity_score = lines + (functions * 3) + (classes * 5) + imports
        
        if complexity_score < 20:
            return 'simple'
        elif complexity_score < 60:
            return 'medium'
        else:
            return 'complex'
    
    @staticmethod
    def detect_security_indicators(code: str) -> list:
        """Detect potential security-related patterns"""
        security_patterns = []
        
        if re.search(r'["\'].*password.*["\']', code, re.IGNORECASE):
            security_patterns.append('password_handling')
        if 'sql' in code.lower() or any(db in code.lower() for db in ['execute', 'query', 'select', 'insert']):
            security_patterns.append('database_operations')
        if any(hash_func in code.lower() for hash_func in ['md5', 'sha1', 'hash']):
            security_patterns.append('hashing_operations')
        if 'request' in code.lower() and any(method in code.lower() for method in ['post', 'get', 'form']):
            security_patterns.append('user_input_handling')
        if any(file_op in code for file_op in ['open(', 'file.save', 'upload']):
            security_patterns.append('file_operations')
            
        return security_patterns

# Dynamic Template Library
DYNAMIC_BUG_TEMPLATES = {
    'flask_web': {
        'simple': '''You are a senior web security engineer specializing in Flask applications.

Focus on Flask security issues:
- SQL injection vulnerabilities in database queries
- Authentication and session management flaws
- Input validation and sanitization issues
- Hardcoded secret keys and configuration
- Debug mode in production settings
- File upload vulnerabilities

Code to analyze:
{code}

Provide detailed findings with specific fix recommendations and Flask best practices.''',
        
        'complex': '''You are a principal security architect specializing in enterprise Flask applications.

Comprehensive security analysis for complex Flask system:
- Advanced SQL injection patterns and authentication bypass
- Authorization and privilege escalation flaws  
- API security vulnerabilities and compliance violations
- Production deployment security and scalability implications

Code to analyze:
{code}

Provide enterprise-grade security analysis with threat modeling and prioritized remediation roadmap.'''
    },
    
    'data_science': {
        'simple': '''You are a senior data engineer focusing on secure and efficient data processing.

Focus on data science code issues:
- Data validation and sanitization problems
- Memory leaks with large datasets
- Data type inconsistencies and error handling
- Resource management and scalability bottlenecks

Code to analyze:
{code}

Focus on data security, performance issues, and data quality problems.''',
        
        'complex': '''You are a principal data architect specializing in production ML/data systems.

Enterprise data system analysis:
- Data governance and compliance issues (GDPR, CCPA)
- Production scalability and performance optimization
- Data quality monitoring and fault tolerance
- Security risks in data processing pipelines

Code to analyze:
{code}

Provide comprehensive analysis covering data governance, scalability, and architectural improvements.'''
    },
    
    'security': {
        'simple': '''You are a cybersecurity expert specializing in secure coding practices.

Focus on security implementation:
- Weak hashing algorithms and encryption issues
- Password security and session management flaws
- Input validation and injection vulnerabilities
- Access control bypasses and token security

Code to analyze:
{code}

Provide detailed security assessment with cryptographic and authentication analysis.''',
        
        'complex': '''You are a principal security architect conducting enterprise security code review.

Advanced threat assessment:
- Complex attack vector analysis and vulnerability chains
- Enterprise security controls and compliance framework alignment
- Trust boundary violations and security architecture weaknesses

Code to analyze:
{code}

Provide enterprise security analysis with advanced vulnerability assessment and strategic recommendations.'''
    },
    
    'algorithm': {
        'simple': '''You are an algorithms expert and competitive programming specialist.

Focus on algorithmic analysis:
- Time and space complexity analysis (Big O notation)
- Algorithm correctness and edge case handling
- Off-by-one errors and boundary conditions
- Mathematical correctness and numerical stability

Code to analyze:
{code}

Focus on complexity analysis, algorithm correctness, and performance optimization.''',
        
        'complex': '''You are a computer science professor specializing in advanced algorithms.

Advanced algorithmic analysis:
- Comprehensive complexity analysis with mathematical proofs
- Advanced optimization techniques and alternative algorithms
- Numerical stability and precision considerations
- Production deployment and scalability analysis

Code to analyze:
{code}

Provide comprehensive algorithmic review with detailed complexity analysis and optimization recommendations.'''
    },
    
    'general': {
        'simple': '''You are a senior Python developer conducting a comprehensive code review.

Focus on Python best practices:
- Logic errors and potential bugs
- Python best practice violations and code style
- Performance inefficiencies and resource management
- Error handling and maintainability concerns

Code to analyze:
{code}

Provide thorough analysis covering bugs, best practices, and performance issues.''',
        
        'complex': '''You are a principal software engineer conducting enterprise Python code review.

Enterprise Python analysis:
- Architectural design and SOLID principles adherence
- Performance bottlenecks and scalability considerations
- Production readiness and error handling
- Technical debt and maintainability assessment

Code to analyze:
{code}

Provide enterprise-level analysis with architectural assessment and strategic recommendations.'''
    }
}

try:
    def get_dynamic_bugchains(llm, code):
        """Generate dynamic bug detection chain based on code analysis"""
        
        # Analyze the code
        analyzer = CodeAnalyzer()
        code_type = analyzer.detect_code_type(code)
        complexity = analyzer.assess_complexity(code)
        security_indicators = analyzer.detect_security_indicators(code)
        
        # Select appropriate template
        template_category = DYNAMIC_BUG_TEMPLATES.get(code_type, DYNAMIC_BUG_TEMPLATES['general'])
        template_text = template_category.get(complexity, template_category['simple'])
        
        # Create dynamic prompt template
        bug_template = PromptTemplate(
            input_variables=["code"],
            template=template_text
        )
        
        # Return the same pattern: template | llm | parser
        return bug_template | llm | StrOutputParser()
    
    # Backward compatibility - keep original function but add dynamic option
    def get_bugchains(llm, code=None, use_dynamic=True):
        """
        Get bug detection chain - supports both static and dynamic modes
        
        Args:
            llm: Language model instance
            code: Code to analyze (required for dynamic mode)
            use_dynamic: Whether to use dynamic prompting (default: True)
        """
        if use_dynamic and code:
            return get_dynamic_bugchains(llm, code)
        else:
            # Fallback to original static template
            bug_template = PromptTemplate(
                input_variables=["code"],
                template='''You are a Python expert. Review the following code and list any bugs, errors, or bad practices with explanations:\n\n{code}'''
            )
            return bug_template | llm | StrOutputParser()
    
except Exception as e:
    raise CustomException(e, sys)