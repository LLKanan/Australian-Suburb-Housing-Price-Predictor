import requests
import json
import pandas as pd 
from pathlib import Path
from bs4 import BeautifulSoup
import logging
logger = logging.getLogger(__name__)

#Gets data from a single URL
def getData(url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}
    logger.info('Scraping data from: ' + url)
    try:
        request = requests.get(url,allow_redirects=False, timeout=10,headers=headers)
        logger.info('Successfully received data')
        return request.text
    except requests.exceptions.Timeout as err:
        logger.error('Error getting data from :' + url)
        logger.debug(err)
    return None

#Validates URL
#Checks we're querying speaking same & checks url for page
def validateURL(url):
    logger.info('Validating URL: ' + url)
    if url.find('http://house.speakingsame.com/p.php?q=') != -1 and url.find('&p=') != -1:
        logger.info('Valid URL')
        return True
    logger.info('Invalid URL')
    return False

#Generates list of apges
def getPages(url):
    logger.info('Getting pages from URL: ' + url)

    pages = []
    startPageIndex = url.find('&p=') + 3
    endPageIndex = startPageIndex
    while url[endPageIndex].isdigit():
        endPageIndex += 1

    for pageNumber in range(0,30,1):
        pages.append(url[:startPageIndex] + str(pageNumber) + url[endPageIndex:])

    return pages

def processData(rawData):
    logger.info('Processing raw data for a single page')
    addresses = []
    propertyInfo = []

    soup = BeautifulSoup(rawData,"html.parser")
    addrSpans = soup.find_all('span', class_='addr')

    for span in addrSpans:
        addresses.append(span.a.text)

    tables = soup.find_all('table', style='font-size:13px')

    for listing in range(2,12):
        info = []
        try:
            trs = tables[listing].find_all('tr')
            for tr in trs:
                info.append(tr.td.text)
        except:
            info.append('')
        propertyInfo.append(info)

    listings = []
    for i in range(0, len(addresses)):
        propertyDict = {}
        propertyDict['Address'] = addresses[i]

        for j in range(0, len(propertyInfo[i])):
            try:
                info = propertyInfo[i][j].split(' ')
                match info[0]:
                    case 'Sold':
                        propertyDict['Price'] = info[1]
                        propertyDict['Sale Date'] = propertyInfo[i][j].split('in ')[1]

                    case 'Apartment:' | 'House:' | 'Townhouse:' | 'Unit:':
                        propertyDict['Type'] = info[0].split(':')[0]
                        propertyDict['Bedrooms'] = info[1]
                        try:
                            propertyDict['Bathrooms'] = info[3]
                        except:
                            propertyDict['Bathrooms'] = ''
                        try:
                            propertyDict['Parking'] = info[5]
                        except:
                            propertyDict['Parking'] = ''

                    case 'Agent:':
                        propertyDict['Agent'] = propertyInfo[i][j].split(': ')[1]

                    case 'Rent':
                        propertyDict['Rent'] = info[1]
                        propertyDict['Rent date'] = propertyInfo[i][j].split('in ')[1]

                    case _:
                        if info[1] == 'size':
                            if info[0] == 'Land':
                                propertyDict['Land size'] = info[2]
                                try:
                                    if info[5] == 'Building':
                                        propertyDict['Building size'] = info[7]
                                except:
                                    continue
                            elif info[0] == 'Building':
                                propertyDict['Building Size'] = info[2]
            except:
                continue
        listings.append(propertyDict)
    return listings


#Scrapes data returns 1 if Successful, otherwise returns -1
def scrapeData(url):
    logger.info('Beginning data scraping process for URL: ' + url)
    if validateURL(url) == False: 
        logger.error('Invalid URL: ' + url)
        return -1
    pages = getPages(url)
    
    #Get raw data from each page
    rawData = []
    for page in pages:
        data = getData(page)
        if data == None:
            logging.error('Terminating data scraper due to failure to retrieve data')
            return -1
        rawData.append(data)

    #Process raw data for each page
    processedData = []
    for page in rawData:
        processedData += processData(page)

    #Save to CSV
    dir = Path('./DataCollection/')
    try:
        dir.mkdir(mode=0o777,parents=True,exist_ok=False)
    except:
        logger.info('Directory already exists')
    df = pd.DataFrame(processedData)
    df.to_csv(str(dir) + '/scrapedData.csv')
    return 1
