import re, os, sys, datetime, time
import pandas
import urllib
from selenium import webdriver
from contextlib import closing
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pattern.web import URL, extension, cache, plaintext, Newsfeed, DOM

 
class GoogleImageExtractor(object):
 
    def __init__(self, search_key = '' ):

        if type(search_key) == str:
            self.g_search_key_list = [search_key]
        elif type(search_key) == list:
            self.g_search_key_list = search_key
        else:
            print 'google_search_keyword not of type str or list'
            raise
 
        self.g_search_key = ''
        self.image_dl_per_search = 200
        self.prefix_of_search_url = "https://www.google.com.sg/search?q="
        self.postfix_of_search_url = '&source=lnms&tbm=isch&sa=X&ei=0eZEVbj3IJG5uATalICQAQ&ved=0CAcQ_AUoAQ&biw=939&bih=591'# non changable text
        self.target_url_str = ''
 
        self.pic_url_list = []
        self.pic_info_list = []
 
        self.folder_main_dir_prefix = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'gimage_pic')
 
    def reformat_search_for_spaces(self):
        self.g_search_key = self.g_search_key.rstrip().replace(' ', '+')
 
    def set_num_image_to_dl(self, num_image):
        self.image_dl_per_search = num_image
 
    def get_searchlist_fr_file(self, filename):
        with open(filename,'r') as f:
            self.g_search_key_list = f.readlines()
 
    def formed_search_url(self):
        self.reformat_search_for_spaces()
        self.target_url_str = self.prefix_of_search_url + self.g_search_key +\
                                self.postfix_of_search_url
 
    def retrieve_source_fr_html(self):
        driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'chromedriver'))
        driver.get(self.target_url_str)
 
        try:
            driver.execute_script("window.scrollTo(0, 30000)")
            time.sleep(2)
            self.temp_page_source = driver.page_source
            driver.find_element_by_id('smb').click() #ok
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 60000)")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 60000)")
 
        except:
            print 'not able to find'
            driver.quit()
 
        self.page_source = driver.page_source
 
        driver.close()
 
    def extract_pic_url(self):
        dom = DOM(self.page_source)
        tag_list = dom('a.rg_l')
 
        for tag in tag_list[:self.image_dl_per_search]:
            tar_str = re.search('imgurl=(.*)&imgrefurl', tag.attributes['href'])
            try:
                self.pic_url_list.append(tar_str.group(1))
            except:
                print 'error parsing', tag
 
    def multi_search_download(self):
        for indiv_search in self.g_search_key_list:
            self.pic_url_list = []
            self.pic_info_list = []
 
            self.g_search_key = indiv_search
 
            self.formed_search_url()
            self.retrieve_source_fr_html()
            self.extract_pic_url()
            self.downloading_all_photos() #some download might not be jpg?? use selnium to download??
            self.save_infolist_to_file()
 
    def downloading_all_photos(self):
        self.create_folder()
        pic_counter = 1
        for url_link in self.pic_url_list:
            print pic_counter
            pic_prefix_str = self.g_search_key  + str(pic_counter)
            self.download_single_image(urllib.unquote(url_link), pic_prefix_str)
            pic_counter = pic_counter +1
 
    def download_single_image(self, url_link, pic_prefix_str):
        self.download_fault = 0
        file_ext = os.path.splitext(url_link)[1] #use for checking valid pic ext
        temp_filename = pic_prefix_str + file_ext
        temp_filename_full_path = os.path.join(self.gs_raw_dirpath, temp_filename )
 
        valid_image_ext_list = ['.png','.jpg','.jpeg', '.gif', '.bmp', '.tiff'] #not comprehensive
 
        url = URL(url_link)
        if url.redirect:
            return # if there is re-direct, return
 
        if file_ext not in valid_image_ext_list:
            return #return if not valid image extension
 
        f = open(temp_filename_full_path, 'wb') # save as test.gif
        print url_link
        self.pic_info_list.append(pic_prefix_str + ': ' + url_link )
        try:
            f.write(url.download())#if have problem skip
        except:
            print 'Problem with processing this data: ', url_link
            self.download_fault =1
        f.close()
 
    def create_folder(self):
        self.gs_raw_dirpath = os.path.join(self.folder_main_dir_prefix, time.strftime("_%d_%b%y", time.localtime()))
        if not os.path.exists(self.gs_raw_dirpath):
            os.makedirs(self.gs_raw_dirpath)
 
    def save_infolist_to_file(self):
        temp_filename_full_path = os.path.join(self.gs_raw_dirpath, self.g_search_key + '_info.txt' )
 
        with  open(temp_filename_full_path, 'w') as f:
            for n in self.pic_info_list:
                f.write(n)
                f.write('\n')
 
if __name__ == '__main__':
 
    choice =4
 
    if choice ==4:
        """test the downloading of files"""
        w = GoogleImageExtractor('')#leave blanks if get the search list from file
        searchlist_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'imgsearch_list.txt')
        w.set_num_image_to_dl(20)
        w.get_searchlist_fr_file(searchlist_filename)#replace the searclist
        w.multi_search_download()