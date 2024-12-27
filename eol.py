import llm
import sys

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
from your previous generations, you should reflect on them to improve your solution

Output your answer concisely in the following format: 

<thoughts>
[Your understanding of the task and feedback and how you plan to improve]
</thoughts>

<response>
[Your code implementation here]
</response>
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
    
    # Extract thoughts and result from the response
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
    
    # Extract evaluation and feedback from the response
    evaluation = response.text().split("<evaluation>")[1].split("</evaluation>")[0].strip()
    feedback = response.text().split("<feedback>")[1].split("</feedback>")[0].strip()
    
    print("\n=== EVALUATION START ===")
    print(f"Status: {evaluation}")
    print(f"Feedback: {feedback}")
    print("=== EVALUATION END ===\n")
    
    return evaluation, feedback

# Loop function to iterate generate and evaluate process
def evaluator_optimizer_loop(model, task):
    memory = []
    chain_of_thought = []

    # Initial generation
    thoughts, result = generate_code(model, generator_prompt, task)
    memory.append(result)
    chain_of_thought.append({"thoughts": thoughts, "result": result})

    while True:
        evaluation, feedback = evaluate_code(model, evaluator_prompt, result, task)
        
        if evaluation == "PASS":
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
    
    # Determine how to read the task
    if len(sys.argv) > 1:
        input_source = sys.argv[1]
    else:
        input_source = 'stdin'
    
    task = read_task(input_source)
    evaluator_optimizer_loop(model, task)

