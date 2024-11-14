import requests
import os
import re
import argparse

from PIL import Image
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileWriter, PdfFileReader

MAIN_PATH = os.getcwd()
IMG_PATH  = os.path.join(MAIN_PATH, 'one-piece-images')
CHPT_PATH = os.path.join(MAIN_PATH, 'one-piece-chapters')

def make_path(path):    
    
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

def all_chapter(start, stop):
    '''All chapters for Naruto'''
    
    stop = stop + 1

    for chapter in range(start, stop):
        get_pages(chapter)

    print("Successfully chapters are stored in one-piece-chapters folder")

    try:
        os.remove(IMG_PATH)
    except PermissionError:
        print("You have to manually delete the one-piece-images folder")

def get_pages(chapter: int):
    '''Gets all the pages from the URL'''

    url = "https://w11.read-onepiece.com/manga/one-piece-chapter-{}".format(chapter)

    response = request(url)
    soup = BeautifulSoup(response.text, "html.parser")
    div_classes = soup.find("div", attrs={"class":"entry-content"}) # finds the class which holds the images
    p_classes = div_classes.find_all("p")
    urls = []

    for p_class in p_classes:
        try:
            url = p_class.find("img").get("src") # finds the element which holds the image url
            urls.append(url)
        
        except:
            pass

    image_urls = save_image(urls)

    img_pdf = pdf(chapter, image_urls)

    return img_pdf

def save_image(urls: list) -> list:

    image_urls = []

    for url in urls:
        try:
            response = request(url)

            soup = BeautifulSoup(response.text, "html.parser")
        
            re_url = re.match('https:\/\/readoverlordmanga\.com.*(\/.*)', url) # matches the urls to get the image number to save 

            new_url = re_url.group(1)

            image_urls.append(new_url)
            make_path(IMG_PATH)

            with open(IMG_PATH +"\\"+ new_url, "wb") as img:
                img.write(response.content)
        except:
            pass
    return image_urls

def pdf(chapter: int, image_urls: list):
    '''Pdf Converter to convert images into pdf'''

    list_url = []
    IMG_PATH = os.path.join(MAIN_PATH, 'one-piece-images')

    for image_url in image_urls:
        page = Image.open(IMG_PATH +"\\"+ image_url)
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
    
    all_chapter(start, stop)
    # get_pages(105)