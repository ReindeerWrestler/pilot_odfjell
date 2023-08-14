from numpy import array
import scrapy
from scrapy import Request, FormRequest
from bs4 import BeautifulSoup
import pandas as pd
import urllib3 as urllib

startdate = '20220721'#input("Enter Start Date:")
enddate = '20221231'#input("Enter End Date:")



class OdfjellscraperSpider(scrapy.Spider):
    name = 'odfjellscraper'
    allowed_domains = ['iis.odfjell.co.kr']
    start_urls = ['http://iis.odfjell.co.kr/']

    def parse(self, response):
        #print(response.text)
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate'
        }
        formdata={
            '__VIEWSTATE': response.css('[name="__VIEWSTATE"] ::attr(value)').get(),
            '__VIEWSTATEGENERATOR': response.css('[name="__VIEWSTATEGENERATOR"] ::attr(value)').get(),
            '__EVENTVALIDATION': response.css('[name="__EVENTVALIDATION"] ::attr(value)').get(),
            'txtUserID': 'Pilot',
            'txtPass': 'otk20210801!',
            'btnLogin': 'Login'
        }
        r = FormRequest.from_response(response,
                                    formdata=formdata,
                                    headers=headers,
                                    callback = self.after_login)
        yield r
        #print(response.headers)
        #print(response.text)
        #print(r.body)
        #print(self.to_write(r.body))
    
    #def to_write(uni_str):
        #return urllib.unquote(uni_str.encode('utf8')).decode('utf8')

    def after_login(self, response):
        r = scrapy.Request(
            method="GET",
            url='http://iis.odfjell.co.kr/product_out_between_term.aspx',
            callback=self.tablesearch)
        yield r

    def tablesearch(self, response):
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate'
        }
        formdata={
            '__VIEWSTATE': response.css('[name="__VIEWSTATE"] ::attr(value)').get(),
            '__VIEWSTATEGENERATOR': response.css('[name="__VIEWSTATEGENERATOR"] ::attr(value)').get(),
            '__EVENTVALIDATION': response.css('[name="__EVENTVALIDATION"] ::attr(value)').get(),
            'txtStart': startdate,
            'txtEnd': enddate,
            'btnDataSearch': 'Search',
            'chk탱크필드보이이기': 'on'
        }
        r = FormRequest.from_response(
            response,
            formdata=formdata,
            headers=headers,
            callback=self.tableparse)
        yield r

    def tableparse(self, response):
        soup = BeautifulSoup(response.text, features='lxml') # create soup object
        
        columns = soup.find_all('th') # get and parse columns
        columndata = list()
        for tag in columns:
            col = tag.get_text()
            columndata.append(col)
        
        rows = soup.find_all('td') # get and parse rows
        #_, *rows, _=rows
        newrows = list() 
        for row in rows:
            newrow = row.get_text()
            newrows.append(newrow)
        
        def rowdivide(l, n): # divide rows into groups of 14
            for i in range(0, len(l), n):
                yield l[i:i + n]
        n = 14
        rowdata = list(rowdivide(newrows, n))

        df = pd.DataFrame(rowdata, columns=columndata) # create table
        df.drop(df.tail(1).index,inplace=True) # drop last row
        #df.to_csv (r'C:\\Users\\ejproffitt\\localdev\\otkscraping\\output.csv', index = None, header=True, encoding="utf-8") 
        print(df)
        #print('화물정보조회')
        df
        ##df2 = 

#from scrapy.crawler import CrawlerProcess

#c = CrawlerProcess({
#    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'
#})

#c.crawl(odfjellspider)
#output = c.start()
