#!/usr/bin/env python3
'''
repo : https://github.com/openmarmot/review
email : andrew@openmarmot.com
notes :
CLI tool to create AI generated reviews of files
'''

import os
import argparse
import sys
import requests
import json

# Global dictionary mapping file extensions to language names
SUPPORTED_LANGUAGES = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.java': 'java',
    '.cpp': 'cpp',
    '.c': 'c',
    '.h': 'c',  # Treat headers as C for simplicity; adjust if needed for C++
    '.cs': 'csharp',
    '.go': 'go',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.php': 'php',
    '.html': 'html',
    '.css': 'css',
    '.yml': 'yaml',
    '.yaml': 'yaml',
    '.sh': 'bash',
}

#------------------------------------------------------------------------------
def create_ai_vars_file(file_path):
    '''create the ai variables file'''
    vars={}
    vars['model']='x-ai/grok-code-fast-1'
    vars['api_key']=input('Enter your API key:')
    vars['api_url']='https://openrouter.ai/api/v1/chat/completions'

    write_dict_to_file(vars,file_path)

    return vars

#------------------------------------------------------------------------------
def find_most_recent_file(start_dir, extensions):
    """Recursively find the most recently modified file with specified extensions."""
    most_recent_file = None
    most_recent_time = 0

    for root, _, files in os.walk(start_dir):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                mtime = os.path.getmtime(file_path)
                if mtime > most_recent_time:
                    most_recent_time = mtime
                    most_recent_file = file_path
    
    return most_recent_file

#------------------------------------------------------------------------------
def generate_prompt(file_path):
    '''generates the full prompt including file data'''
    code_content=read_file_content(file_path)
    
    # Get language from file extension
    ext = os.path.splitext(file_path)[1].lower()
    code_type = SUPPORTED_LANGUAGES.get(ext, 'code')  # Default to 'code' for unknown extensions
    
    prompt = (
    "Please review the following code or configuration:\n\n"
    "Structure your response as a numbered list of up to 10 issues, prioritized by:"
    "Syntax errors (with line numbers if possible).\n"
    "Logic errors or bugs (explain impact and suggest fixes with code snippets).\n"
    "Security vulnerabilities or performance issues.\n"
    "Style and best practices (reference standards like PEP8 for Python).\n"
    "Other improvements (e.g., readability, modularity).\n"
    f"```{code_type}\n"
    f"{code_content}\n"
    "```\n\n"
    )
    return prompt

#------------------------------------------------------------------------------
def generate_review(file_path):
    '''all the code needed to generate the review'''
    
    # create or load ai variables
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ai_variable_file = os.path.join(script_dir, 'review_ai_variables.txt')
    ai_vars = get_dict_from_file(ai_variable_file)
    if not ai_vars:
        ai_vars = create_ai_vars_file(ai_variable_file)

    print(f'Ai Model : {ai_vars['model']}')
    print(f'Generating review for: {file_path}')
    print("========================================")

    prompt = generate_prompt(file_path)

    try:
        response = requests.post(
            url=ai_vars['api_url'],
            headers={
                "Authorization": f"Bearer {ai_vars['api_key']}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": ai_vars['model'],
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            })
        )
        
        # Raise an exception if the request failed (non-2xx status)
        response.raise_for_status()
        
        # Parse JSON
        response_data = response.json()
        
        # Access content and usage safely
        content = response_data["choices"][0]["message"]["content"]
        usage = response_data["usage"]

        print('review:')
        print(content)
        print("========================================")
        print("API Usage Data")
        print("========================================")
        print(json.dumps(usage, indent=2))
        print("========================================")
        print('Have a nice day!')
        print("========================================")

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, IndexError) as e:
        print(f"Unexpected API response structure: {e}", file=sys.stderr)
        print(f"Raw response: {response.text}", file=sys.stderr)  # For debugging
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response: {e}", file=sys.stderr)
        print(f"Raw response: {response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

#------------------------------------------------------------------------------
def get_dict_from_file(file_path):
    '''generate a dictionary from a file'''
    result = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:  # Skip empty lines
                    key, value = line.split(':', 1)
                    result[key.strip()] = value.strip()
        return result
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return {}
    except Exception as e:
        print(f"Error processing file: {e}")
        return {}

#------------------------------------------------------------------------------
def read_file_content(file_path):
    """Read the contents of a file into a string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

#------------------------------------------------------------------------------
def main():
    '''entry point'''
    print("========================================")
    print("OpenMarmot Code Review")
    print("Project : https://github.com/openmarmot/review")
    parser = argparse.ArgumentParser(description="Read contents of a file or find and read the most recent supported file")
    parser.add_argument('filename', nargs='?', help="Optional file to read")
    
    args = parser.parse_args()

    # Use keys from SUPPORTED_LANGUAGES as valid extensions
    valid_extensions = SUPPORTED_LANGUAGES.keys()
    
    file_path=None

    if args.filename:
        ext = os.path.splitext(args.filename)[1].lower()
        if ext not in valid_extensions:
            print(f"Error: Unsupported file extension {ext}. Supported: {', '.join(valid_extensions)}", file=sys.stderr)
            sys.exit(1)
        if not os.path.isfile(args.filename):
            print(f"Error: {args.filename} does not exist", file=sys.stderr)
            sys.exit(1)
        file_path=args.filename
    else:
        print('Checking for most recent supported file..')
        found_file = find_most_recent_file(os.getcwd(), valid_extensions)
        if not found_file:
            print(f"Error: No supported files found in directory. Supported extensions: {', '.join(valid_extensions)}", file=sys.stderr)
            sys.exit(1)
        file_path=found_file

    generate_review(file_path)

#------------------------------------------------------------------------------
def write_dict_to_file(dictionary, file_path):
    '''write a dictionary to a file in line=key:value syntax '''
    try:
        with open(file_path, 'w') as file:
            for key, value in dictionary.items():
                file.write(f"{key}:{value}\n")
        return True
    except Exception as e:
        print(f"Error writing to file: {e}")
        return False

if __name__ == "__main__":
    main()