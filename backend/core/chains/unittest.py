# from langchain.prompts import PromptTemplate
# import sys
# from dotenv import load_dotenv
# from langchain.schema.output_parser import StrOutputParser
# from src.logger import logging
# from src.exception import CustomException

# load_dotenv()

# try:
#     def unittestchains(llm):
#         logging.info("Process has Started...")
#         unittest_template = PromptTemplate(
#             input_variables=['code'],
#             template = '''You are a Senior Python Developer. 
#             Write Unit test code for the following python code:\n\n{code}'''
#         )

#         return unittest_template | llm | StrOutputParser()

# except Exception as e:
#     logging.info("There has been a Problem..")
#     raise CustomException(e,sys)

from langchain.prompts import PromptTemplate
import sys
from dotenv import load_dotenv
from langchain.schema.output_parser import StrOutputParser
from core.src.logger import logging
from core.src.exception import CustomException
import re
import ast

load_dotenv()

class TestAnalyzer:
    """Analyzes code to determine appropriate testing strategy"""
    
    @staticmethod
    def detect_code_type(code: str) -> str:
        """Detect code type for testing approach"""
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
    def assess_test_complexity(code: str) -> str:
        """Assess testing complexity needed"""
        lines = len([line for line in code.split('\n') if line.strip()])
        functions = code.count('def ')
        classes = code.count('class ')
        
        complexity_score = lines + (functions * 2) + (classes * 3)
        
        if complexity_score < 20:
            return 'simple'
        elif complexity_score < 50:
            return 'comprehensive'
        else:
            return 'enterprise'
    
    @staticmethod
    def identify_test_scenarios(code: str) -> dict:
        """Identify specific test scenarios needed"""
        scenarios = {}
        
        # Function analysis
        functions = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
        except:
            # Fallback regex method
            functions = re.findall(r'def\s+(\w+)', code)
        
        if functions:
            scenarios['functions'] = functions
        
        # Error handling scenarios
        if any(error in code for error in ['try:', 'except', 'raise']):
            scenarios['error_handling'] = ['exception_scenarios']
        
        # Database scenarios
        if any(db in code.lower() for db in ['execute', 'query', 'select', 'insert']):
            scenarios['database'] = ['connection_tests', 'query_validation', 'transaction_rollback']
        
        # File operation scenarios
        if any(file_op in code for file_op in ['open(', 'read(', 'write(']):
            scenarios['file_operations'] = ['file_existence', 'permissions', 'content_validation']
        
        # Web endpoint scenarios
        if '@app.route' in code or 'def ' in code and 'request' in code:
            scenarios['web_endpoints'] = ['status_codes', 'authentication', 'input_validation']
        
        # Data processing scenarios
        if any(data in code.lower() for data in ['pandas', 'dataframe', 'csv']):
            scenarios['data_processing'] = ['empty_data', 'invalid_formats', 'large_datasets']
        
        return scenarios

