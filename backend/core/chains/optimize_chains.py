# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# from langchain.schema.output_parser import StrOutputParser
# from src.logger import logging
# from src.exception import CustomException
# import sys
# from dotenv import load_dotenv

# load_dotenv()

# try:
#     def get_optimized_chains(llm):
#           logging.info("Process has Started..")
#           optimized_template = PromptTemplate(
#           input_variables=["code"],
#           template='''You are a senior Python engineer. Refactor the code below to make it cleaner, more readable, 
#                     and more efficient:\n\n{code}'''
#           )
#           return optimized_template | llm | StrOutputParser()


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

load_dotenv()

class OptimizationAnalyzer:
    """Analyzes code to determine optimization focus areas"""
    
    @staticmethod
    def detect_code_type(code: str) -> str:
        """Detect code type for optimization focus"""
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
        
        # API/Service Detection
        elif any(api in code_lower for api in ['requests', 'http', 'api', 'json']):
            return 'api_service'
        
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
    def detect_optimization_opportunities(code: str) -> dict:
        """Detect specific optimization opportunities with line numbers"""
        opportunities = {}
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_clean = line.strip()
            
            # Loop optimization opportunities
            if re.search(r'for.*in.*range\(len\(', line_clean):
                if 'loop_optimization' not in opportunities:
                    opportunities['loop_optimization'] = []
                opportunities['loop_optimization'].append(f"Line {i}: Use enumerate() instead of range(len())")
            
            # List comprehension opportunities
            if '.append(' in line_clean and any(prev_line.strip().startswith('for ') for prev_line in lines[max(0, i-3):i]):
                if 'list_comprehension' not in opportunities:
                    opportunities['list_comprehension'] = []
                opportunities['list_comprehension'].append(f"Line {i}: Consider list comprehension")
            
            # Database optimization
            if 'execute(' in line_clean and 'for ' in ' '.join(lines[max(0, i-5):i+5]):
                if 'database_optimization' not in opportunities:
                    opportunities['database_optimization'] = []
                opportunities['database_optimization'].append(f"Line {i}: Consider batch operations")
            
            # Memory optimization
            if '+=' in line_clean and 'str' in line_clean.lower():
                if 'string_optimization' not in opportunities:
                    opportunities['string_optimization'] = []
                opportunities['string_optimization'].append(f"Line {i}: String concatenation inefficiency")
            
            # Pandas optimization
            if '.apply(' in line_clean and 'pandas' in code.lower():
                if 'vectorization' not in opportunities:
                    opportunities['vectorization'] = []
                opportunities['vectorization'].append(f"Line {i}: Consider vectorized operations")
            
            # Function call optimization
            if line_clean.count('(') > 3:
                if 'function_optimization' not in opportunities:
                    opportunities['function_optimization'] = []
                opportunities['function_optimization'].append(f"Line {i}: Multiple function calls - consider caching")
        
        return opportunities
    
    @staticmethod
    def calculate_performance_metrics(code: str) -> dict:
        """Calculate basic performance metrics"""
        lines = code.split('\n')
        metrics = {
            'total_lines': len([line for line in lines if line.strip()]),
            'function_count': code.count('def '),
            'class_count': code.count('class '),
            'loop_count': code.count('for ') + code.count('while '),
            'conditional_count': code.count('if '),
            'complexity_estimate': 'low'
        }
        
        # Estimate complexity
        complexity_score = (metrics['function_count'] * 2 + 
                          metrics['class_count'] * 3 + 
                          metrics['loop_count'] * 2 + 
                          metrics['conditional_count'])
        
        if complexity_score > 20:
            metrics['complexity_estimate'] = 'high'
        elif complexity_score > 10:
            metrics['complexity_estimate'] = 'medium'
        
        return metrics

