import llm

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

task = """<user input>
Implement a Stack with:
1. push(x)
2. pop()
3. getMin()
All operations should be O(1).
</user input>
"""

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
def evaluator_optimizer_loop(model):
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
    evaluator_optimizer_loop(model)
