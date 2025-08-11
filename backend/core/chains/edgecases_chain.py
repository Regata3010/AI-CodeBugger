# # chains/edge_case_chains.py
# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate
# from langchain.schema.output_parser import StrOutputParser
# from src.logger import logging
# from src.exception import CustomException
# import sys
# import ast
# import re
# from typing import Dict, List, Any
# from dotenv import load_dotenv

# load_dotenv()

# class EdgeCaseAnalyzer:
#     """Analyzes code to identify potential edge case scenarios"""
    
#     def __init__(self):
#         self.risk_patterns = {
#             'null_checks': [r'\.get\(', r'\[.*\]', r'\.pop\(', r'\.remove\('],
#             'loops': [r'for\s+\w+\s+in', r'while\s+'],
#             'divisions': [r'\/(?!=)', r'%', r'//'],
#             'recursion': [r'def\s+(\w+).*:\s*.*\1\('],
#             'external_calls': [r'requests\.', r'open\(', r'\.read\(', r'\.write\('],
#             'type_assumptions': [r'int\(', r'str\(', r'float\(', r'len\(']
#         }
    
#     def analyze_code_risks(self, code: str) -> Dict[str, List[str]]:
#         """Identify potential risk areas in code"""
#         try:
#             risks = {}
            
#             for risk_type, patterns in self.risk_patterns.items():
#                 found_risks = []
#                 for pattern in patterns:
#                     matches = re.findall(pattern, code, re.MULTILINE)
#                     if matches:
#                         found_risks.extend(matches)
                
#                 if found_risks:
#                     risks[risk_type] = found_risks
            
#             # AST analysis for deeper insights
#             try:
#                 tree = ast.parse(code)
#                 ast_risks = self._analyze_ast_risks(tree)
#                 risks.update(ast_risks)
#             except SyntaxError:
#                 logging.warning("Could not parse code for AST analysis")
            
#             return risks
            
#         except Exception as e:
#             logging.error(f"Error analyzing code risks: {str(e)}")
#             return {}
    
#     def _analyze_ast_risks(self, tree: ast.AST) -> Dict[str, List[str]]:
#         """Analyze AST for complex risk patterns"""
#         risks = {}
        
#         # Find function definitions and their complexity
#         functions = []
#         classes = []
#         loops = []
#         conditionals = []
        
#         for node in ast.walk(tree):
#             if isinstance(node, ast.FunctionDef):
#                 functions.append(node.name)
#             elif isinstance(node, ast.ClassDef):
#                 classes.append(node.name)
#             elif isinstance(node, (ast.For, ast.While)):
#                 loops.append(f"Line {node.lineno}")
#             elif isinstance(node, ast.If):
#                 conditionals.append(f"Line {node.lineno}")
        
#         if functions:
#             risks['functions'] = functions
#         if classes:
#             risks['classes'] = classes
#         if loops:
#             risks['loops_detected'] = loops
#         if conditionals:
#             risks['conditionals'] = conditionals
            
#         return risks
    
#     def get_function_signature(self, code: str) -> str:
#         """Extract function signatures for better edge case generation"""
#         try:
#             tree = ast.parse(code)
#             signatures = []
            
#             for node in ast.walk(tree):
#                 if isinstance(node, ast.FunctionDef):
#                     args = [arg.arg for arg in node.args.args]
#                     sig = f"def {node.name}({', '.join(args)})"
#                     signatures.append(sig)
            
#             return '\n'.join(signatures) if signatures else "No functions found"
            
#         except Exception as e:
#             return f"Could not extract signatures: {str(e)}"

# # Enhanced edge case generation chains
# try:
#     def get_edge_case_chains(llm):
#         """Generate comprehensive edge cases for code"""
#         logging.info("Edge case generation started...")
        
#         edge_case_template = PromptTemplate(
#             input_variables=["code", "risk_analysis", "function_signatures"],
#             template='''You are a senior QA engineer and testing expert specializing in finding edge cases that break code.

# Code to analyze:
# {code}

# Detected risk areas: {risk_analysis}
# Function signatures: {function_signatures}

# Generate comprehensive edge cases in the following categories:

# ## 1. 🔴 INPUT EDGE CASES
# - Empty inputs ([], "", None, 0)
# - Single element inputs
# - Very large inputs (performance stress)
# - Invalid types
# - Boundary values (min/max integers, empty strings)

# ## 2. 🟡 ERROR CONDITIONS  
# - Null pointer exceptions
# - Index out of bounds
# - Division by zero
# - File not found
# - Network timeouts
# - Invalid permissions

