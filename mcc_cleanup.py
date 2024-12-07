import sys
import csv
import json

with open('mcc_codes.csv', 'r') as fp:
    reader = csv.reader(fp, delimiter=',', )
    source_headers = ['Код','Название','Описание']
    dest = {}
    
    csv_iter = iter(reader)
    for row in csv_iter:
        code = row[0]
        name = row[1]
        description = row[2]
        dest[code] = name, description
        
with open('mcc_codes.json', 'w', encoding='utf-8') as f:
    json.dump(dest, f, ensure_ascii=False, indent=4)
