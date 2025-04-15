import os
import argparse
import time
import json
import requests
from anthropic import Anthropic
from openai import OpenAI

def load_tasks_from_file(file_path):
    """Load programming tasks from a Python file."""
    with open(file_path, 'r') as f:
        return f.read()

def get_api_key(provider, api_key=None):
    """Get API key from arguments or environment variables."""
    if api_key is not None:
        return api_key
    
    env_var_name = f"{provider.upper()}_API_KEY"
    api_key = os.environ.get(env_var_name)
    
    if api_key is None:
        raise ValueError(f"No API key provided. Set {env_var_name} environment variable or pass it as an argument.")
    
    return api_key

def extract_code_from_response(content):
    """Extract code from a response that might contain markdown code blocks."""
    if "```python" in content and "```" in content:
        start = content.find("```python") + len("```python")
        end = content.rfind("```")
        return content[start:end].strip()
    elif "```" in content:
        start = content.find("```") + len("```")
        end = content.rfind("```")
        return content[start:end].strip()
    return content

def create_prompt(task_content):
    """Create a standard prompt for all providers."""
    return f"""
You are a Python programming assistant. Below is a Python file containing programming tasks.
Please complete the tasks by implementing the missing code.
Return ONLY the complete code without any explanations or markdown formatting.

```python
{task_content}
```
"""

def solve_with_claude(task_content, model_name, api_key=None):
    """Use Claude API to solve the given programming task with the specified model."""
    api_key = get_api_key("anthropic", api_key)
    client = Anthropic(api_key=api_key)
    
    try:
        response = client.messages.create(
            model=model_name,
            max_tokens=4000,
            temperature=0.0,
            system="You are a skilled Python programmer. When completing code, return only the complete code with no explanations.",
            messages=[
                {"role": "user", "content": create_prompt(task_content)}
            ]
        )
        
        content = response.content[0].text
        return extract_code_from_response(content)
        
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return None

def solve_with_openai(task_content, model_name, api_key=None):
    """Use OpenAI API to solve the given programming task with the specified model."""
    api_key = get_api_key("openai", api_key)
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            max_tokens=4000,
            temperature=0.0,
            messages=[
                {"role": "system", "content": "You are a skilled Python programmer. When completing code, return only the complete code with no explanations."},
                {"role": "user", "content": create_prompt(task_content)}
            ]
        )
        
        content = response.choices[0].message.content
        return extract_code_from_response(content)
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None

def solve_with_together(task_content, model_name, api_key=None):
    """Use Together API to solve the given programming task with the specified model."""
    api_key = get_api_key("together", api_key)
    
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model_name,
        "max_tokens": 4000,
        "temperature": 0.0,
        "messages": [
            {"role": "system", "content": "You are a skilled Python programmer. When completing code, return only the complete code with no explanations."},
            {"role": "user", "content": create_prompt(task_content)}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        content = data["choices"][0]["message"]["content"]
        return extract_code_from_response(content)
        
    except Exception as e:
        print(f"Error calling Together API: {e}")
        return None

def save_solution(solution, output_file):
    """Save the solution to an output file."""
    with open(output_file, 'w') as f:
        f.write(solution)
    print(f"Solution saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Solve programming tasks using various LLM APIs")
    parser.add_argument("task_file", help="Path to the Python file containing tasks")
    parser.add_argument("--provider", choices=["anthropic", "openai", "together"], default="anthropic",
                        help="API provider to use (default: anthropic)")
    parser.add_argument("--model", help="Model to use (default depends on provider)")
    parser.add_argument("--output", help="Output file path (default: solution_{provider}_{model}.py)")
    parser.add_argument("--api-key", help="API key (default: from environment variables)")
    
    args = parser.parse_args()
    
    # Default models for each provider
    default_models = {
        "anthropic": "claude-3-7-sonnet-20250219",
        "openai": "gpt-4o",
        "together": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
    }
    
    # Set default model if not specified
    if args.model is None:
        args.model = default_models.get(args.provider)
    
    # Set default output file if not specified
    if not args.output:
        model_short = args.model.split('/')[-1] if '/' in args.model else args.model.split('-')[-1]
        args.output = f"solution_{args.provider}_{model_short}.py"
    
    # Load tasks
    task_content = load_tasks_from_file(args.task_file)
    
    # Map of provider names to solver functions
    solvers = {
        "anthropic": solve_with_claude,
        "openai": solve_with_openai,
        "together": solve_with_together
    }
    
    # Solve with selected provider
    print(f"Solving tasks with {args.provider} using {args.model}...")
    
    # Get the appropriate solver function
    solver_function = solvers.get(args.provider)
    if solver_function:
        solution = solver_function(task_content, args.model, args.api_key)
        
        if solution:
            # Save solution
            save_solution(solution, args.output)
        else:
            print("Failed to generate a solution.")
    else:
        print(f"Unsupported provider: {args.provider}")

if __name__ == "__main__":
    main()