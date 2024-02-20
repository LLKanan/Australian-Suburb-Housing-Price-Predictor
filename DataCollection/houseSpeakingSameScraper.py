import requests
import pandas as pd 
import pgeocode
from pathlib import Path
from bs4 import BeautifulSoup
import logging
logger = logging.getLogger(__name__)

#Get the state of the given postcode and suburb
def getState(suburb,postcode):
    logger.info('Getting state of suburb and postcode')
    nomi = pgeocode.Nominatim('au')
    result = nomi.query_postal_code(postcode)
    for place in result['place_name'].split(', '):
        if place == suburb:
            logger.info('Found matching suburb and postcode')
            return result['state_code']
    logger.error('Unable to find matching suburb and postcode')
    return None

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

#generates the URLs for the given suburb and state
def generateURLs(suburb,state):
    logger.info('Generating URL for: ' + suburb + ',' + state)
    pages = []
    for pageNumber in range(0,30,1):
        pages.append('http://house.speakingsame.com/p.php?q=' + suburb.replace(' ','+') + '&p=' + str(pageNumber) + '&s=1&st=&type=&count=300&region=' + suburb + '&lat=0&lng=0&sta=' + state.lower() + '&htype=&agent=0&minprice=0&maxprice=0&minbed=0&maxbed=0&minland=0&maxland=0')
    return pages

#processed the raw data into a format we can pass into a dataframe
def processData(rawData):
    logger.info('Processing raw data')
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


#Scrapes data for a particular suburb returns 1 if Successful, otherwise returns -1
def scrapeData(suburb,postcode):
    logger.info('Checking if suburb and postcode are valid')
    state = getState(suburb,postcode)
    if state == None:
        logger.error('Unable to find state, terminating program')
        return -1

    logger.info('State Found: ' + str(state))
    logger.info('Beginning data scraping process for: ' + suburb + ', ' + state + ', ' + postcode)

    #Generate URLs to scrape given a suburb and state
    pages = generateURLs(suburb,state)

    #Get raw data from each page and process it
    data = []
    for page in pages:
        rawData = getData(page)
        if rawData == None:
            logging.error('Terminating data scraper due to failure to retrieve data')
            return -1
        processedData = processData(rawData)
        if processedData == []:
            logging.info('No more pages that contain data avaialble, stopping data collection')
            break
        data += processedData

    #Save to CSV
    dir = Path('./DataCollection/Data/')
    try:
        dir.mkdir(mode=0o777,parents=True,exist_ok=False)
    except:
        logger.info('Directory already exists')
    df = pd.DataFrame(data)
    df['State'] = state
    df['Suburb'] = suburb
    df['Postcode'] = postcode
    df.to_csv(str(dir)+ '/' + postcode + ' - ' + suburb + '.csv',index=False)
    return 1
