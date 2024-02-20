from DataCollection.houseSpeakingSameScraper import scrapeData 
import logging

def main():
    logging.basicConfig(filename='PerthHousingEstimator.log', level = logging.DEBUG)
    logging.info('Application started')
    suburb = input('Enter Suburb: ')
    postcode = input('Enter Postcode: ')
    if scrapeData(suburb,postcode) == -1:
        logging.debug('Application has failed to scrape data, now terminating')
        return None
    logging.info('Application has successfully scraped data')
    logging.info('Application finished')

if __name__=='__main__':
    main()
