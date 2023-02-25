import pycountry
from bs4 import BeautifulSoup
import requests
import re
import os


class UniversityScraper:

    BASE_URL = "https://www.4icu.org"

    def __init__(self , country = "",city=""):

        self.country = country
        self.city = city
        

    def __getFeesAmount(self,text):

        if text == "Not reported":
            return None
    
        range_ = re.findall(r'\d+,*\d*',text)
        fst_num = int ( range_[0].replace(",","") )
        amount = fst_num

        if len(range_) >1 :
            
            amount = range_[0]+"-"+range_[1]

        return amount


    def __getFees(self,body):
    
        tr = body.find_all("tr")
        tds0 = tr[0].find_all("td")
        local_undergraduate_fees = tds0[1].find("strong").get_text()
        local_postgraduate_fees = tds0[2].find("strong").get_text()

        tds1 = tr[1].find_all("td")
        inter_undergraduate_fees = tds1[1].find("strong").get_text()
        inter_postgraduate_fees = tds1[2].find("strong").get_text()


        return {
            "local_students":{
                "undergraduate": self.__getFeesAmount(local_undergraduate_fees),
                "postgraduate": self.__getFeesAmount(local_postgraduate_fees)
            },
            "international_students":{
                "undergraduate": self.__getFeesAmount(inter_undergraduate_fees),
                "postgraduate": self.__getFeesAmount(inter_postgraduate_fees)
            }
        }


    def __getStudy(self,body):

        trs = body.find_all('tr')
        studies = []

        for tr in trs:

            tds = tr.find_all('td')
            degrees = []

            for td in tds[2:]:
                
                i = td.find('i')
                degrees.append(i['class'][1] == 'd1')

            studies.append(degrees)


        study_areas = {
            "arts" : {
                "B" : studies[0][0],
                "M" : studies[0][1],
                "D" : studies[0][2]
            },
            "business" : {
                "B" : studies[1][0],
                "M" : studies[1][1],
                "D" : studies[1][2]
            },
            "language" : {
                "B" : studies[2][0],
                "M" : studies[2][1],
                "D" : studies[2][2]
            },
            "medecine" : {
                "B" : studies[3][0],
                "M" : studies[3][1],
                "D" : studies[3][2]
            },
            "engineering" : {
                "B" : studies[4][0],
                "M" : studies[4][1],
                "D" : studies[4][2]
            },
            "science" : {
                "B" : studies[5][0],
                "M" : studies[5][1],
                "D" : studies[5][2]
            }
        }



        return study_areas


    def __getRank(self, body):

        trs = body.find_all('tr')

        ranks = []

        for tr in trs:

            td = tr.find_all('td')[1]
            ranks.append(td.find('a').find('strong').getText())
        

        return {
            'local': ranks[0],
            'global': ranks[1]
        }
    
    def __getLocation(self, body):

        trs = body.find_all("tr")


        return {
            "address":trs[0].find("td").find("span").getText(),
            "phone_number":trs[1].find("td").find("span").getText()
        }

    def __getUniDetail(self,href):

        url = self.BASE_URL+href
        html_text = requests.get(url=url).text
        soup = BeautifulSoup(html_text,"lxml")
        tbodies = soup.find_all('tbody')
        
        rank_div = soup.find("div", {"class":"panel panel-default text-center"})
        studies_div = tbodies[1]
        fees_div = tbodies[2]
        location_div = soup.find("div", {"itemtype":"http://schema.org/PostalAddress"})

        study_ = self.__getStudy(studies_div)
        rank_ = self.__getRank(rank_div)
        location_ = self.__getLocation(location_div)
        
        
        fees_ =  self.__getFees(fees_div)


        return { 
            "website_url":tbodies[0].find("tr").find("td").find("a")['href'],
            "rank": rank_,
            "location": location_,
            "studies" : study_,
            "fees" : fees_,
            }


    def scrap(self):

        
        abb = pycountry.countries.search_fuzzy(self.country)[0].alpha_2.lower()
        url = self.BASE_URL+"/"+abb+"/"+self.city+"/"

        html_text = requests.get(url=url).text
        soup = BeautifulSoup(html_text,"lxml")


        body = soup.find('tbody')
        unis = []

        for tr in body.find_all("tr"):

            tds = tr.find_all("td")

            try:
                
                name = tds[1].contents[0].get_text()

                print(f"{name} scraping in process...")


                city = tds[2].contents[0]

                a = tds[1].find('a')
                
                detail = self.__getUniDetail(a['href'])
        
                
                unis.append({
                    'name':name,
                    'country':self.country,
                    'city':city,
                    'source':self.BASE_URL + a['href'],
                    'detail':detail
                })

                print(f"{name} Done.")
                print("\n")
            except Exception as err:
                print(err)
        
            

        return unis