# ## 3. 🟢 BUSINESS LOGIC EDGE CASES
# - Invalid user states
# - Expired sessions/tokens
# - Insufficient resources
# - Concurrent access issues
# - Data corruption scenarios

# ## 4. 🔵 PERFORMANCE EDGE CASES
# - Memory exhaustion
# - CPU intensive operations
# - Large dataset processing
# - Infinite loops potential
# - Stack overflow conditions

# For each edge case, provide:
# 1. **Test Case Name**: Descriptive name
# 2. **Input Example**: Specific test data
# 3. **Expected Behavior**: What should happen
# 4. **Potential Failure**: How it might break
# 5. **Pytest Code**: Executable test case

# Format as executable Python test cases using pytest with assertions.'''
#         )
        
#         return edge_case_template | llm | StrOutputParser()
    
#     def get_leetcode_style_chains(llm):
#         """Generate LeetCode-style test cases with difficulty levels"""
#         logging.info("LeetCode-style test generation started...")
        
#         leetcode_template = PromptTemplate(
#             input_variables=["code", "complexity_score", "function_type"],
#             template='''You are a LeetCode problem creator specializing in comprehensive test case design.

# Code function: {code}
# Complexity score: {complexity_score}
# Function type: {function_type}

# Create LeetCode-style test cases with increasing difficulty:

# ## 🟢 EASY CASES (Basic functionality)
# Example:
# ```python
# def test_basic_functionality():
#     assert function_name([1, 2, 3]) == expected_output
#     assert function_name([]) == expected_empty_output
# ```

# ## 🟡 MEDIUM CASES (Edge conditions)
# Example:
# ```python
# def test_edge_conditions():
#     assert function_name([1]) == single_element_output
#     assert function_name([1, 1, 1]) == duplicate_output
#     assert function_name(None) raises appropriate_exception
# ```

# ## 🔴 HARD CASES (Stress testing)
# Example:
# ```python
# def test_performance_limits():
#     large_input = list(range(10000))
#     result = function_name(large_input)
#     assert result is not None
#     assert len(result) <= expected_max_length
# ```

# ## 🟣 EXPERT CASES (Corner cases)
# Example:
# ```python
# def test_corner_cases():
#     # Test mathematical edge cases
#     assert function_name([sys.maxsize]) handles_overflow
#     # Test memory edge cases  
#     assert function_name(['a' * 10**6]) handles_large_strings
# ```

# Include performance benchmarks and memory usage tests where relevant.
# Provide at least 15 comprehensive test cases covering all difficulty levels.'''
#         )
        
#         return leetcode_template | llm | StrOutputParser()
    
#     def get_interactive_test_chains(llm):
#         """Generate interactive test scenarios for real-time testing"""
#         logging.info("Interactive test generation started...")
        
#         interactive_template = PromptTemplate(
#             input_variables=["code", "user_input", "test_focus"],
#             template='''You are an interactive testing assistant helping developers test their code in real-time.

# Code under test: {code}
# User's testing focus: {test_focus}
# User input/question: {user_input}

# Generate specific, actionable test cases based on the user's focus area:

# ## 🎯 TARGETED TEST CASES
# Create 5-7 test cases specifically for: {test_focus}

# ## 🧪 INTERACTIVE TESTING APPROACH
# 1. **Quick Smoke Tests**: Fast tests to verify basic functionality
# 2. **Focused Edge Cases**: Tests specific to user's concern area
# 3. **Debugging Helpers**: Tests that help isolate issues
# 4. **Performance Checks**: Simple performance validation

# ## 📊 TEST EXECUTION PLAN
# Provide a step-by-step testing approach:
# 1. Run basic functionality tests first
# 2. Gradually increase complexity
# 3. Focus on the user's specific concern area
# 4. Suggest improvements based on test results

# Format all tests as executable Python code with clear explanations.
# Make tests copy-pasteable and immediately runnable.'''
#         )
        
#         return interactive_template | llm | StrOutputParser()

# except Exception as e:
#     logging.error("Error in edge case chains...")
#     raise CustomException(e, sys)

# # Test execution utilities
# class TestExecutor:
#     """Execute generated test cases safely"""
    
#     def __init__(self):
#         self.timeout_seconds = 10
#         self.max_memory_mb = 100
    
#     def execute_test_case(self, test_code: str, original_code: str) -> Dict[str, Any]:
#         """Execute a single test case and return results"""
#         try:
#             # Create safe execution environment
#             namespace = {
#                 '__builtins__': __builtins__,
#                 'sys': __import__('sys'),
#                 'pytest': __import__('pytest')
#             }
            
