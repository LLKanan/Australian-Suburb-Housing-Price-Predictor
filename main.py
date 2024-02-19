from DataCollection.houseSpeakingSameScraper import scrapeData 
import logging

def main():
    logging.basicConfig(filename='PerthHousingEstimator.log', level = logging.DEBUG)
    logging.info('Application started')
    url = 'http://house.speakingsame.com/p.php?q=Dayton&p=29&s=1&st=&type=&count=300&region=Dayton&lat=0&lng=0&sta=wa&htype=&agent=0&minprice=0&maxprice=0&minbed=1&maxbed=0&minland=0&maxland=0'
    if scrapeData(url) == -1:
        logging.debug('Application has failed to scrape data, now terminating')
        return None
    logging.info('Application has successfully scraped data')
    logging.info('Application finished')

if __name__=='__main__':
    main()
