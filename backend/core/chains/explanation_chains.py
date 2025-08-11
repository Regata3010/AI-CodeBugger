# from langchain_openai import ChatOpenAI
# from langchain.schema.output_parser import StrOutputParser
# from langchain.prompts import PromptTemplate
# from src.logger import logging
# from src.exception import CustomException
# import sys
# from dotenv import load_dotenv

# load_dotenv()

# try:
#     def get_expalanationchains(llm):
#         logging.info("Process has Started..")
#         explanation_template = PromptTemplate(
#             input_variables=['code'],
#             template='''You're an experienced Python instructor.Explain the following code line by line in simple, beginner-friendly language:\n\n{code}'''
#         )
#         return explanation_template | llm | StrOutputParser()

# except Exception as e:
#     logging.info("There has been an Error..")
#     raise CustomException(e,sys)
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate
from core.src.logger import logging
from core.src.exception import CustomException
import sys
import re
import ast
from dotenv import load_dotenv

load_dotenv()

class ExplanationAnalyzer:
    """Analyzes code to determine appropriate explanation approach"""
    
    @staticmethod
    def detect_code_type(code: str) -> str:
        """Detect code type for context-specific explanations"""
        code_lower = code.lower()
        
        # Web Framework Detection
        if any(framework in code_lower for framework in ['flask', 'django', 'fastapi']):
            if 'flask' in code_lower or 'app.route' in code_lower:
                return 'flask_web'
            elif 'django' in code_lower:
                return 'django_web'
            elif 'fastapi' in code_lower:
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
        elif ('def ' in code and any(algo in code_lower for algo in ['sort', 'search', 'tree', 'graph'])):
            return 'algorithm'
        
        # Object Oriented Detection
        elif 'class ' in code and 'def __init__' in code:
            return 'object_oriented'
        
        # File Operations
        elif any(file_op in code_lower for file_op in ['open(', 'file', 'read(', 'write(']):
            return 'file_operations'
        
        # API/Network
        elif any(api in code_lower for api in ['requests', 'http', 'api', 'json']):
            return 'api_network'
        
        else:
            return 'general'
    
    @staticmethod
    def assess_complexity(code: str) -> str:
        """Assess code complexity for explanation depth"""
        lines = len([line for line in code.split('\n') if line.strip()])
        functions = code.count('def ')
        classes = code.count('class ')
        imports = len([line for line in code.split('\n') if line.strip().startswith(('import ', 'from '))])
        
        complexity_score = lines + (functions * 2) + (classes * 3) + imports
        
        if complexity_score < 15:
            return 'beginner'
        elif complexity_score < 40:
            return 'intermediate'
        else:
            return 'advanced'
    
    @staticmethod
    def identify_key_concepts(code: str) -> list:
        """Identify key programming concepts to explain"""
        concepts = []
        
        # Control structures
        if 'if ' in code:
            concepts.append('conditionals')
        if any(loop in code for loop in ['for ', 'while ']):
            concepts.append('loops')
        
        # Data structures
        if '[' in code or 'list(' in code:
            concepts.append('lists')
        if '{' in code or 'dict(' in code:
            concepts.append('dictionaries')
        
        # Functions and classes
        if 'def ' in code:
            concepts.append('functions')
        if 'class ' in code:
            concepts.append('classes')
        
        # Error handling
        if 'try:' in code or 'except' in code:
            concepts.append('error_handling')
        
        # File operations
        if 'open(' in code:
            concepts.append('file_handling')
        
        # Advanced concepts
        if 'lambda' in code:
            concepts.append('lambda_functions')
        if any(comp in code for comp in ['for ', 'if ']) and '[' in code:
            concepts.append('comprehensions')
        
        return concepts

