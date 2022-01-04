# BiwWillBot project

## Launch the bot
1. Add a config.ini file with your credentials in that format:
```
[DEFAULT]
api_key = <YOUR API KEY>
api_secret = <YOUR API SECRET>
subaccount_name = <YOUR SUB ACCOUNT>
```

## launch the project
``` uvicorn app.main:app --reload --port 8000```