DYNAMIC_OPTIMIZATION_TEMPLATES = {
    'flask_web': {
        'simple': '''You are a senior Flask performance engineer specializing in web application optimization.

Focus on Flask-specific optimizations:
- Database query optimization and connection pooling
- Caching strategies for improved response times
- Session management and cookie optimization
- Request/response optimization and middleware efficiency

Code to optimize:
{code}

Provide optimized Flask code with performance improvements, database optimization, and scalability enhancements.''',
        
        'complex': '''You are a principal architect specializing in enterprise Flask application optimization.

Enterprise Flask optimization focus:
- Advanced caching strategies and database connection pooling
- Asynchronous processing and background task optimization
- Load balancing considerations and horizontal scaling
- API performance optimization and rate limiting

Code to optimize:
{code}

Provide enterprise-grade optimized code with comprehensive performance strategy and scalability architecture.'''
    },
    
    'data_science': {
        'simple': '''You are a senior data engineer specializing in Python data processing optimization.

Focus on data science performance:
- Pandas vectorization and efficient data operations
- NumPy array optimization and memory efficiency
- Loop elimination and list comprehension optimization
- Memory management for large datasets

Code to optimize:
{code}

Provide optimized code focusing on vectorized operations, memory efficiency, and faster data processing.''',
        
        'complex': '''You are a principal data architect optimizing enterprise-scale data processing systems.

Enterprise data optimization:
- Distributed computing optimization and parallel processing
- Memory optimization for big data processing
- Data pipeline optimization and streaming efficiency
- Production data system performance and monitoring

Code to optimize:
{code}

Provide enterprise data processing optimization with scalable architecture and production-ready performance enhancements.'''
    },
    
    'algorithm': {
        'simple': '''You are an algorithms optimization specialist focusing on computational efficiency.

Focus on algorithmic optimization:
- Time complexity reduction and algorithm efficiency
- Space complexity optimization and memory usage
- Loop optimization and iteration efficiency
- Data structure selection for optimal performance

Code to optimize:
{code}

Provide optimized code with improved time and space complexity, efficient algorithms, and performance benchmarks.''',
        
        'complex': '''You are a computer science researcher specializing in advanced algorithm optimization.

Advanced algorithmic optimization:
- Advanced data structures and algorithm selection
- Mathematical optimization and numerical efficiency
- Parallel processing and concurrent algorithm design
- Cache-efficient algorithms and memory access patterns

Code to optimize:
{code}

Provide research-grade algorithmic optimization with advanced techniques and comprehensive performance analysis.'''
    },
    
    'database': {
        'simple': '''You are a database performance specialist focusing on Python database operations.

Focus on database optimization:
- Query optimization and efficient SQL generation
- Connection pooling and resource management
- Batch operations and bulk data processing
- Transaction optimization and commit strategies

Code to optimize:
{code}

Provide optimized database code with efficient query patterns, connection management, and scalable data access.''',
        
        'complex': '''You are a principal database architect optimizing enterprise database systems.

Enterprise database optimization:
- Advanced query optimization and execution planning
- Distributed database optimization and sharding strategies
- High-performance data access patterns and caching
- Database connection optimization and load balancing

Code to optimize:
{code}

Provide enterprise database optimization with advanced performance strategies and scalable architecture.'''
    },
    
    'object_oriented': {
        'simple': '''You are a senior software engineer specializing in object-oriented design optimization.

Focus on OOP optimization:
- Class design optimization and inheritance efficiency
- Method optimization and performance improvements
- Memory usage optimization in object creation
- Design pattern implementation for better performance

Code to optimize:
{code}

Provide optimized object-oriented code with improved class design, better performance, and enhanced maintainability.''',
        
        'complex': '''You are a principal software architect optimizing enterprise object-oriented systems.

Enterprise OOP optimization:
- Advanced design pattern optimization and architectural efficiency
- Performance optimization for large-scale object systems
- Memory optimization and garbage collection efficiency
- Concurrent object design and thread safety optimization

Code to optimize:
{code}

Provide enterprise-grade object-oriented optimization with advanced architectural patterns and performance strategies.'''
    },
    
    'general': {
        'simple': '''You are a senior Python performance engineer focusing on code optimization.

Focus on general Python optimization:
- Code efficiency and performance improvements
- Memory usage optimization and resource management
- Loop optimization and iteration efficiency
- Function optimization and call overhead reduction

Code to optimize:
{code}

Provide optimized Python code with performance improvements, memory optimization, and cleaner code structure.''',
        
        'complex': '''You are a principal software engineer optimizing enterprise Python systems.

Enterprise Python optimization:
- Advanced performance optimization and profiling integration
- Memory optimization and resource efficiency for production systems
- Concurrent programming optimization and parallel processing
- Production system performance and monitoring integration

Code to optimize:
{code}

Provide enterprise-level Python optimization with comprehensive performance strategy and production-ready architecture.'''
    }
}

try:
    def get_dynamic_optimization_chains(llm, code):
        """Generate dynamic optimization chain based on code analysis"""
        
        # Analyze the code
        analyzer = OptimizationAnalyzer()
        code_type = analyzer.detect_code_type(code)
        complexity = analyzer.assess_complexity(code)
        optimization_opportunities = analyzer.detect_optimization_opportunities(code)
        performance_metrics = analyzer.calculate_performance_metrics(code)
        
        # Select appropriate template
        template_category = DYNAMIC_OPTIMIZATION_TEMPLATES.get(code_type, DYNAMIC_OPTIMIZATION_TEMPLATES['general'])
        template_text = template_category.get(complexity, template_category['simple'])
        
        # Enhance template with specific analysis
        enhanced_template = f"""{template_text}

DETECTED OPTIMIZATION OPPORTUNITIES:
{chr(10).join([f"- {area}: {', '.join(issues)}" for area, issues in optimization_opportunities.items()])}

PERFORMANCE METRICS:
- Code complexity: {performance_metrics['complexity_estimate']}
- Total functions: {performance_metrics['function_count']}
- Loop count: {performance_metrics['loop_count']}
- Lines of code: {performance_metrics['total_lines']}

Focus on the specific line-level optimizations identified above."""
        
        # Create dynamic prompt template
        optimization_template = PromptTemplate(
            input_variables=["code"],
            template=enhanced_template
        )
        
        # Return the same pattern: template | llm | parser
        return optimization_template | llm | StrOutputParser()
    
    # Backward compatibility - keep original function but add dynamic option
    def get_optimized_chains(llm, code=None, use_dynamic=True):
        """
        Get optimization chain - supports both static and dynamic modes
        
        Args:
            llm: Language model instance
            code: Code to optimize (required for dynamic mode)
            use_dynamic: Whether to use dynamic prompting (default: True)
        """
        if use_dynamic and code:
            return get_dynamic_optimization_chains(llm, code)
        else:
            # Fallback to original static template
            optimization_template = PromptTemplate(
                input_variables=["code"],
                template='''You are a senior Python engineer. Refactor the code below to make it cleaner, more readable, 
                          and more efficient:\n\n{code}'''
            )
            return optimization_template | llm | StrOutputParser()
    
except Exception as e:
    raise CustomException(e, sys)