#             # Execute original code first
#             exec(original_code, namespace)
            
#             # Execute test case
#             exec(test_code, namespace)
            
#             return {
#                 'status': 'passed',
#                 'execution_time': 0.0,  # Would implement timing
#                 'memory_usage': 0,      # Would implement memory tracking
#                 'output': 'Test executed successfully'
#             }
            
#         except Exception as e:
#             return {
#                 'status': 'failed',
#                 'error': str(e),
#                 'error_type': type(e).__name__,
#                 'output': f'Test failed with error: {str(e)}'
#             }
    
#     def benchmark_performance(self, code: str, test_inputs: List[Any]) -> Dict[str, Any]:
#         """Benchmark code performance with different inputs"""
#         import time
#         import tracemalloc
        
#         results = {}
        
#         for i, test_input in enumerate(test_inputs):
#             try:
#                 # Memory tracking
#                 tracemalloc.start()
#                 start_time = time.time()
                
#                 # Execute code (would need safer execution)
#                 # result = execute_code_with_input(code, test_input)
                
#                 execution_time = time.time() - start_time
#                 current, peak = tracemalloc.get_traced_memory()
#                 tracemalloc.stop()
                
#                 results[f'test_{i}'] = {
#                     'execution_time': execution_time,
#                     'memory_peak': peak / 1024 / 1024,  # MB
#                     'input_size': len(str(test_input)),
#                     'status': 'completed'
#                 }
                
#             except Exception as e:
#                 results[f'test_{i}'] = {
#                     'status': 'failed',
#                     'error': str(e)
#                 }
        
#         return results
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from core.src.logger import logging
from core.src.exception import CustomException
import sys
import ast
import re
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

