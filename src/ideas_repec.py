import argparse
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from random import randint
from time import sleep

class IDEASRePEc:

    def __init__(self):
        self.timeout = args.timeout
        self.sleep = args.sleep
        self.user_agent = args.user_agent
        self.file_name = args.file_name

    def get_link(self, headers):
        url = 'https://logec.repec.org/RAS/'
        try:
            res = requests.get(url, timeout=self.timeout, headers=headers)
            content = BeautifulSoup(res.content, features='html.parser')
            link = content.find('div', {'class': 'sidebar'}).find_all('a')
            link = [x.get('href') for x in link]
            link = [x for x in link if '/RAS/' in  x]
            return link
        except Exception:
            sleep(self.sleep)
            pass
        
    def get_author(self, link, headers):
        url = f'https://logec.repec.org/{link}'
        try:
            res = requests.get(url, timeout=self.timeout, headers=headers)
            content = BeautifulSoup(res.content, features='html.parser')
            author = content.find('table').find_all('a')
            author = [x.get('href') for x in author]
            return author
        except Exception:
            sleep(self.sleep)
            pass

    def statistics(self, author, headers, index, total_column, total_value):
        try:
            url = f'https://logec.repec.org{author}'
            res = requests.get(url, timeout=self.timeout, headers=headers)
            content = BeautifulSoup(res.content, features='html.parser')
            table = content.find_all('table', {'class': 'stats'})
            column = table[index].find('tr', {'class': 'rowwithtopborder'}).get_text().split('\n')
            column = [x.replace(' ', '_').lower() for x in column if x != '']
            sub_column = table[index].find('tr', {'class': 'rowwithbottomborder'}).get_text().split('\n')
            sub_column = [x.replace(' ', '_').lower() for x in sub_column if x != '']
            cols = []
            for i in column[1:]:
                for j in sub_column[:4]:
                    cols.append(f'{i}_{j}')
            cols.insert(0, column[0])
            df = table[index].find_all('tr')[2:]
            df = [x.get_text().split('\n') for x in df]
            df = [[x for x in w if x != ''] for w in df]
            df = pd.DataFrame(df)
            df.columns = cols
            df.insert(0, 'author', content.find('title').get_text().replace('LogEc: Access Statistics for ', ''))
            df.insert(1, 'id', url)
            df = df[df[total_column] != total_value]
            return df
        except UnboundLocalError:
            return None
        except Exception:
            sleep(self.sleep)
            pass

def main():
    ir = IDEASRePEc()
    headers = {'User-Agent': ir.user_agent}
    link = ir.get_link(headers)
    length_link = len(link)
    i = 0
    while i < args.author:
        try:
            author = ir.get_author(link[randint(0, length_link)], headers)
            author = [x for x in author if 'default' not in x and '/RAS/' in x]
            total_author = len(author)
            df = ir.statistics(
                author=author[randint(0, total_author)],
                headers=headers,
                index=args.index,
                total_column=args.column,
                total_value=args.value
            )
            file_name = args.file_name
            if os.path.exists(file_name):
                existing = pd.read_csv(file_name)
                df = pd.concat([df, existing], sort=False)
                df = df.drop_duplicates()
                df = df.reset_index(drop=True)
                df = df.sort_values(by='author', ascending=True)
                df.to_csv(file_name, index=False)
            else:
                df.to_csv(file_name, index=False)
        except IndexError:
            pass
        except TypeError:
            pass
        except AttributeError:
            pass
        i += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a',
        '--author',
        type=int,
        default=10,
        help='How many author(s) will be scraped (default is 10)',
        metavar=''
    )
    parser.add_argument(
        '-t',
        '--timeout',
        type=int,
        default=5,
        help='How long for each request before it timed out in seconds (default is 5)',
        metavar=''
    )
    parser.add_argument(
        '-s',
        '--sleep',
        type=int,
        default=5,
        help='How long to make time interval between iterations in case exception occurs in seconds (default is 1)',
        metavar=''
    )
    parser.add_argument(
        '-u',
        '--user_agent',
        type=str,
        default='user-agent',
        help='User agent used for headers (default is user-agent)',
        metavar=''
    )
    parser.add_argument(
        '-i',
        '--index',
        type=int,
        default=0,
        choices=[0, 1],
        help='Table index. 0 = working papers; 1 = journal articles (default is 0)',
        metavar=''
    )
    parser.add_argument(
        '-c',
        '--column',
        type=str,
        default='working_paper',
        choices=['working_paper', 'journal_article'],
        help='Total column name (default is working_paper)',
        metavar=''
    )
    parser.add_argument(
        '-v',
        '--value',
        type=str,
        default='Total Working Papers',
        choices=['Total Working Papers', 'Total Journal Articles'],
        help='Total column value (default is Total Working Papers)',
        metavar=''
    )
    parser.add_argument(
        '-f',
        '--file_name',
        type=str,
        default='./data/working-paper.csv',
        choices=['./data/working-paper.csv', './data/journal-article.csv'],
        help='Ouput file path (default is ./data/working-paper.csv)',
        metavar=''
    )
    args = parser.parse_args()
    main()
