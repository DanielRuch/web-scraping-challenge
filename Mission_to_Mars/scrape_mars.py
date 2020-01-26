#Dependencies
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, jsonify, render_template, redirect, url_for
from flask_pymongo import PyMongo

#Functions
def init_browser():
    executable_path = {"executable_path": "C:\Program Files (x86)\ChromeDriver\chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=True)


def scrapeSite(url, clickBool = False, linkId = "" ):
    browser = init_browser()

    browser.visit(url)

    #If a cicked is needed, click based on the id given
    if clickBool == True:
        browser.click_link_by_id(linkId)
    
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    # return soup object
    return soup

def scrape():
    #Get existing data from database
    dbReply = getInfo()

    #Dictionary for information
    marsInfo = {}
    marsInfo["name"] = "Mars Info"

    #Update existing value or add if none exists
    d = {"name" : "Mars Info"}
    dbReply.update(d)

    #1.1 - Scrape latest news article
    url = "https://mars.nasa.gov/news/"

    soup = scrapeSite(url)

    #Get title & text and save into dict
    try:
        title = soup.find("div", class_="content_title").find("a", target="_self").get_text()
        text = soup.find("div", class_="article_teaser_body").get_text()
    except:
        title = "Failed to retrieve data"
        text = ""
    
    marsInfo["news_title"] = title
    marsInfo["news_text"] = text

    print("Step 1.1 Done")

    #1.2 - Scrape JPL Mars Space Images - Featured Image
    url1 = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"

    #Scrape the site after clicking the full image buttton
    soup1 = scrapeSite(url1)

    try:
        link1 = soup1.find("a", id="full_image")

        #Build secondary url
        url2 = "https://www.jpl.nasa.gov"
        url2 = url2 + link1["data-link"]

        soup2 = scrapeSite(url2)

        #Get hires image link
        link2 = soup2.find("img", class_="main_image")

        #Build final url
        urlFinal = "https://www.jpl.nasa.gov"
        urlFinal = urlFinal + link2["src"]
        featuredImageUrl = urlFinal
    except:
        featuredImageUrl = "Failed to retrieve data"

    
    marsInfo["featured_image_url"] = featuredImageUrl

    print("Step 1.2 Done")

    #Mars weather from twitter skipped - see file in root directory of homework. Beautifulsoup/Splinter receiving error message from twitter

    #1.4 - Mars Facts
    #Get site data
    soup = scrapeSite("https://space-facts.com/mars/")

    #Try to retrieve data
    try:
        text = soup.find_all("table")
        df = pd.read_html(str(text))[0]
        tableHtml = df.to_html()
    except:
        tableHtml = "Failed to Retrieve Data"
    
    marsInfo["marsFactsTable"] = tableHtml

    print("Step 1.4 Done")
    #1.5  - Mars Hemispheres
    #Website down at time of homework (1/25-1/26), will revisit when website working
    return marsInfo

def getInfo():
    dbReply = mongo.db.marsInfo.find_one()
    
    return dbReply

#Temporary approach for testing:
tempTable = {}
tempTable["news_title"] = "Nine Finalists Chosen in NASA's Mars 2020 Rover Naming Contest" 
tempTable["news_text"] = "Nine finalists have been chosen in the essay contest for K-12 students across U.S. to name NASA's next Mars rover. Now you can help by voting for your favorite. "
tempTable["featured_image_url"] = "https://www.jpl.nasa.gov/spaceimages/images/largesize/PIA19871_hires.jpg"


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

# Define database and collection
marsData = mongo.db.marsInfo

#################################################
# Flask Routes
#################################################

@app.route("/")
def index():
    """Generate html page"""
    
    # Get info from MongoDb
    dbReply = getInfo()

    # Return the template with the teams list passed in
    #return render_template('index.html', newsTitle=tempTable["news_title"], newsText=tempTable["news_text"], imageLink=tempTable["featured_image_url"])
    return render_template('index.html', marsData = dbReply)

@app.route("/scrape")
def new_scrape():
    """Get updated info"""
    scrapeData = scrape()

    marsData.update({}, scrapeData, upsert=True)
    
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)