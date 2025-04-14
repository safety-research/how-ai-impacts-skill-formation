import os
import argparse
import anthropic
from anthropic import Anthropic
import time
import json

def load_tasks_from_file(file_path):
    """Load programming tasks from a Python file."""
    with open(file_path, 'r') as f:
        return f.read()

def solve_with_claude(task_content, model_name, api_key=None):
    """Use Claude API to solve the given programming task with the specified model."""
    if api_key is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key is None:
            raise ValueError("No API key provided. Set ANTHROPIC_API_KEY environment variable or pass it as an argument.")
    
    client = Anthropic(api_key=api_key)
    
    # Craft a prompt that asks Claude to complete the programming task
    prompt = f"""
You are a Python programming assistant. Below is a Python file containing programming tasks.
Please complete the tasks by implementing the missing code.
Return ONLY the complete code without any explanations or markdown formatting.

```python
{task_content}
```
"""

    try:
        response = client.messages.create(
            model=model_name,
            max_tokens=4000,
            temperature=0.0,  # Use deterministic output for consistent results
            system="You are a skilled Python programmer. When completing code, return only the complete code with no explanations.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract only the code from the response
        content = response.content[0].text
        # If code is in a code block, extract it
        if "```python" in content and "```" in content:
            start = content.find("```python") + len("```python")
            end = content.rfind("```")
            content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + len("```")
            end = content.rfind("```")
            content = content[start:end].strip()
            
        return content
        
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return None

def save_solution(solution, output_file):
    """Save the solution to an output file."""
    with open(output_file, 'w') as f:
        f.write(solution)
    print(f"Solution saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Solve programming tasks using Claude API")
    parser.add_argument("task_file", help="Path to the Python file containing tasks")
    parser.add_argument("--model", default="claude-3-7-sonnet-20250219", 
                        help="Claude model to use (default: claude-3-7-sonnet-20250219)")
    parser.add_argument("--output", help="Output file path (default: solution_{model}.py)")
    parser.add_argument("--api-key", help="Anthropic API key (default: from ANTHROPIC_API_KEY env var)")
    
    args = parser.parse_args()
    
    if not args.output:
        model_short = args.model.split('-')[-1]  # Extract just the model name part
        args.output = f"solution_{model_short}.py"
    
    # Load tasks
    task_content = load_tasks_from_file(args.task_file)
    
    # Solve with Claude
    print(f"Solving tasks with {args.model}...")
    solution = solve_with_claude(task_content, args.model, args.api_key)
    
    if solution:
        # Save solution
        save_solution(solution, args.output)
    else:
        print("Failed to generate a solution.")

if __name__ == "__main__":
    main()