# COMPLETE DYNAMIC EDGE CASE TEMPLATES
DYNAMIC_EDGE_CASE_TEMPLATES = {
    'cybersecurity': {
        'simple': '''You are a senior cybersecurity analyst specializing in secure code edge case testing.

Focus on security-specific edge cases:
- Cryptographic implementation failures and key management issues
- Authentication bypass and privilege escalation scenarios
- Input validation bypass and injection attack vectors
- Timing attacks and side-channel vulnerability testing
- Encryption/decryption edge cases and key rotation failures

Code to analyze:
{code}

Generate comprehensive security test cases focusing on cryptographic failures and attack simulation.''',
        
        'complex': '''You are a principal security researcher designing advanced threat simulation frameworks.

Advanced cybersecurity edge cases:
- Advanced persistent threat simulation and multi-vector attacks
- Zero-day vulnerability discovery and exploit development
- Enterprise security architecture testing and compliance validation
- Nation-state level attack simulation and defense testing

Code to analyze:
{code}

Design research-grade security testing with advanced threat modeling and comprehensive attack simulation.'''
    },
    
    'machine_learning': {
        'simple': '''You are a senior ML engineer specializing in machine learning model edge case testing.

Focus on ML-specific edge cases:
- Model accuracy degradation with edge case inputs
- Training data corruption and adversarial examples
- Memory exhaustion with large models and datasets
- Model inference failures and prediction edge cases
- Feature engineering failures and data preprocessing issues

Code to analyze:
{code}

Generate comprehensive ML test cases focusing on model robustness and data quality validation.''',
        
        'complex': '''You are a principal ML architect designing enterprise ML system testing frameworks.

Advanced machine learning edge cases:
- Production model drift and performance degradation testing
- Adversarial attack resistance and model security testing
- Distributed training failures and scaling edge cases
- Real-time inference performance and latency testing

Code to analyze:
{code}

Design enterprise ML testing with advanced model validation and production monitoring scenarios.'''
    },
    
    'data_science': {
        'simple': '''You are a senior data quality engineer specializing in data processing edge case testing.

Focus on data-specific edge cases:
- Corrupted data formats and encoding issues
- Memory exhaustion with large datasets
- Statistical edge cases and numerical instability
- Data type mismatches and schema violations
- Missing data patterns and null value handling

Code to analyze:
{code}

Generate comprehensive test cases for data quality, performance limits, and statistical accuracy validation.''',
        
        'complex': '''You are a principal data architect designing enterprise data pipeline testing frameworks.

Advanced data processing edge cases:
- Production-scale data volume testing
- Data corruption and recovery scenarios
- Distributed processing failure modes
- Real-time streaming edge cases and backpressure

Code to analyze:
{code}

Design enterprise data testing with advanced failure simulation and production monitoring validation.'''
    },
    
    'devops': {
        'simple': '''You are a senior DevOps engineer specializing in infrastructure code edge case testing.

Focus on DevOps-specific edge cases:
- Container deployment failures and resource exhaustion
- Configuration management errors and environment inconsistencies
- CI/CD pipeline failures and deployment rollback scenarios
- Infrastructure scaling issues and resource limit testing
- Service discovery failures and network connectivity issues

Code to analyze:
{code}

Generate comprehensive infrastructure test cases focusing on deployment failures and operational edge cases.''',
        
        'complex': '''You are a principal cloud architect designing enterprise infrastructure testing frameworks.

Advanced DevOps edge cases:
- Multi-cloud deployment failures and disaster recovery testing
- Advanced orchestration failures and complex dependency testing
- Enterprise security compliance and infrastructure validation
- Production incident simulation and chaos engineering scenarios

Code to analyze:
{code}

Design enterprise infrastructure testing with advanced failure simulation and production validation.'''
    },
    
    'financial_systems': {
        'simple': '''You are a senior fintech engineer specializing in financial system edge case testing.

Focus on financial-specific edge cases:
- Numerical precision errors in financial calculations
- Market data corruption and real-time processing failures
- Transaction integrity and double-spending prevention
- Regulatory compliance violations and audit trail failures
- Currency conversion errors and exchange rate edge cases

Code to analyze:
{code}

Generate comprehensive financial test cases focusing on calculation accuracy and transaction integrity.''',
        
        'complex': '''You are a principal quantitative finance architect designing enterprise trading system testing.

Advanced financial system edge cases:
- High-frequency trading edge cases and latency testing
- Risk management failures and portfolio optimization issues
- Regulatory compliance testing and stress testing scenarios
- Market crash simulation and extreme volatility testing

Code to analyze:
{code}

Design enterprise financial testing with advanced market simulation and regulatory compliance validation.'''
    },
    
    'flask_web': {
        'simple': '''You are a senior web security QA engineer specializing in Flask application edge case testing.

Focus on web-specific edge cases:
- Authentication bypass scenarios and session manipulation
- SQL injection and XSS attack vectors
- Malformed HTTP requests and invalid JSON payloads
- File upload attacks and path traversal scenarios
- Rate limiting bypass and CSRF token manipulation
- Database connection failures and timeout scenarios

Code to analyze:
{code}

Generate executable pytest test cases focusing on web security vulnerabilities and Flask-specific failure modes.''',
        
        'complex': '''You are a principal security architect designing advanced web application penetration testing.

Advanced Flask security edge cases:
- Multi-stage attack vectors and complex exploit chains
- Advanced authentication bypass and privilege escalation
- Enterprise security testing with compliance requirements
- Production load testing and denial of service scenarios

Code to analyze:
{code}

Design enterprise-grade security test suite with advanced attack simulation and comprehensive vulnerability assessment.'''
    },
    
    'database': {
        'simple': '''You are a database testing specialist focusing on database operation edge cases.

Focus on database-specific edge cases:
- Connection failures and timeout scenarios
- Transaction rollback and deadlock situations
- Data integrity violations and constraint failures
- SQL injection prevention and parameter validation
- Concurrent access and race condition testing

Code to analyze:
{code}

Generate comprehensive database edge case tests with transaction management and connection failure simulation.''',
        
        'complex': '''You are a principal database architect designing enterprise database testing frameworks.

Advanced database edge cases:
- Distributed transaction failures and consistency testing
- High-concurrency scenarios and performance degradation
- Database migration and schema evolution edge cases
- Disaster recovery and backup validation scenarios

Code to analyze:
{code}

Design enterprise database testing with advanced transaction scenarios and production failure simulation.'''
    },
    
    'algorithm': {
        'simple': '''You are an algorithms testing specialist focusing on computational edge cases.

Focus on algorithmic edge cases:
- Mathematical boundary conditions and overflow scenarios
- Algorithmic complexity stress testing with large inputs
- Numerical precision and floating-point edge cases
- Recursive depth limits and stack overflow conditions
- Performance degradation and worst-case scenarios

Code to analyze:
{code}

Generate comprehensive algorithmic test cases with mathematical validation and performance stress testing.''',
        
        'complex': '''You are a computer science researcher designing advanced algorithm validation frameworks.

Advanced algorithmic edge cases:
- Formal verification scenarios and mathematical proof validation
- Advanced complexity analysis with adversarial inputs
- Numerical stability testing and precision analysis
- Parallel processing edge cases and concurrent algorithm testing

Code to analyze:
{code}

Design research-grade algorithmic testing with formal verification and advanced performance analysis.'''
    },
    
    'general': {
        'simple': '''You are a senior QA engineer specializing in comprehensive edge case testing.

Focus on general programming edge cases:
- Input validation failures and type error scenarios
- Resource exhaustion and memory limit testing
- Error handling and exception propagation scenarios
- Boundary conditions and limit testing
- Performance degradation and timeout scenarios

Code to analyze:
{code}

Generate comprehensive edge case tests covering input validation, error handling, and performance limits.''',
        
        'complex': '''You are a principal software engineer designing enterprise edge case testing frameworks.

Advanced edge case testing:
- Production failure simulation and recovery testing
- Advanced error propagation and system resilience
- Security vulnerability testing and attack simulation
- Performance regression and optimization validation

Code to analyze:
{code}

Design enterprise edge case testing with advanced failure simulation and comprehensive system validation.'''
    }
}

