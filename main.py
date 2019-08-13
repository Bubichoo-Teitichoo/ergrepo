import requests
from html.parser import HTMLParser
import os
import json


def SanatizeFileName(filename : str):
    filename = filename.replace('\n', '').replace('(', '_').replace(')', '_').replace('+', '_').replace('/', '_').replace('-', '_').replace('%', 'pct').replace(':', '_').replace('*', 'x').replace(' ', '')
    filename = filename.replace('"', '').replace('@', 'at').replace('?', '').replace('>', 'over').replace('<', 'under').replace('#', 'nr').replace('!', '').replace('[', '').replace(']', '_').replace('.', '')
    return filename

class MRCFile:
    def __init__(self, filename : str, description : str = 'Generic Description'):
        self.__filename =  filename
        if '.mrc' != self.__filename[-4:]:
            self.__filename += '.mrc'
        wipefile = self.__filename[:-4] + '.wipe.mrc'
        self.__outfile = open(self.__filename, 'wb+')
        open(wipefile, 'wb+').close()
        open(wipefile + '.plan', 'wb+').close()
        self.__data_lst = []
        self.__WriteHeader(filename, description)


    def __del__(self):
        self.__WriteLine('[COURSE DATA]')
        time = 0.0
        for data_point in self.__data_lst:
            self.__WriteLine('%.02f\t%d'%(time, data_point['start']))
            time += data_point['time']
            self.__WriteLine('%.02f\t%d'%(time, data_point['end']))
        self.__WriteLine('[END COURSE DATA]')
        self.__outfile.close()
    
    def __WriteHeader(self, filename : str, description : str ):
        self.__WriteLine('[COURSE HEADER]')
        self.__WriteLine('VERSION = 2')
        self.__WriteLine('UNITS = ENGLISH')
        self.__WriteLine('DESCRIPTION = %s'%description)
        self.__WriteLine('FILE NAME = %s'%filename[filename.rfind('/')+1:])
        self.__WriteLine('MINUTES PERCENT')
        self.__WriteLine('[END COURSE HEADER]')

    def __WriteLine(self, Line : str):
        self.__outfile.write(str.encode(Line + '\n'))

    def AddDataPoint(self, time : float, start : int, end : int):
        self.__data_lst.append({'time': time, 'start': start, 'end': end})

        
            
class ErgDBScraper(HTMLParser):
    def __init__(self, outdir : str = './MRC', url : str = 'http://ergdb.org'):
        HTMLParser.__init__(self)
        self.__outdir = outdir
        self.__url = url
        self.__nextlink = url + '/search'

    def Scrape(self):
        while len(self.__nextlink):
            print('Scraping to', self.__nextlink)
            response = requests.get(url = self.__nextlink)
            self.feed(response.text)

    def handle_starttag(self, tag, attrs):
        if any(key == 'class' and 'wpv-filter-next-link' in value for key, value in attrs):
            for key, value in attrs:
                if key == 'href':
                    self.__nextlink = self.__url + value

        elif any(key == 'class' and 'downloadMrc' in value for key, value in attrs):
            for key, value in attrs:
                if key =='onclick':
                    ovalue = value
                    value = value[value.find('(')+1 : value.rfind(')')]
                    value, _ = self.__crop(value)
                    value, wname = self.__crop(value)
                    value, _ = self.__crop(value) 
                    wdata = value[value.find('[['): value.find(']]')+2]
                    value = value[value.find(']]'):]
                    value, wcreator = self.__crop(value) 

                    try:
                        if len(wdata):
                            pjson = json.loads(wdata)
                            odir = self.__outdir + '/%s/'%SanatizeFileName(wcreator)
                            if not os.path.isdir(odir):
                                os.makedirs(odir)
                            outfile = MRCFile(odir + SanatizeFileName(wname), 'Creator: %s'%wcreator)
                            for time, start, end in pjson:
                                outfile.AddDataPoint(time, start, end)
                        else:
                            print('Skipping', wname)
                    except Exception as e:
                        print(ovalue)
                        print(e)
                        exit()
    def feed(self, d):
        self.__nextlink = ''
        HTMLParser.feed(self, data = d)

    def __crop(self, value_str : str) -> (str, str):
        value_str = value_str[value_str.find("'")+1:]
        retval = value_str[:value_str.find("'")]
        value_str = value_str[value_str.find("'")+1:]
        return (value_str, retval)


p = ErgDBScraper()
p.Scrape()
   