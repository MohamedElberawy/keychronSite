import scrapy
import json
from scrapy.crawler import CrawlerProcess
import smtplib
from email.message import EmailMessage
import mimetypes
import pandas as pd
import os

CSV_FILE = "key2.csv"


class Keychron1Spider(scrapy.Spider):
    name = "keychron1"
    start_urls = [
        "https://www.keychron.com/collections/custom-keyboards/products/keychron-q1"]

    custom_settings = {
        'FEEDS': {
            CSV_FILE: {
                'format': 'csv',
                'encoding': 'utf-8'
            }
        }
    }
    
# This functions yield the information we want
    def parse(self, response):
        raw_data = response.css(
            'script[type="application/ld+json"]::text').get()
        data = json.loads(raw_data)
        for item in data["offers"]:
            available = True if "InStock" in item["availability"] else False
            yield {
                'name': item["name"],
                'price': item["price"],
                'available': available,
                'Url': item["url"],
                'priceValidUntil': item["priceValidUntil"]
            }

            
def get_body():
    df = pd.read_csv(CSV_FILE)
    df[df['available']].to_html()

# this function send the csv file we create to the email
def send_mail():
    msg = EmailMessage()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER
    msg['Subject'] = "Keychron Availability Status"

    EMAIL_USER = os.environ.get('ZMAIL')
    EMAIL_PASS = os.environ.get('ZPASS')

    body = get_body()
    msg.set_content(body, subtype="html")

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
        print('-----------------------fdsgsd----------------------------')


def cleanup():
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)


def main():
    cleanup()
    process = CrawlerProcess()
    process.crawl(Keychron1Spider)
    process.start()
    send_mail()


if __name__ == "__main__":
    main()
