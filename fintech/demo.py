from bs4 import BeautifulSoup

with open('fintech_demo.html', 'r') as f:
    txt = f.read()

soup = BeautifulSoup(txt)
p= soup.find('p')
print(p)