from PIL import Image
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileWriter, PdfFileReader

import argparse
import requests
import re
import os


MAIN_PATH = os.getcwd()
IMG_PATH  = os.path.join(MAIN_PATH, 'detective-images')
CHPT_PATH = os.path.join(MAIN_PATH, 'detective-chapters')

def make_path(path):    
    
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

def all_chapter(start, stop):
    '''All chapters for Detective'''
    
    stop = stop + 1

    for chapter in range(start, stop):
        get_pages(chapter)
    print("Successfully chapters are stored in detective-chapters folder")

    try:
        os.remove(IMG_PATH)
    except PermissionError:
        print("You have to manually delete the detective-images folder")

def get_pages(chapter: int):
    '''Gets all the pages from the URL'''

    url = "https://detectiveconan.online/manga/detective-conan-chapter-{}/".format(chapter)
    response = request(url)
    
    soup = BeautifulSoup(response.text, "html.parser")

    div_classes = soup.find_all("div", attrs={"class":"separator"}) # finds the class which holds the images
    
    if div_classes == []:
        div_classes = soup.find_all("p", attrs={"class":"separator"})
    
    urls = []

    for div_class in div_classes:
        try:
            url = div_class.find("a").get("href") # finds the element which holds the image url
            urls.append(url)
        
        except:
            pass
    # print(urls)
    image_urls = save_image(urls)

    img_pdf = pdf(chapter, image_urls)

    return img_pdf

def save_image(urls: list) -> list:
    '''Saves images from url'''

    image_urls = []
    
    for url in urls:
        response = request(url)
        # response = requests.get(url)
        
        re_url = re.match('https:\/\/1\.bp\.blogspot\.com\/-.*\/s1600\/(.*)', url) # matches the urls to get the image number to save 
        new_url = re_url.group(1)

        image_urls.append(new_url)
        make_path(IMG_PATH)

        with open(IMG_PATH +"\\"+ new_url + ".jpg", "wb") as img:
            img.write(response.content)
    
    return image_urls

def pdf(chapter: int, image_urls: list):
    '''Pdf Converter to convert images into pdf'''

    list_url = []
    IMG_PATH = os.path.join(MAIN_PATH, 'detective-images')

    for image_url in image_urls:
        page = Image.open(IMG_PATH +"\\"+ image_url + ".jpg")
        pdf_page = page.convert('RGB') # Converting images for PDf
        list_url.append(pdf_page)

    make_path(CHPT_PATH)
    pdf_page.save(CHPT_PATH +"\\Chapter "+ str(chapter) + '.pdf', save_all=True, append_images=list_url)

    '''As pdfs are saving with extra last page at the start
    so the further step removes the first page i.e the end page'''

    pages_to_delete = [0] # page numbering starts from 0
    infile = PdfFileReader(CHPT_PATH +"\\Chapter "+ str(chapter) +'.pdf', 'rb')
    output = PdfFileWriter()

    for page in range(infile.getNumPages()):
        if page not in pages_to_delete:
            p = infile.getPage(page)
            output.addPage(p) 

    with open(CHPT_PATH +"\\Chapter "+ str(chapter) + '.pdf', 'wb') as op_file:
        output.write(op_file) # Saving images in pdf
    
    return op_file

def request(url: str):
    '''Returns get response for url'''

    return requests.get(url)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-start", help="Input page start ", nargs='+')
    parser.add_argument("-stop", help="input page stop", nargs='+')

    args = parser.parse_args()
    startJoin = ''.join(args.start)
    start = str(startJoin)
    stopJoin = ''.join(args.stop)
    stop = str(stopJoin)

    start = int(start)
    stop = int(stop)
    # get_pages(1)
    all_chapter(start, stop)
    