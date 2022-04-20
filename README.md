# Fetch leaderboard container action log

## How to use
### Run
```
python investigate.py
```
output will be saved at `result.json`  
### Config
config.yaml for stage  
prod_config.yaml for production  
Fill in username & password in config file.  

### Python setup
```python
# "sta", "prod"
ENV = "prod"
LBContainerID = "5cce5356-7130-49f2-ad1e-124a89af2e44"
QUERY_IDS = [
    
]
```
- Change LBContainerID to your leaderboard container ID
- QUERY_IDS can add other container ID you want to fetch
- ENV have two options ["sta", "prod"]