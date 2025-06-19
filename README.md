# review
CLI tool to create AI reviews of files

This a simple command line tool that uses AI to generate code reviews of individal files.  
It is designed to be fast and simple to use so that it can easily be added to a development 
workflow in a similar way to conventional tools like pylint.

API : openrouter.ai  
MODEL : XAI Grok3 Mini

Openrouter has the advantage of providing a standardized API for a wide variety of models, and it also makes key management very easy.  

Grok3 mini is a cost efficent reasoning model with a large context that performs well for this use case.  

### Setup
PreReqs: Python3. No additional packages are needed.

1. Create a account with openrouter.ai and create a api key for usage with this application.

2. Optionally create a symbolic link to a shorter command like 'r' in a folder in your PATH.  
    This allows you to run the program by typing 'r'
    ```bash
    ln -s /my/git/dir/review/code/review.py ~/.local/bin/r 
    ```
    Once this is done you will want to close and re-open your terminal so it takes effect.
3. The first time the program is launched it will create a file 'review_ai_variables.txt' in 
the location that review.py or your symbolic link is located. You will be prompted for your 
API key. This file can be updated to change the model or api key later if you wish.

### Usage

create a review of the most recently modified code file in your current folder
```bash
r
```
<br>
create a review of a specific file, or a file in a subfolder. 

```bash
r file.py
r folder/file.py
```

### Cost
Reviewing a 3000 line file is currently costing me around $0.017 USD. Cost will change based on file size and API costs.

![screenshot](/screenshots/Screenshot From 2025-06-19 13-28-56.png "Review output")

