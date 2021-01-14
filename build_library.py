import argparse
import string
import os

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLineHorizontal

from glob import glob
from io import StringIO

def query_dblp(title):
    import requests
    dblp_url = "http://dblp.org/search/publ/api"
    r = requests.post(dblp_url + f'?q="{title.strip()}"' +"&format=json&h=3&c=1")
    reply = r.json()
    if 'hits' not in reply['result'].keys():
        return None
    if 'hit' not in reply['result']['hits'].keys():
        return None
    return reply['result']['hits']['hit']

def filter_unicode(c):
    d = { 
        0xfb00:'ff',
        0xfb01:'fi',
        0xfb02:'fl',
        0xfb03:'ffi',
        0xfb04:'ffl',
        0xfb05:'ft',
        0xfb06:'st'
    }
    if len(c) and ord(c) in d.keys():
        return d[ord(c)]
    return c

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("-o", default="index.md", help="Output filename (.md)")
    parser.add_argument("-z", action="store_true", help="Titles only, no DBLP requests.")
    args = parser.parse_args()

    D = args.path + "**.pdf"

    outfile = open(args.o, 'w', encoding = 'utf8')

    for file in glob(D):
        with open(file, 'rb') as in_file:
            title = ""
            page0_layout = next(extract_pages(file))
            for element in page0_layout:
                if isinstance(element, LTTextContainer):
                    if element.y1 > 500:
                        for i,text_line in enumerate(element):
                            if isinstance(text_line, LTTextLineHorizontal) and text_line.height > 14:
                                for c in text_line.get_text():
                                    title += filter_unicode(c)

            title = title.replace('\n', ' ')
            print(f"- [{title}]({file})")
            print(f"- [{title}]({file})", file=outfile)
            if len(title) > 5 and not args.z:
                r = query_dblp(title)
                if r != None:
                    for e in r:
                        i = e['info']
                        s = f"  * {i['year']} [{i['title']}]({i['ee']})"
                        print(s)
                        print(s, file=outfile)
            else:
                s = f"{file} :\n  * Title not matched"
                print(s)
                print(s, file=outfile)
    
    outfile.close()