import asyncio
import concurrent.futures
import os
import yaml
import signal
import sys
import time
import threading
from datetime import datetime, timezone
from pymongo import *
import pymongo
import argparse
import certifi
import json
from enum import Enum
from datetime import datetime

# "sta", "prod"
ENV = "sta"
LBContainerID = "c4d05b93-87fd-473b-bab4-fcc42e923077"
QUERY_IDS = [
]

QUERY_LISTS = []

class ResourceType(Enum):
    TypeDummy = 0
    TypeCampaign = 1
    TypeLeaderboard = 2
    TypeContainer = 3
    TypeEvaluator = 4
    TypeAggregator = 5
    TypeMission = 6
    TypeQuestionaire = 7
    TypePrize = 8

def GetActionLog(ID, eventoryDB):
    global QUERY_LISTS
    query = {"resourceID":ID}
    sort = [('timestamp', -1)]
    cursor = eventoryDB["ActionLog"].find(query).sort(sort)

    for e in cursor:
        del e['_id']
        e['resourceType'] = str(ResourceType(e['resourceType']).name)
        e['mydatetime'] = datetime.fromtimestamp(int(e['timestamp'])).strftime("%Y/%m/%d, %H:%M:%S")
        if 'snapshot' in e:
            e['snapshot'] = json.loads(e['snapshot'])
            
        QUERY_LISTS.append(e)

def GetRelatedID(ID, eventoryDB):
    ids = [ID]

    query = {"ID":ID}
    dataContainerCursor = eventoryDB["DataContainer"].find_one(query)
    if dataContainerCursor:
        lbID = dataContainerCursor['refID']
        ids.append(lbID)
    
    # Evaluator
    query = {"targetContainerID":ID}
    EvaluatorCursor = eventoryDB["Evaluator"].find(query)
    for evaluator in EvaluatorCursor:
        ids.append(evaluator['ID'])

    # Aggregator
    query = {"srcContainerID":ID}
    AggregatorCursor = eventoryDB["Aggregator"].find(query)
    for aggr in AggregatorCursor:
        ids.append(aggr['ID'])

    # Aggregator
    query = {"targetContainerID":ID}
    AggregatorCursor = eventoryDB["Aggregator"].find(query)
    for aggr in AggregatorCursor:
        ids.append(aggr['ID'])

    return ids

def main(argv):

    global ENV, LBContainerID, QUERY_IDS, QUERY_LISTS

    ca = certifi.where()

    if ENV=="sta":
        with open("config.yaml", "r") as f:
            data = yaml.safe_load(f)
    elif ENV=="prod":
        with open("prod_config.yaml", "r") as f:
            data = yaml.safe_load(f)

    if data["mongodb"]["eventory"]["username"]==None or data["mongodb"]["eventory"]["password"]==None or data["mongodb"]["user"]["username"]==None or data["mongodb"]["user"]["password"]==None:
        print("config.yaml need your DB account and password")
        return

    eventoryClient = MongoClient(data["mongodb"]["eventory"]["address"], 
    data["mongodb"]["eventory"]["port"],
    connect=True,
    username=data["mongodb"]["eventory"]["username"],
    password=data["mongodb"]["eventory"]["password"],
    tlsCAFile=ca
    ) 
    eventoryDB = eventoryClient["eventory"]

    # get all related QUERY_IDS
    QUERY_IDS = QUERY_IDS + GetRelatedID(LBContainerID, eventoryDB)
    for id in QUERY_IDS:
        print("Fetch ID={}".format(id))
        GetActionLog(id, eventoryDB)

    QUERY_LISTS = sorted(QUERY_LISTS, key=lambda d: d['timestamp'])
    # # QUERY_LISTS.reverse()

    with open('result.json', 'w') as f:
        f.write(json.dumps({"result":QUERY_LISTS}, indent=4))

if __name__ == "__main__":
    main(sys.argv[1:])