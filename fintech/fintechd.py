import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import json
import pandas as pd

def main():
    df = pd.read_csv(r'/Users/shritiwari/dev/git/vitmantra/notebooks/b2b_companies.csv')
    companies = []
    [companies.extend(df[c].dropna().to_list()) for c in df.columns]

    records = []
    #companies = ['fego']
    driver = webdriver.Firefox(executable_path=r'/Users/shritiwari/dev/software/geckodriver')

    for company in set(companies):
        print(f"started for {company}")
        records = scrap_company_records(company, driver, records)

        # try:
        #     records = scrap_company_records(company, driver, records)
        # except Exception as e:
        #     print(f"error while downloading for {company}")
            # t = time.time_ns()
            #
            # with open(f'/Users/shritiwari/dev/git/finance/fintech/data/all_records_{t}.json', 'w') as f:
            #     recs = json.dumps(records)
            #     f.write(recs)
            # raise e

    t = time.time_ns()

    with open(f'/Users/shritiwari/dev/git/finance/fintech/data/all_records_{t}.json', 'w') as f:
        recs = json.dumps(records)
        f.write(recs)

import os
def scrap_company_records(company, driver, records):
    page_url = r'https://www.ynos.in/products/startups/index.html#!/dashboard?query={}'.format(company)
    # chromedriver_autoinstaller.install()
    file_path = f'/Users/shritiwari/dev/git/finance/fintech/data/{company}.html'
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

    founders = [a.text.strip().split('\n')[0] for a in soup.find_all(class_='founder-bio')]
    investors_tag = soup.find("div", {"pill-data": "startup['Investors']['Funds']"})
    if investors_tag is not None:
        investors = [a.text.strip() for a in investors_tag.find_all(
                         class_='pill-user-name ng-binding ng-scope')]
    else:
        investors = ['NA']
    company_tag = soup.find('h2', class_="ng-binding")
    if company_tag is not None:
        records.append({'founders': founders, 'investors': investors, 'company': company_tag.text, })
        with open(file_path, 'w') as f:
            f.write(driver.page_source)
    else :
        print(f"error : company {company} not found")
    return records


if __name__ == '__main__':
    main()