from collections import  defaultdict
import yfinance as yf

yf.download()

members_map = defaultdict(list)

with open(r"/Users/pankajti/dev/git/wqu/capstone/topics/members.txt", 'r') as members_f:
    lines = members_f.readlines()
    topic = 'start'

    for l in lines:
        if l[0].isdigit():
            topic=l
            print(topic)
        else:
            members_map[topic].append(l)

print(members_map)

print(list(members_map.values())[0][::8])