#!/usr/bin/env python3
'''
repo : https://github.com/openmarmot/review
email : andrew@openmarmot.com
notes :
CLI took to create AI generated reviews of files
'''

import os
import argparse
import sys
import requests
import json


#------------------------------------------------------------------------------
def create_ai_vars_file(file_path):
    '''create the ai variables file'''
    vars={}
    vars['model']='x-ai/grok-3-mini-beta'
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
    code_content=read_file_content(file_path)
    code_type='code'
    if '.py' in file_path:
        code_type='python'
    prompt = (
    "Please review the following code:\n\n"
    f"```{code_type}\n"
    f"{code_content}\n"
    "```\n\n"
    "Provide a code review, focusing on these issues in order of importance:\n"
    "- Syntax errors\n"
    "- Logic errors\n"
    "- Other critical issues\n"
    "- Style improvements\n"
    "- Other suggestions\n"
    "If you find more than 10 issues, only report on 10 sorted with the above ranking.\n"
    "Your response will be read from a terminal, so keep lines short.\n"
    )
    return prompt

#------------------------------------------------------------------------------
def generate_review(file_path):
    '''all the code needed to generate the review'''
    
    print("========================================")
    print(f'Generating code review for:')
    print(file_path)
    print('One moment..')
    print("========================================")

    # first lets get or create the ai parameters
    # create or load ai variables
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ai_variable_file = os.path.join(script_dir, 'review_ai_variables.txt')
    ai_vars=get_dict_from_file(ai_variable_file)
    if not ai_vars:
        ai_vars=create_ai_vars_file(ai_variable_file)

    prompt=generate_prompt(file_path)

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

    response=response.json()
    # Extract specific sections
    # Extract sections
    content = response["choices"][0]["message"]["content"]
    usage = response["usage"]

    # Print content with newlines interpreted
    print("========================================")
    print("Code Review")
    print("========================================")
    print(content)  # \n becomes actual line breaks
    print("========================================")
    print("API Usage Data")
    print("========================================")
    print(json.dumps(usage, indent=2))
    print("========================================")
    print('Have a nice day!')
    print("========================================")



#------------------------------------------------------------------------------
def get_dict_from_file(file_path):
    '''generate a dictionary from a file'''
    result = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Remove whitespace and split on first colon
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
    print("https://github.com/openmarmot/review")
    print("========================================")
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Read contents of a file or find and read the most recent .py or .js file")
    parser.add_argument('filename', nargs='?', help="Optional file to read")
    
    # Parse arguments
    args = parser.parse_args()

    # Valid extensions
    VALID_EXTENSIONS = ['.py', '.js']
    
    file_path=None

    if args.filename:
        # If filename is provided, read that file
        if not os.path.isfile(args.filename):
            print(f"Error: {args.filename} does not exist", file=sys.stderr)
            sys.exit(1)
        file_path=args.filename
    else:
        # If no filename, search for most recently modified .py or .js file
        print("========================================")
        print('Checking for most recent code file')
        print('One moment..')
        print("========================================")
        found_file = find_most_recent_file(os.getcwd(), VALID_EXTENSIONS)
        if not found_file:
            print("Error: No .py or .js files found in directory", file=sys.stderr)
            sys.exit(1)
        file_path=found_file

    generate_review(file_path)

#------------------------------------------------------------------------------
def write_dict_to_file(dictionary, file_path):
    '''write a dictionary to a file in line=key:value syntax '''
    try:
        with open(file_path, 'w') as file:
            for key, value in dictionary.items():
                # Ensure key and value are strings and write in key:value format
                file.write(f"{key}:{value}\n")
        return True
    except Exception as e:
        print(f"Error writing to file: {e}")
        return False

if __name__ == "__main__":
    main()