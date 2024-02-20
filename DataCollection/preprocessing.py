import requests
import json
import pandas as pd
import os
import logging
logger = logging.getLogger(__name__)

def getGKey():
    return os.environ.get('gkey')

def addLocation(csvFilePath):
    #Get the location of all the files within the csv
    df = pd.read_csv(csvFilePath)
    lat = []
    long []

