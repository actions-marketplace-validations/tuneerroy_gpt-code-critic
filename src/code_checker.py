# code_checker.py

# Import necessary libraries
import openai
import os
import json

# Load code to be checked
def load_code():
    # Get the path to the code file from the GitHub context
    code_file_path = os.environ.get("GITHUB_WORKSPACE") + "/path/to/code/file.py"

    # Read the code from the file
    with open(code_file_path, 'r') as f:
        code = f.read()

    return code

# Use GPT-3 to analyze code and generate code problems
def analyze_code_with_gpt3(filename, code_diff):
    # Preface with explanation
    prompt = "Analyze the following code changes to file " + filename + ".\n"
    prompt += "You should format your response like:\n"
    prompt += "Issue X (Line Y, Column Z)::: Comment about problem, quality, readability, or issue\n"
    prompt += "Issue X (Line Y, Column Z)::: Comment about problem, quality, readability, or issue\n"
    prompt += "...\n\n\n"
    prompt += "diff:\n" + code_diff + "\n"

    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "user", "content": prompt}
      ]
    )

    # Extract the generated analysis from the API response
    result = completion.choices[0].message.content

    return result

# Process results to SARIF format
def process_results_to_sarif(filename, result):
    # Parse the generated analysis from GPT-3
    results = result.split('Issue')
    issues = []
    for result in results:
        issue = {}
        tokens = result.strip().split(':::')
        if len(tokens) >= 2:
            try:
                issue['message'] = tokens[1].strip()
                location = {}
                location['file'] = filename
                location['line'] = int(tokens[0].split('Line')[1].split(',')[0].strip())
                location['column'] = int(tokens[0].split('Column')[1].strip()[:-1])
                issue['location'] = location
                issues.append(issue)
            except:
              pass

    # Create SARIF result objects
    sarif_results = []
    for issue in issues:
        # Extract issue details from the analysis
        message = issue.get("message", "")
        location = issue.get("location", {})
        file_path = location.get("file", "")
        line_number = location.get("line", 0)
        column_number = location.get("column", 0)

        # Create SARIF result object
        sarif_result = {
            "message": {
                "text": message
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": file_path
                        },
                        "region": {
                            "startLine": line_number,
                            "startColumn": column_number
                        }
                    }
                }
            ]
        }

        # Add the SARIF result object to the list
        sarif_results.append(sarif_result)

    # Create SARIF report
    sarif_report = {
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "GPT-3 Code Analysis",
                        "informationUri": "https://openai.com/gpt-3/",
                        "version": "1.0"
                    }
                },
                "results": sarif_results
            }
        ]
    }

    return json.dumps(sarif_report)

# Write SARIF files to disk
def write_sarif_files(sarif_files):
    # Placeholder function to write SARIF files to disk
    # Replace this with your own implementation to save the SARIF files
    # to disk, which can be used for further processing or display
    for sarif_file in sarif_files:
        # Write the SARIF file to disk
        with open(sarif_file['filename'], 'w') as f:
            f.write(sarif_file['content'])
        print(f"Generated SARIF file: {sarif_file['filename']}")

# Entry point of the script
if __name__ == '__main__':
    
    openai.api_key = os.environ.get("OPENAI_API_KEY")

    # Load code to be checked
    filename = 'main.py'
    code = 'def foo():\n    prnt("Hello, world!")'

    # Use GPT-3 to analyze code and generate code problems
    problems = analyze_code_with_gpt3(filename, code)

    print("RESPONSE:")
    print(problems)
    print("\n\n\n\n\n\n")

    # Process the results and generate SARIF files
    sarif_file = process_results_to_sarif(filename, problems)

    print(sarif_file)

    # Write SARIF files to disk
    write_sarif_files([sarif_file])

