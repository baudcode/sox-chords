from abc import abstractmethod, abstractproperty
from bs4 import BeautifulSoup as bs
from os.path import join, exists
from os import makedirs, remove
from requests import get as request_get
from sys import stdout
from pickle import load as pickle_load
from pickle import dump as pickle_dump


from sox_chords.util.utils import get_url_content
from sox_chords.exceptions import DataSetParseException, DataSetFetchException
from sox_chords.util.logger import pp


class PklDataSet(object):

    def __init__(self, pkl="DataSet.pkl", data_output_dir="download"):
        """
        Initialize DataSet with given pickle file if found
        
        :param pkl: str, location of pickle file which organizes the data
        :param data_output_dir: data output directory of the dumped files, will be created if it does not exist
        """
        self.pkl = pkl
        self.data_output_dir = data_output_dir

        if not exists(data_output_dir):
            makedirs(data_output_dir)
        if exists(pkl):
            self.data = pickle_load(open(self.pkl, "rb"))
        else:
            self.data = None

    def get(self):
        """
        Retrieves or loads the data set
        :return: map, data set
        """
        if not self.data:
            self.data = self._get()
            with open(self.pkl, "wb") as handler:
                pickle_dump(self.data, handler)

        return self.data

    @abstractmethod
    def _get(self):
        """
        Retrieves the data set representation
        :return: dict,  data set 
        """
        pass

    @abstractproperty
    def url(self):
        """ website url to retrieve the data set from"""
        pass

    def _download(self, urls=None):
        """
        Download all urls to download dir
        :param urls: list, urls to download
        :return: map, [url] = abs_download_path
        """
        content = {}
        for i in range(len(urls)):

            name = urls[i].split("/")[-1]
            path = join(self.data_output_dir, name)

            try:
                if not exists(path):
                    PklDataSet.__download_file(url=urls[i], destination=path, d_num=i, d_nums=len(urls))

            except DataSetFetchException as e:
                print ("Error while downloading data set", e)
            else:
                content[urls[i]] = path

        return content

    @staticmethod
    def __download_file(url="", destination="", d_num=1, d_nums=10, progress=True):
        """ Download a file to destination"""

        r = request_get(url, stream=True)
        if r.status_code == 200:

            total_length = r.headers.get('content-length')
            try:
                with open(destination, 'wb') as f:
                    if total_length is None:
                        if progress:
                            stdout.write("\r[Downloading %i of %i][%s%s]" %
                                         (d_num, d_nums, '=' * 20 + 'please wait' + '=' * 19, ''))
                            stdout.flush()
                        f.write(r.content)
                    else:
                        dl = 0
                        total_length = int(total_length)
                        for data in r.iter_content(chunk_size=4096):
                            dl += len(data)
                            f.write(data)
                            done = int(50 * dl / total_length)
                            if progress:
                                stdout.write("\r[Downloading %i of %i][%s%s]" %
                                             (d_num, d_nums, '=' * done, ' ' * (50 - done)))
                                stdout.flush()
            except IOError as io_err:
                raise DataSetFetchException("Could not download because of invalid rights or no disk space left:" + url)
        else:
            raise DataSetFetchException("Could not download because the file was not found on the server: " + url)

    @staticmethod
    def helper(url, parse):
        """
        A helper method to parse content from a url
        :param url: str, content to retrieve from
        :param parse: func, parse function expecting data as one argument
        :return: parse(data)
        """
        try:
            data = bs(get_url_content(url), 'html.parser')
            return parse(data)

        except AttributeError as attr_err:
            raise DataSetParseException("Could not parse " + url)
        except KeyError as key_err:
            raise DataSetParseException("Could not parse " + url)


