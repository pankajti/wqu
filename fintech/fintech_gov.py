from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import json
import pandas as pd

def main():
    df = pd.read_excel(r'/Users/pankajti/dev/git/wqu/fintech/data/fintech_names.xlsx')
    companies = []
    [companies.extend(df[c].dropna().to_list()) for c in df.columns]
    #companies=['ZIGRAM']

    records = []
    #companies = ['fego']
    driver = webdriver.Firefox()
    page_url = r'https://www.ynos.in/products/startups/index.html#!/dashboard?query={}'.format(company)


    for company in set(companies):
        print(f"started for {company}")
        #records = scrap_company_records(company, driver, records)

        try:
            records = scrap_company_records(company, driver, records)
            with open(f'/Users/pankajti/dev/git/wqu/fintech/data/all_records_temp.json', 'w') as f:
                recs = json.dumps(records)
                f.write(recs)
        except Exception as e:
            print(f"error while downloading for {company}")
            t = time.time_ns()

            with open(f'/Users/pankajti/dev/git/wqu/fintech/data/all_records_{t}.json', 'w') as f:
                recs = json.dumps(records)
                f.write(recs)
            raise e

    t = time.time_ns()

    with open(f'/Users/pankajti/dev/git/wqu/fintech/data/all_records_{t}.json', 'w') as f:
        recs = json.dumps(records)
        f.write(recs)

import os
def scrap_company_records(company, driver, records):
    page_url = r'https://www.ynos.in/products/startups/index.html#!/dashboard?query={}'.format(company)
    # chromedriver_autoinstaller.install()
    file_path = f'/Users/pankajti/dev/git/wqu/fintech/data/{company}.html'
    if os.path.exists(file_path):
        print(f"file {file_path} is present locally")
        with open (file_path) as f:
            soup = BeautifulSoup(f.read())
    else :
        driver.get(page_url)
        time.sleep(10)
        more_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'more')]")
        for but in more_buttons:
            but.click()
        soup = BeautifulSoup(driver.page_source)

    # card-content > div.card-content_body.ng-isolate-scope

    companies = soup.find_all("div",class_="card-content_body ng-isolate-scope" )
    if len(companies)>0 :
        company_1 = companies[0]
    else :
        return records


    founders = [a.text.strip().split('\n')[0] for a in company_1.find_all(class_='founder-bio')]
    investors = get_investors(company_1)
    company_tag = company_1.find('h2', class_="ng-binding")
    if company_tag is not None:
        records.append({'founders': founders, 'investors': investors, 'company': company_tag.text, })
        with open(file_path, 'w') as f:
            f.write(driver.page_source)
    else :
        print(f"error : company {company} not found")
    return records


def get_investors(soup):
    ret=[]
    try:
        angels_hrefs= [a for a in soup.find_all("a") if   'angels/' in a['href']]
        angles = [a['href'].split("?")[-1] for a in angels_hrefs]
        ret.extend([vc.split("=")[1].replace("+", " ") for vc in angles if vc.split("=")[0].startswith("query")])

        vcs =  [a['href'].split("?")[-1] for a in soup.find_all("a") if   'vcs/' in a['href']]
        ret.extend([vc.split("=")[1].replace("+", " ") for vc in vcs if vc.split("=")[0].startswith("query")])

        investors = {"angels":angles, "vcs":vcs}
    except Exception as e:
        print("error getting investors ")
    return ret


if __name__ == '__main__':
    main()