# Dynamic explanation templates
DYNAMIC_EXPLANATION_TEMPLATES = {
    'flask_web': {
        'beginner': '''You are a friendly web development instructor teaching Flask to beginners.

Explain this Flask code line by line, focusing on:
- What Flask is and why we use it
- How web routes work (URLs and functions)
- What HTTP methods (GET, POST) do
- How web requests and responses work
- Basic web development concepts

Code to explain:
{code}

Use simple language and relate everything to real-world web interactions. Explain like you're teaching someone who has never built a website before.''',
        
        'intermediate': '''You are an experienced web development teacher explaining Flask concepts to intermediate programmers.

Explain this Flask application focusing on:
- Flask application architecture and patterns
- Request/response cycle and HTTP concepts
- Database integration and data flow
- Security considerations and best practices
- Production deployment concepts

Code to explain:
{code}

Provide detailed technical explanations while keeping it accessible to someone with basic programming knowledge.''',
        
        'advanced': '''You are a senior web architect explaining advanced Flask implementation to experienced developers.

Explain this complex Flask system covering:
- Advanced Flask patterns and architectural decisions
- Performance implications and optimization strategies
- Security architecture and threat mitigation
- Scalability considerations and production practices
- Integration patterns and microservices concepts

Code to explain:
{code}

Provide expert-level analysis with architectural insights and production considerations.'''
    },
    
    'data_science': {
        'beginner': '''You are a patient data science instructor teaching Python data analysis to beginners.

Explain this data science code step by step:
- What data science libraries do (pandas, numpy)
- How data is stored and manipulated
- What different data operations accomplish
- Why we use these specific methods
- How data flows through the analysis

Code to explain:
{code}

Use analogies and simple examples. Explain like you're teaching someone who has never worked with data before.''',
        
        'intermediate': '''You are an experienced data scientist explaining analysis techniques to intermediate practitioners.

Explain this data analysis code focusing on:
- Data manipulation techniques and their purposes
- Statistical concepts and mathematical operations
- Performance considerations for data processing
- Best practices for data analysis workflows
- Common patterns and methodologies

Code to explain:
{code}

Provide thorough explanations with practical insights and methodology explanations.''',
        
        'advanced': '''You are a principal data scientist explaining advanced data engineering to experienced practitioners.

Explain this complex data system covering:
- Advanced data processing architectures
- Performance optimization and scalability
- Statistical methodology and mathematical foundations
- Production data pipeline considerations
- Research methodologies and experimental design

Code to explain:
{code}

Provide expert-level analysis with theoretical foundations and production considerations.'''
    },
    
    'algorithm': {
        'beginner': '''You are a computer science teacher explaining algorithms to programming beginners.

Explain this algorithm step by step:
- What the algorithm is trying to accomplish
- How each step moves toward the solution
- Why we use these specific programming constructs
- What the time and space implications are
- How to trace through the execution

Code to explain:
{code}

Use simple language and walk through examples. Explain like you're teaching someone their first algorithm.''',
        
        'intermediate': '''You are an algorithms instructor explaining computational techniques to intermediate programmers.

Explain this algorithm focusing on:
- Algorithm design patterns and techniques
- Time and space complexity analysis
- Optimization strategies and trade-offs
- Comparison with alternative approaches
- Implementation best practices

Code to explain:
{code}

Provide detailed analysis with complexity considerations and optimization insights.''',
        
        'advanced': '''You are a computer science researcher explaining advanced algorithmic concepts to experienced developers.

Explain this complex algorithm covering:
- Advanced algorithmic techniques and theory
- Mathematical foundations and proof concepts
- Performance analysis and optimization strategies
- Research context and theoretical implications
- Production implementation considerations

Code to explain:
{code}

Provide expert-level analysis with theoretical depth and research insights.'''
    },
    
    'object_oriented': {
        'beginner': '''You are a programming instructor teaching object-oriented concepts to beginners.

Explain this object-oriented code focusing on:
- What classes and objects represent
- How methods and attributes work
- Why we organize code this way
- How different parts interact
- Real-world analogies for OOP concepts

Code to explain:
{code}

Use simple analogies and examples. Explain like you're introducing OOP for the first time.''',
        
        'intermediate': '''You are an experienced software engineer explaining OOP design to intermediate developers.

Explain this object-oriented system covering:
- Design patterns and architectural decisions
- Inheritance and composition strategies
- Encapsulation and abstraction principles
- Method design and interface considerations
- Code organization and maintainability

Code to explain:
{code}

Provide detailed explanations with design pattern insights and best practices.''',
        
        'advanced': '''You are a software architect explaining advanced OOP design to senior developers.

Explain this complex object-oriented system covering:
- Advanced design patterns and architectural principles
- Performance implications of design decisions
- Extensibility and maintainability strategies
- Enterprise patterns and scalability considerations
- Design trade-offs and architectural alternatives

Code to explain:
{code}

Provide expert-level analysis with architectural insights and design philosophy.'''
    },
    
    'general': {
        'beginner': '''You are a friendly Python instructor teaching programming fundamentals to beginners.

Explain this Python code line by line:
- What each line does in simple terms
- Why we write it this way
- What programming concepts are being used
- How the data flows through the program
- What the expected output would be

Code to explain:
{code}

Use simple language and explain every concept. Assume the student is new to programming.''',
        
        'intermediate': '''You are an experienced Python developer explaining code to intermediate programmers.

Explain this Python code focusing on:
- Programming patterns and techniques used
- Best practices and design decisions
- How different parts work together
- Alternative approaches and trade-offs
- Common pitfalls and optimization opportunities

Code to explain:
{code}

Provide detailed explanations with practical insights and best practices.''',
        
        'advanced': '''You are a senior Python engineer explaining complex code to experienced developers.

Explain this advanced Python implementation covering:
- Advanced language features and design patterns
- Performance implications and optimization strategies
- Architectural decisions and design trade-offs
- Production considerations and best practices
- Integration patterns and scalability aspects

Code to explain:
{code}

Provide expert-level analysis with architectural insights and advanced techniques.'''
    }
}

