import os
import subprocess
import argparse
import time
import pathlib

# Available Claude models
MODELS = {
    "claude-3-7-sonnet-20250219": "anthropic",
    "claude-3-5-haiku-20241022": "anthropic",
    "claude-3-5-sonnet-20240620": "anthropic",
    "claude-3-opus-20240229": "anthropic",
    "claude-3-sonnet-20240229": "anthropic",
    "claude-3-haiku-20240307": "anthropic",
    "gpt-4.1-mini": "openai",
    "gpt-4o-mini-2024-07-18": "openai",
    "gpt-4o-2024-08-06": "openai",
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free": "together",
    "mistralai/Mistral-Small-24B-Instruct-2501": "together", 
    "deepseek-ai/DeepSeek-V3":"together"
}

def run_claude_solver(task_file, model, api_key=None):
    """Run the Claude API solver for a specific model."""

    provider = MODELS.get(model)
    name = pathlib.Path(task_file).stem
    output_path = f"auto-eval/solutions/{name}"
    os.makedirs(output_path, exist_ok=True) 

    output_file = f"{output_path}/solution_{model.split("/")[-1]}.py"
    if os.path.exists(output_file):
        print("Results already generated")
    else: 
        cmd = ["python", "auto-eval/multi_api_solver.py", task_file, "--model", model, "--provider", provider, "--output", output_file]
        
        if api_key:
            cmd.extend(["--api-key", api_key])
        
        print(f"Running task with {model}...")
        subprocess.run(cmd)
    
    return output_file

def main():
    parser = argparse.ArgumentParser(description="Solve tasks with multiple Claude models")
    parser.add_argument("task_file", help="Path to the Python file containing tasks")
    parser.add_argument("--models", nargs="+", choices=list(MODELS.keys()) + ["all"], 
                        default=["claude-3-7-sonnet-20250219"],
                        help="Claude models to use (default: claude-3-7-sonnet-20250219)")
    parser.add_argument("--api-key", help="Anthropic API key (default: from ANTHROPIC_API_KEY env var)")
    parser.add_argument("--run-tests", action="store_true", 
                        help="Run pytest on each solution after generation")
    parser.add_argument("--test-file", default="test_solution.py",
                        help="Path to pytest file (default: test_solution.py)")
    parser.add_argument("--results-dir", default="auto-eval/results")
    
    args = parser.parse_args()
    
    if args.models == ["all"]:
        models = list(MODELS.keys())
    else:
        models = args.models
    
    # Generate solutions with each model
    solutions = []
    for model in models:
        output_file = run_claude_solver(args.task_file, model, args.api_key)
        solutions.append((model, output_file))
        time.sleep(1)  # Small delay between API calls
    
    # Run tests if requested
    name = pathlib.Path(args.task_file).stem 
    results_path = f"{args.results_dir}/{name}"
    os.makedirs(results_path, exist_ok=True) 

    if args.run_tests:
        print("\n=== Running tests on solutions ===")
        for model, solution_file in solutions:
            with open(f"{results_path}/results-{model.split("/")[-1]}.txt", 'w') as f: 
                test_cmd = ["pytest", args.test_file, f"--solution-file={solution_file}", "-v"]
                result = subprocess.run(test_cmd, stdout=f, stderr=subprocess.STDOUT)
                
                if result.returncode == 0:
                    print(f"✅ {model} solution passed all tests")
                else:
                    print(f"❌ {model} solution failed some tests")

if __name__ == "__main__":
    main()