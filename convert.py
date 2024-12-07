import sys
import csv
import datetime
import json
from decimal import Decimal
import re
report_file_name = str(sys.argv[1])
mcc_codes = {}
mcc_code_pattern = re.compile(r'\d{4}')
date_pattern = re.compile(r'\d{2}\.\d{2}\.\d{4}')
phone_pattern = re.compile(r'\+\d{10}')
sbp_payment_pattetn = re.compile(r'Платеж\s\w+\sв\s(.+)\sчерез\sСистему\sбыстрых\sплатежей')
account_pattern = re.compile(r'\d+')

with open('mcc_codes.json', 'r') as file:
    mcc_codes = json.load(file)
with open(report_file_name, 'r') as fp:
    reader = csv.reader(fp, delimiter=';', )
    source_headers = ['Дата операции','Дата проводки','', 'Код','Категория','','','','','','','Описание','Сумма в валюте счета','','Статус']
    dest_headers = ['Дата операции','Дата проводки','Код','Категория','Подкатегория','MCC','Источник','Контрагент','Описание','Сумма в валюте счета','Статус']
    with open(report_file_name+'_alfa.csv', "w") as output:
        csv_iter = iter(reader)
        print(";".join(list(dest_headers)), file=output)
        for row in csv_iter:
            if not row[0] or not row[1]:
                continue
            if not date_pattern.match(row[0]):
                continue
            mcc = ''
            subcategory = ''
            party = ''
            description = ''
            source = ''
            _description = row[11]
            parts = _description.split(',')
            # в конце может быть MCC
            if len(parts) > 2:
                if 'MCC' in parts[-1]:
                    if result := mcc_code_pattern.search(parts[-1]):
                        mcc = result.group(0)
                    if _party := parts[-2]:
                        if position := _party.find('место совершения операции:') > -1:
                            party = _party[position+len('место совершения операции:'):].strip()
                            
                description = parts[0]
                if 'Операция по карте: ' in description:
                    source = description[len('Операция по карте: '):]
            if len(parts) == 2: # Внутрибанковский перевод между счетами, ФИО.Со счёта DDD на счёт DDD
                subcategory = parts[0]
                if result := account_pattern.findall(parts[1]):
                    source = result[0]
                    party = result[1]
                description = _description
            else:
                description = _description
                # Категория: Перевод по СБП.Перевод C421806240013655 через Систему быстрых платежей на +7XXXXXXXX. Без НДС.
                parts = _description.split('.')
                if 'Категория: ' in parts[0]:
                    subcategory = parts[0][len('Категория: '):]
                    if result := phone_pattern.search(parts[1]):
                        party = result.group(0)
                    elif result := sbp_payment_pattetn.match(parts[1]):
                        party = result.group(1)
            if mcc and str(mcc)  in mcc_codes:
                subcategory = mcc_codes[str(mcc)][0]
            dest = {
                dest_headers[0]: row[0],
                dest_headers[1]: row[1],
                dest_headers[2]: row[3],
                dest_headers[3]: row[4],
                dest_headers[4]: subcategory,
                dest_headers[5]: mcc,
                dest_headers[6]: source,
                dest_headers[7]: party,
                dest_headers[8]: description,
                dest_headers[9]: row[12],
                dest_headers[10]: row[14],
            }
            print(";".join([str(f) for f in dest.values()]), file=output)
