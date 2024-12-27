import llm
import sys
import subprocess

# Define the evaluator and generator prompts
evaluator_prompt = """Evaluate this following code implementation for:
1. code correctness
2. time complexity
3. style and best practices

You should be evaluating only and not attempting to solve the task.
Only output "PASS" if all criteria are met and you have no further suggestions for improvements.
Output your evaluation concisely in the following format.

<evaluation>PASS, NEEDS_IMPROVEMENT, or FAIL</evaluation>
<feedback>
What needs improvement and why.
</feedback>
"""

generator_prompt = """Your goal is to complete the task based on <user input>. If there are feedback 
from your previous generations, you should reflect on them to improve your solution.

Output your answer concisely in the following format: 

<thoughts>
[Your understanding of the task and feedback and how you plan to improve]
</thoughts>

<response>
[Your code implementation here]
</response>
"""

pr_title_prompt = """Generate a concise title for a pull request based on the following code and task:
Task: <task>
Code: <code>
"""

pr_body_prompt = """Generate a detailed description for a pull request based on the following code and task:
Task: <task>
Code: <code>
"""

commit_message_prompt = """Generate a commit message for the following code and task:
Task: <task>
Code: <code>
"""

branch_name_prompt = """Generate a concise branch name for a feature based on the following task:
Task: <task>
"""

# Function to read the task from input
def read_task(input_source):
    if input_source == 'stdin':
        print("Please enter the task (end with EOF):")
        task = sys.stdin.read().strip()
    else:
        with open(input_source, 'r') as file:
            task = file.read().strip()
    return task

# Function to generate code based on the generator prompt
def generate_code(model, prompt, task, context=""):
    if context:
        full_prompt = f"{prompt}\n{context}\nTask: {task}"
    else:
        full_prompt = f"{prompt}\nTask: {task}"
    response = model.prompt(full_prompt)
    
    thoughts = response.text().split("<thoughts>")[1].split("</thoughts>")[0].strip()
    result = response.text().split("<response>")[1].split("</response>")[0].strip()
    
    print("\n=== GENERATION START ===")
    print(f"Thoughts:\n{thoughts}\n")
    print(f"Generated:\n{result}")
    print("=== GENERATION END ===\n")
    
    return thoughts, result

# Function to evaluate the generated code
def evaluate_code(model, evaluator_prompt, content, task):
    full_prompt = f"{evaluator_prompt}\nOriginal task: {task}\nContent to evaluate: {content}"
    response = model.prompt(full_prompt)
    
    evaluation = response.text().split("<evaluation>")[1].split("</evaluation>")[0].strip()
    feedback = response.text().split("<feedback>")[1].split("</feedback>")[0].strip()
    
    print("\n=== EVALUATION START ===")
    print(f"Status: {evaluation}")
    print(f"Feedback: {feedback}")
    print("=== EVALUATION END ===\n")
    
    return evaluation, feedback

# Function to save code to a file
def save_code_to_file(code, filename='generated_code.py'):
    with open(filename, 'w') as f:
        f.write(code)
    print(f"Code saved to {filename}")
    return filename

# Function to create a GitHub pull request using Git commands
def create_pull_request(filename, pr_title, pr_body, commit_message):
    """Assumes you're in a git repository with the proper SSH setup."""
    branch_name = generate_branch_name(model, task)  # Generate branch name using LLM

    # Create a new branch for the changes
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)

    # Add the generated code file
    subprocess.run(["git", "add", filename], check=True)

    # Commit the changes using the generated commit message
    subprocess.run(["git", "commit", "-m", commit_message], check=True)

    # Push the new branch to the repository
    subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)

    # Create the pull request using Github CLI
    subprocess.run(["gh", "pr", "create", "--title", pr_title, "--body", pr_body, "--base", "main"], check=True)

# Function to generate PR title, body, and commit message
def generate_pr_metadata(model, task, code):
    pr_title = model.prompt(pr_title_prompt.replace('<task>', task).replace('<code>', code)).text().strip()
    pr_body = model.prompt(pr_body_prompt.replace('<task>', task).replace('<code>', code)).text().strip()
    commit_message = model.prompt(commit_message_prompt.replace('<task>', task).replace('<code>', code)).text().strip()
    return pr_title, pr_body, commit_message

def generate_branch_name(model, task):
    return model.prompt(branch_name_prompt.replace('<task>', task)).text().strip()

# Function to get the current repository URL
def get_repo_url():
    result = subprocess.run(["git", "config", "--get", "remote.origin.url"], capture_output=True, text=True, check=True)
    return result.stdout.strip()

# Loop function to iterate generate and evaluate process
def evaluator_optimizer_loop(model, task, output_file):
    memory = []
    chain_of_thought = []

    # Initial generation
    thoughts, result = generate_code(model, generator_prompt, task)
    memory.append(result)
    chain_of_thought.append({"thoughts": thoughts, "result": result})

    while True:
        evaluation, feedback = evaluate_code(model, evaluator_prompt, result, task)
        
        if evaluation == "PASS":
            filename = save_code_to_file(result, output_file)

            # Generate PR metadata using LLM
            pr_title, pr_body, commit_message = generate_pr_metadata(model, task, result)

            create_pull_request(filename, pr_title, pr_body, commit_message)
            print(f"Final Result:\n{result}")
            break
        
        context = "Previous attempts:\n" + "\n".join(f"- {m}" for m in memory) + f"\nFeedback: {feedback}\n"
        
        # Generate a new response based on feedback
        thoughts, result = generate_code(model, generator_prompt, task, context)
        memory.append(result)
        chain_of_thought.append({"thoughts": thoughts, "result": result})

# Main execution
if __name__ == "__main__":
    model = llm.get_model("gpt-4o-mini")  # Change the model as needed
    
    # Determine how to read the task and file output name
    if len(sys.argv) > 1:
        input_source = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'generated_code.py'
    else:
        input_source = 'stdin'
        output_file = 'generated_code.py'
    
    task = read_task(input_source)

    # Get the repository URL for the current working directory
    repo_url = get_repo_url()
    evaluator_optimizer_loop(model, task, output_file)

