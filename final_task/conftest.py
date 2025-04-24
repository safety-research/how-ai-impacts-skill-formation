import pytest
import sys
import os
import importlib.util

def pytest_addoption(parser):
    """Add command-line options to pytest."""
    parser.addoption(
        "--solution-file", 
        action="store",
        default="solution.py",
        help="Path to the solution file to test"
    )

# Create a global variable to hold the imported module
solution_module = None

def pytest_configure(config):
    """Configure pytest - import the solution module once at the start."""
    global solution_module
    
    # Get the file path from command line
    file_path = config.getoption("--solution-file")
    print(f"Loading solution module from: {file_path}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Solution file not found: {file_path}")
        
    # Get module name from filename (without extension)
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"Module name derived: {module_name}")
    
    # Import the module dynamically
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Could not create module spec for {file_path}")
    
    module = importlib.util.module_from_spec(spec)
    if module is None:
        raise ImportError(f"Could not create module from spec for {file_path}")
    
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    # Store the module globally
    solution_module = module
    
    # Make the module available in the global namespace of test_skill4.py
    sys.modules["solution_module"] = module
    
    # Verify module has expected functions
    print(f"Module loaded. Available attributes: {dir(module)}")