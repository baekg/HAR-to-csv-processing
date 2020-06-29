import datetime
from scipy import stats
import os
import json
import numpy as np
import csv
pattern='%Y-%m-%dT%H:%M:%S.%f'
url_dict=dict()
# directory="/home/chitrank/Downloads/new_front_with_cache/"
rem_len=len("http://0.0.0.0:3000/")
for filename in os.listdir(directory):    
    if filename.endswith(".har"):
        with open(directory+filename, 'r') as content_file:
            content = content_file.read()
            dicti=json.loads(content)
        num_entries=len(dicti["log"]["entries"])
        urls_tup=tuple(i["request"]["url"] for i in dicti["log"]["entries"])
        url_to_info=dict()
        for i in range(num_entries):
            en=dicti["log"]["entries"][i] 
            en_time=en["timings"]
            url=en["request"]["url"]
            time=0 if en["time"]==-1 else round(en["time"],3)
            dns=0 if en_time["dns"]==-1 else round(en_time["dns"],3)
            ssl=0 if en_time["ssl"]==-1 else round(en_time["ssl"],3)   
            blocked=0 if en_time["blocked"]==-1 else round(en_time["blocked"],3)
            connect=0 if en_time["connect"]==-1 else round(en_time["connect"],3)
            send=0 if en_time["send"]==-1 else round(en_time["send"],3)
            receive=0 if en_time["receive"]==-1 else round(en_time["receive"],3)
            wait=0 if en_time["wait"]==-1 else round(en_time["wait"],3)
            cache="****" if "_fromCache" not in en else en["_fromCache"]
            size=0.0 if "size" not in en["response"]["content"] else en["response"]["content"]["size"]
            typef=0.0 if "mimeType" not in en["response"]["content"] else en["response"]["content"]["mimeType"]
            if i==0:
                start_time=datetime.datetime.strptime(en["startedDateTime"][:-1], pattern)
                sent_req=0
            else:
                time1=datetime.datetime.strptime(en["startedDateTime"][:-1], '%Y-%m-%dT%H:%M:%S.%f')
                sent_req=(time1-start_time).total_seconds()
            if url not in url_dict:
                name=url.split("/")[-1]
                if name[0]=='?':
                    name="<URL>"
                url_dict[url]={"name":name,"type":typef.split("/")[-1],"files":[filename],"request":[sent_req],"cache":[cache],"values":[[0.00001*size,time,blocked,dns,ssl,connect,send,wait,receive]]}
            else:
                url_dict[url]["request"].append(sent_req)
                url_dict[url]["files"].append(filename)
                url_dict[url]["cache"].append(cache)
                url_dict[url]["values"].append([0.00001*size,time,blocked,dns,ssl,connect,send,wait,receive])               
#                 url_dict[url]={"request":requestl,"cache":cachel,"values":vall}

for url in url_dict:
#     print(len(url_dict[url]["request"]))
#     print(url)
    url_dict[url]["request"]=np.mean(url_dict[url]["request"])
    url_dict[url]["cache"]=stats.mode(url_dict[url]["cache"])[0][0]
    url_dict[url]["values"]=np.mean(url_dict[url]["values"],0)
    url_dict[url]["files"]=", ".join(url_dict[url]["files"])
with open('meter_cache_cold.csv', mode='w') as csv_file:
    fieldnames = ['S.no', 'RequestURL',"Files","name of file","Type of file","Request time(s)","Load time since start(s)","cache","size(100KB)","Time(ms)","Blocked(ms)","DNS(ms)","SSL(ms)","Connect(ms)","Send(ms)","TFFB(ms)","Receive(ms)"]
    writer = csv.writer(csv_file)
    writer.writerow(fieldnames)
    i=0
    for url in url_dict:
        row=[i+1,url[rem_len:],url_dict[url]["files"],url_dict[url]["name"],url_dict[url]["type"],url_dict[url]["request"],url_dict[url]["request"]+0.001*url_dict[url]["values"][0],url_dict[url]["cache"]]
        row.extend(url_dict[url]["values"])
        writer.writerow(row)
        i+=1