# Dynamic unit test templates
DYNAMIC_UNITTEST_TEMPLATES = {
    'flask_web': {
        'simple': '''You are a senior web application testing engineer specializing in Flask applications.

Generate comprehensive unit tests for this Flask code focusing on:
- HTTP endpoint testing with proper status codes
- Request/response validation and JSON format testing
- Authentication and session management testing
- Input validation and security testing
- Database integration testing with mocking
- Error handling for web-specific scenarios

Code to test:
{code}

Provide complete pytest test suite with:
- Flask test client setup and configuration
- Mocked database connections and external services
- Authentication flow testing
- Edge cases for web security (SQL injection, XSS prevention)
- Performance testing for web endpoints
- Integration tests for complete request/response cycles''',
        
        'comprehensive': '''You are a principal QA architect designing enterprise Flask application test suites.

Create comprehensive test coverage for this Flask system:
- Complete API endpoint testing with all HTTP methods
- Authentication and authorization testing across user roles
- Database transaction testing with rollback scenarios
- Security testing for OWASP Top 10 vulnerabilities
- Load testing and performance validation
- Integration testing with external services and APIs
- Error handling and graceful degradation testing

Code to test:
{code}

Design enterprise-grade test architecture with fixture management, test data factories, and comprehensive coverage analysis.'''
    },
    
    'data_science': {
        'simple': '''You are a senior data engineer specializing in Python data processing testing.

Generate comprehensive tests for this data science code focusing on:
- Data validation and schema testing
- Edge cases with empty, null, and malformed data
- Performance testing with large datasets
- Statistical accuracy validation
- Memory usage and efficiency testing
- Error handling for data processing failures

Code to test:
{code}

Provide complete test suite with:
- Mock data generation and fixtures
- Pandas DataFrame validation testing
- Statistical assertion testing
- Memory and performance benchmarking
- Data quality and integrity checks''',
        
        'comprehensive': '''You are a principal data scientist designing enterprise data pipeline test frameworks.

Create comprehensive test coverage for this data system:
- End-to-end data pipeline testing with realistic datasets
- Statistical model validation and accuracy testing
- Performance testing with production-scale data volumes
- Data quality monitoring and anomaly detection testing
- Integration testing with data sources and destinations
- Regression testing for model performance and accuracy

Code to test:
{code}

Design enterprise data testing architecture with automated data validation, model testing, and production monitoring.'''
    },
    
    'algorithm': {
        'simple': '''You are an algorithms testing specialist focusing on computational correctness and performance.

Generate comprehensive tests for this algorithmic code focusing on:
- Correctness testing with known input/output pairs
- Edge cases and boundary condition testing
- Performance testing and complexity validation
- Mathematical property testing and invariants
- Stress testing with large inputs
- Corner cases and algorithmic edge conditions

Code to test:
{code}

Provide complete test suite with:
- Property-based testing for algorithm correctness
- Performance benchmarking and complexity analysis
- Mathematical validation and invariant testing
- Comprehensive edge case coverage
- Stress testing with extreme inputs''',
        
        'comprehensive': '''You are a computer science researcher designing advanced algorithm testing frameworks.

Create comprehensive validation for this algorithmic system:
- Formal correctness verification with mathematical proofs
- Advanced property-based testing with generated test cases
- Performance regression testing and complexity analysis
- Comparative testing against alternative algorithms
- Numerical stability and precision testing
- Production performance monitoring and validation

Code to test:
{code}

Design research-grade testing framework with formal verification, automated property generation, and comprehensive performance analysis.'''
    },
    
    'database': {
        'simple': '''You are a database testing specialist focusing on Python database operations.

Generate comprehensive tests for this database code focusing on:
- Database connection and transaction testing
- Query correctness and performance validation
- Data integrity and constraint testing
- Error handling for database failures
- Connection pooling and resource management testing
- SQL injection prevention and security testing

Code to test:
{code}

Provide complete test suite with:
- Database fixture setup and teardown
- Transaction rollback testing
- Connection failure simulation
- Data validation and integrity checks
- Performance testing for database operations''',
        
        'comprehensive': '''You are a principal database architect designing enterprise database testing frameworks.

Create comprehensive test coverage for this database system:
- Full transaction lifecycle testing with rollback scenarios
- Concurrent access testing and deadlock prevention
- Database migration and schema evolution testing
- Performance testing under production load conditions
- Disaster recovery and backup validation testing
- Security testing for database access and permissions

Code to test:
{code}

Design enterprise database testing architecture with comprehensive transaction testing, performance validation, and production monitoring.'''
    },
    
    'object_oriented': {
        'simple': '''You are a senior software engineer specializing in object-oriented testing methodologies.

Generate comprehensive tests for this OOP code focusing on:
- Class instantiation and initialization testing
- Method behavior and state management testing
- Inheritance and polymorphism validation
- Encapsulation and access control testing
- Object lifecycle and resource management testing
- Design pattern implementation testing

Code to test:
{code}

Provide complete test suite with:
- Object mock and stub creation
- State-based and behavior-based testing
- Inheritance hierarchy validation
- Resource cleanup and memory management testing
- Design pattern correctness verification''',
        
        'comprehensive': '''You are a principal software architect designing enterprise OOP testing frameworks.

Create comprehensive test coverage for this object-oriented system:
- Advanced design pattern testing and architectural validation
- Concurrent object access and thread safety testing
- Performance testing for object creation and manipulation
- Memory management and garbage collection testing
- Integration testing for object collaboration patterns
- Extensibility and maintainability validation testing

Code to test:
{code}

Design enterprise OOP testing architecture with advanced mocking, comprehensive state validation, and architectural testing.'''
    },
    
    'general': {
        'simple': '''You are a senior Python testing engineer specializing in comprehensive test coverage.

Generate thorough unit tests for this Python code focusing on:
- Function behavior testing with various inputs
- Edge cases and boundary condition validation
- Error handling and exception testing
- Input validation and type checking
- Performance testing and optimization validation
- Code coverage and branch testing

Code to test:
{code}

Provide complete pytest test suite with:
- Comprehensive input/output validation
- Mock object creation and dependency injection
- Error scenario testing and exception handling
- Performance benchmarking and optimization validation
- Complete test coverage with edge cases''',
        
        'comprehensive': '''You are a principal software engineer designing enterprise Python testing frameworks.

Create comprehensive test coverage for this Python system:
- Advanced testing patterns and architectural validation
- Performance regression testing and optimization monitoring
- Integration testing with external dependencies and services
- Security testing and vulnerability assessment
- Production monitoring and operational testing
- Comprehensive documentation and test maintenance

Code to test:
{code}

Design enterprise Python testing architecture with advanced patterns, comprehensive coverage, and production validation.'''
    }
}

try:
    def get_dynamic_unittest_chains(llm, code):
        """Generate dynamic unit test chain based on code analysis"""
        
        # Analyze the code
        analyzer = TestAnalyzer()
        code_type = analyzer.detect_code_type(code)
        complexity = analyzer.assess_test_complexity(code)
        test_scenarios = analyzer.identify_test_scenarios(code)
        
        # Select appropriate template
        template_category = DYNAMIC_UNITTEST_TEMPLATES.get(code_type, DYNAMIC_UNITTEST_TEMPLATES['general'])
        template_text = template_category.get(complexity, template_category['simple'])
        
        # Enhance template with identified scenarios
        if test_scenarios:
            scenario_text = '\n'.join([f"- {k}: {', '.join(map(str, v))}" for k, v in test_scenarios.items()])
            scenario_guidance = f"\n\nSpecific test scenarios to cover:\n{scenario_text}"
            template_text += scenario_guidance
        
        # Create dynamic prompt template
        unittest_template = PromptTemplate(
            input_variables=["code"],
            template=template_text
        )
        
        # Return the same pattern: template | llm | parser
        return unittest_template | llm | StrOutputParser()
    
    # Backward compatibility
    def unittestchains(llm, code=None, use_dynamic=True):
        """
        Get unit test chain - supports both static and dynamic modes
        
        Args:
            llm: Language model instance
            code: Code to test (required for dynamic mode)
            use_dynamic: Whether to use dynamic prompting (default: True)
        """
        if use_dynamic and code:
            return get_dynamic_unittest_chains(llm, code)
        else:
            # Fallback to original static template
            unittest_template = PromptTemplate(
                input_variables=['code'],
                template='''You are a Senior Python Developer. 
                Write Unit test code for the following python code:\n\n{code}'''
            )
            return unittest_template | llm | StrOutputParser()

except Exception as e:
    raise CustomException(e, sys)