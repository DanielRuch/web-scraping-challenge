from splinter import Browser
from bs4 import BeautifulSoup


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "C:\Program Files (x86)\ChromeDriver\chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)


def scrape(url, clickBool = False, linkId = "" ):
    browser = init_browser()

    browser.visit(url)

    #If a cicked is needed, click based on the id given
    if clickBool == True:
        browser.click_link_by_id(linkId)
    
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    # return soup object
    return soup

#1. Scrape latest news article
article = {}

url = "https://mars.nasa.gov/news/"

soup = scrape(url)

#Get title & text and save into dict
title = soup.find("div", class_="content_title").find("a", target="_self").get_text()
text = soup.find("div", class_="article_teaser_body").get_text()
articles["title"] = title
articles["text"] = text

#Print to confirm were saved
print(articles["title"])
print(articles["text"])

#END 1.

#2. Scrape JPL Mars Space Images - Featured Image
url1 = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"

#Scrape the site after clicking the full image buttton
soup1 = scrape(url1)
link1 = soup1.find("a", id="full_image")

#Build secondary url
url2 = "https://www.jpl.nasa.gov"
url2 = url2 + link1["data-link"]

soup2 = scrape(url2)

#Get hires image link
link2 = soup2.find("img", class_="main_image")

#Build final url
urlFinal = "https://www.jpl.nasa.gov"
urlFinal = urlFinal + link2["src"]

featuredImageUrl = urlFinal

print(featuredImageUrl)