class OneClassicalDataSet(PklDataSet):

    url = 'http://1classical.com/'

    by_instrument = "download_free_classical_music_MP3_browse_by_instrument.php"

    def _get(self):
        """
        Retrieves the data set model
        :return: map, [instrument][composer][piece][tempo] = abs_download_path
        """
        mapping = {}
        urls = []

        website_dump = OneClassicalDataSet.__name__ + ".dump.pkl"
        if exists("dump.pkl"):
            pp("Restoring Website Information...")
            urls, mapping = pickle_load(open(website_dump, "rb"))
        else:
            pp("Retrieving Website Information for " + self.url)
            for ref_instrument in self._get_ref_links(self.url + self.by_instrument):
                instrument = ref_instrument.split("=")[1]
                # print ("Instrument: ", ref_instrument, instrument)
                mapping[instrument] = {}
                for ref_composer in self._get_ref_links(self.url + ref_instrument):
                    composer = ref_composer.split("=")[1].split("-")[1].strip()
                    # print ("Composer: ", ref_composer, composer)
                    mapping[instrument][composer] = {}
                    for ref_piece in self._get_ref_links(self.url + ref_composer):

                        piece = ref_piece.split("=")[1].split("-")[1].strip()
                        downloads = self._get_downloads(self.url + ref_piece)
                        print (instrument, composer, piece, downloads)
                        mapping[instrument][composer][piece] = downloads
                        urls += list(map(lambda tempo: downloads[tempo], downloads))

            pickle_dump((urls, mapping), open(website_dump, "wb"))
        # Download Data Set
        content = self._download(urls=list(set(urls)))
        # Mapping File Paths to Data Set
        to_remove = []
        for i in mapping:
            for c in mapping[i]:
                for p in mapping[i][c]:
                    for t in mapping[i][c][p]:
                        if mapping[i][c][p][t] in content:
                            mapping[i][c][p][t] = content[mapping[i][c][p][t]]
                        else:
                            to_remove.append([i, c, p, t])

        # Remove all mapping where audio could not be downloaded
        for item in to_remove:
            del(mapping[item[0]][item[1]][item[2]][item[3]])

        # Remove website dump
        remove(website_dump)

        return mapping

    @staticmethod
    def _get_ref_links(url=""):
        def get(data):

            table = data.find('table')
            a_tags = table.find_all('a')
            return map(lambda a: a.get('href'), a_tags)

        return PklDataSet.helper(url, get)

    @staticmethod
    def _get_downloads(url=""):
        def get(data):
            mapping = {}
            for tr in data.find_all('tr'):
                tds = tr.find_all('td')
                if len(tds) == 2 and tds[1].div.a is not None:
                    if tds[1].div.a.get("href").strip() != "":
                        mapping[tds[0].string] = tds[1].div.a.get("href")

            return mapping

        return PklDataSet.helper(url, get)


class RoyalityFreeSounds(PklDataSet):

    def _get(self):
        def get_mp3s(page):
            soup = bs(get_url_content(self.get_url(page)), "html.parser")
            links = []
            for td in soup.find_all("td"):
                for a in td.find_all("a", href=True):
                    if a.get("class") is None:
                        if a.get("href").endswith(".mp3"):
                            links.append(a.get("href"))
            return links

        def get_max_pages():
            soup = bs(get_url_content(self.get_url(1)), "html.parser")
            return int(soup.find_all("a", {"class": "paged"})[-1].string)

        mp3s = []
        for page in range(1, get_max_pages() + 1):
            print("[*] fetching page ", page)
            mp3s += get_mp3s(page)

        return self._download(mp3s)

    def get_url(self, page):
        return (self.url() + "royalty-free-sounds-%d.html") % page

    def url(self):
        return "http://soundbible.com/"

if __name__ == '__main__':
    """
    d = OneClassicalDataSet(pkl="OneClassical.pkl", data_output_dir="/mnt/data/datasets/" +
                                                                    OneClassicalDataSet.__name__)
    """
    d = RoyalityFreeSounds(pkl=RoyalityFreeSounds.__name__,
                           data_output_dir="/mnt/intern/datasets/" + RoyalityFreeSounds.__name__)

    print (d.get())