class EdgeCaseAnalyzer:
    """Analyzes code to identify potential edge case scenarios"""
    
    def __init__(self):
        self.risk_patterns = {
            'null_checks': [r'\.get\(', r'\[.*\]', r'\.pop\('],
            'divisions': [r'\/(?!=)', r'%', r'//'],
            'loops': [r'for\s+\w+\s+in', r'while\s+'],
            'external_calls': [r'requests\.', r'open\(', r'\.read\('],
            'type_conversions': [r'int\(', r'str\(', r'float\(']
        }
    
    def detect_code_type(self, code: str) -> str:
        """Detect code type for edge case focus"""
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
        
        else:
            return 'general'
    
    def assess_complexity(self, code: str) -> str:
        """Assess code complexity for edge case depth"""
        lines = len([line for line in code.split('\n') if line.strip()])
        functions = code.count('def ')
        complexity_score = lines + (functions * 3)
        
        return 'complex' if complexity_score > 50 else 'simple'
    
    def analyze_code_risks(self, code: str) -> Dict[str, List[str]]:
        """Identify potential risk areas in code"""
        try:
            risks = {}
            
            for risk_type, patterns in self.risk_patterns.items():
                found_risks = []
                for pattern in patterns:
                    matches = re.findall(pattern, code, re.MULTILINE)
                    if matches:
                        found_risks.extend(matches)
                
                if found_risks:
                    risks[risk_type] = found_risks
            
            # Get function info
            try:
                tree = ast.parse(code)
                functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                if functions:
                    risks['functions'] = functions
            except SyntaxError:
                logging.warning("Could not parse code for function analysis")
            
            return risks
            
        except Exception as e:
            logging.error(f"Error analyzing code risks: {str(e)}")
            return {}

try:
    def get_dynamic_edge_case_chains(llm, code):
        """Generate dynamic edge case chain based on code analysis"""
        
        # Analyze the code
        analyzer = EdgeCaseAnalyzer()
        code_type = analyzer.detect_code_type(code)
        complexity = analyzer.assess_complexity(code)
        risk_analysis = analyzer.analyze_code_risks(code)
        
        # Select appropriate template
        template_category = DYNAMIC_EDGE_CASE_TEMPLATES.get(code_type, DYNAMIC_EDGE_CASE_TEMPLATES['general'])
        template_text = template_category.get(complexity, template_category['simple'])
        
        # Convert risk analysis to safe string format
        risk_summary = []
        for risk_type, details in risk_analysis.items():
            risk_summary.append(f"- {risk_type}: {', '.join(map(str, details))}")
        
        risk_text = '\n'.join(risk_summary) if risk_summary else "No specific risks detected"
        
        # Enhance template with analysis results
        enhanced_template = f"""{template_text}

Detected risk areas:
{risk_text}

Focus on the specific risk patterns identified above and generate executable pytest test cases."""
        
        # Create dynamic prompt template
        edge_case_template = PromptTemplate(
            input_variables=["code"],
            template=enhanced_template
        )
        
        return edge_case_template | llm | StrOutputParser()
    
    def get_edge_case_chains(llm, code=None, use_dynamic=True):
        """Get edge case chain with dynamic support"""
        if use_dynamic and code:
            return get_dynamic_edge_case_chains(llm, code)
        else:
            # Static fallback
            edge_case_template = PromptTemplate(
                input_variables=["code"],
                template='''You are a senior QA engineer specializing in finding edge cases that break code.

Code to analyze:
{code}

Generate comprehensive edge cases covering input validation, error handling, and performance limits.

Format as clean pytest test cases.'''
            )
            return edge_case_template | llm | StrOutputParser()

except Exception as e:
    raise CustomException(e, sys)