try:
    def get_dynamic_explanation_chains(llm, code):
        """Generate dynamic explanation chain based on code analysis"""
        
        # Analyze the code
        analyzer = ExplanationAnalyzer()
        code_type = analyzer.detect_code_type(code)
        complexity = analyzer.assess_complexity(code)
        key_concepts = analyzer.identify_key_concepts(code)
        
        # Select appropriate template
        template_category = DYNAMIC_EXPLANATION_TEMPLATES.get(code_type, DYNAMIC_EXPLANATION_TEMPLATES['general'])
        template_text = template_category.get(complexity, template_category['beginner'])
        
        # Enhance template with identified concepts
        if key_concepts:
            concept_guidance = f"\n\nPay special attention to explaining these concepts: {', '.join(key_concepts)}"
            template_text += concept_guidance
        
        # Create dynamic prompt template
        explanation_template = PromptTemplate(
            input_variables=["code"],
            template=template_text
        )
        
        # Return the same pattern: template | llm | parser
        return explanation_template | llm | StrOutputParser()
    
    # Backward compatibility
    def get_explanationchains(llm, code=None, use_dynamic=True):
        """
        Get explanation chain - supports both static and dynamic modes
        
        Args:
            llm: Language model instance
            code: Code to explain (required for dynamic mode)
            use_dynamic: Whether to use dynamic prompting (default: True)
        """
        if use_dynamic and code:
            return get_dynamic_explanation_chains(llm, code)
        else:
            # Fallback to original static template
            explanation_template = PromptTemplate(
                input_variables=['code'],
                template='''You're an experienced Python instructor.Explain the following code **line by line** in simple, beginner-friendly language:\n\n{code}'''
            )
            return explanation_template | llm | StrOutputParser()
    
except Exception as e:
    raise CustomException(e, sys)