# README for EOL (Evaluator Optimizer Loop)

## Overview

EOL (Evaluator Optimizer Loop) is a Python tool that facilitates the automation of code generation, evaluation, and integration with GitHub repositories. It leverages a language model (LLM) to create code solutions based on provided tasks and then evaluates the quality of the generated code before making it ready for submission via pull requests.

## Features

- Automated code generation using LLM based on user-defined tasks.
- Evaluation of generated code for correctness, performance, and adherence to best practices.
- Automatic creation of a new branch, committing changes, and submitting pull requests to a GitHub repository.

## Installation

To use the EOL script, you need to have Python installed along with `git` and the GitHub CLI (`gh`). Follow these steps to set up your environment:

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. Install necessary Python packages (if any):
   ```bash
   pip install -r requirements.txt  # Adjust this if you have specific dependencies
   ```

## Usage

To run the EOL script, execute the following command:

```bash
python eol.py <input_source> <output_file>
```

### Parameters:

- `input_source`: Can be the path to a file containing the task description or 'stdin' for manual input.
- `output_file`: The name of the file where the generated code will be saved (default: `generated_code.py`).

### Example:

```bash
python eol.py task.txt generated_code.py
```

## How It Works

1. **Task Input**: The user provides a task description.
2. **Code Generation**: The LLM generates a solution for the task.
3. **Evaluation**: The generated code is evaluated based on correctness, time complexity, and coding standards.
4. **Pull Request Creation**: If the evaluation passes, EOL creates a new branch, commits the code, and submits a pull request on GitHub.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature-new-feature`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-new-feature`).
5. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Thanks to the creators and maintainers of the tools and libraries used in this project!

---

This README provides necessary information while maintaining clarity and simplicity for the end user.
