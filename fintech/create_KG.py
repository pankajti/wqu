import yaml
import os
from neo4j import GraphDatabase
import pandas as pd 


uri= 'bolt://127.0.0.1:7687'
user= 'neo4j'
password= 'fintech123'
database= 'companies'
file_path = r'/Users/shritiwari/dev/git/finance/fintech/data/all_records_1701482111304292000.json'
df = pd.read_json(file_path)


            

def add_company_founder(driver, company_name, founder_name):

    driver.execute_query(
        "MERGE (a:Company {name: $company_name}) "
        "MERGE (founder:Founder {name:$founder_name}) "
        "MERGE (a)-[:Founded_By]->(founder)",
        company_name=company_name, founder_name=founder_name, database_=database,
    )

def add_company_investor(driver, company_name, investor_name):

    driver.execute_query(
        "MERGE (a:Company {name: $company_name}) "
        "MERGE (investor:Investor {name: $investor_name}) "
        "MERGE (a)-[:Invested_By]->(investor)",
        company_name=company_name, investor_name=investor_name, database_=database,
    )


with GraphDatabase.driver( uri, auth=( user, password)) as driver:
    for idx, rec in df.iterrows():
        print(idx)
        company=rec['company']
        founders = rec['founders']
        investors = rec['investors']

        for founder in founders:
            add_company_founder(driver, company_name=company, founder_name= founder)
        
        for investor in investors:
            if investor !='NA':
                add_company_investor(driver, company_name=company, investor_name= investor)
        
