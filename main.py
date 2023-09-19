from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import io
import requests
from pypdf import PdfReader
import openai
import arxiv 
import smtplib

openai.api_key = "API-KEY"
openai.Model.list()



def getPaperTitle(id):
    search = arxiv.Search(id_list=[id])
    paper = next(search.results())
    return paper.title

def getCatagories(s):
    # Initialize the result strings
    result = ""
    substring = ""

    # Iterate over each character in the input string
    inside_parenthesis = False
    for c in s:
        # If we encounter an opening parenthesis, set the flag to True
        if c == "(":
            inside_parenthesis = True
        # If we encounter a closing parenthesis, set the flag to False
        elif c == ")":
            inside_parenthesis = False
        # If we're inside the parenthesis, append to substring
        elif inside_parenthesis:
            substring += c
        # Otherwise, append to the result string
        else:
            result += c

    # Return both the result string and the substring in the parenthesis
    return result, substring



def getArxivCatagories():
    # URL of the web page to fetch
    url = 'https://arxiv.org/category_taxonomy'

    # Fetch the web page content
    response = requests.get(url)
    html_doc = response.text

    # Parse the HTML document with BeautifulSoup
    soup = BeautifulSoup(html_doc, 'html.parser')
    accordion_bodies = soup.find_all('div', {'class': 'accordion-body'})

    catagories = []
    cat_titles = []

    for body in accordion_bodies:
        h4_tags = body.find_all('h4')
        for h4 in h4_tags:
            cat, title = getCatagories(h4.get_text())
            catagories.append(cat[:-1])
            cat_titles.append(title)
    return catagories, cat_titles

app = Flask(__name__)

readingLevel = ["a 12 year old reading level", "an 18 year old reading level", "an undergraduate reading level", ""]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Retrieve values from the form
        selected_option = request.form['options']
        email = request.form['email']
        number = int(request.form['number'])
        length = int(request.form['length'])
        level = readingLevel[int(request.form['reading'])]
        print(level)
        if len(request.form['key']) > 1:
            openai.api_key = request.form['key']


        titles, summarisedPapers, urls = getAndSummarisePapers(selected_option, number, level, length)
        print(titles, summarisedPapers, urls)
        #sendEmail(email, summarisedPapers)

        return render_template('summaries.html', titles=titles, summaries=summarisedPapers, urls=urls)
    
    #Initially render template
    levels = ["ELI5", "Easy Reading", "Undergraduate", "No simplification"]
    options, option_labels = getArxivCatagories()
    return render_template('index.html', levels=levels, options=options, option_labels=option_labels)

def showPaperSummary(paperContent):
    tldr_tag = "\n tl;dr:"
    paper_content = []

    for page in paperContent:    
        text = page + tldr_tag
        response = openai.Completion.create(model="text-davinci-003",prompt=text,temperature=0.1,
            max_tokens=400,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n"]
        )
        paper_content.append(response["choices"][0]["text"])
    
    return paper_content

def sendEmail(email, summarisedPapers):
    # Set up SMTP server and login credentials
    smtp_server = 'smtp.gmail.com'
    port = 587
    sender_email = 'your_email_address@gmail.com'
    sender_password = 'your_email_password'

    # Create a secure SMTP connection
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(sender_email, sender_password)

        #summarise all the papers
        message = '\n\n'.join(summarisedPapers)
        # Send email
        server.sendmail(sender_email, email, message)

def getAndSummarisePapers(option, number, level, length):

    # URL of the web page to fetch
    url = f'https://arxiv.org/list/{option}/pastweek?skip=0&show=50'

    # Fetch the web page content
    response = requests.get(url)
    html_doc = response.text

    #Initialise arrays
    paper_titles = []
    paper_summaries = []
    paper_urls = []

    # Parse the HTML document with BeautifulSoup
    soup = BeautifulSoup(html_doc, 'html.parser')

    # Find all <a> tags with title="Abstract"
    abstract_links = soup.find_all('a', attrs={'title': 'Abstract'})

    todays_papers = []
    # Extract the text content of each link and print it
    for link in abstract_links:
        todays_papers.append(link.text[6:])

    # URL of the PDF file to fetch and parse
    pdf_url = 'https://arxiv.org/pdf/'

    #Change the number of total papers. Max. 50. 
    if number:
        todays_papers = todays_papers[:number]
    else:
        todays_papers = todays_papers[0]

    print("Summarising...")

    for paper in todays_papers:
        paper_url = pdf_url + paper +".pdf"
        # Fetch the PDF file content
        response = requests.get(paper_url)
        pdf_content = response.content

        # Create a PyPDF2 PdfFileReader object from the PDF file content

        reader = PdfReader(io.BytesIO(pdf_content))
        number_of_pages = len(reader.pages)

        text_pages = []

        for page_num in range(number_of_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            text_pages.append(text)

        paperText = showPaperSummary(text_pages)
        paperAll = ""
        for page in paperText:
            paperAll = paperAll + " " + page

        print("Now summarising paper: " + paper)

        prompt = "Summarise this paper into " + length +" sentences " + level + " - including at least one an introduction and one a conclusion of findings/outcomes: " + paperAll
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "user", "content": prompt}]
        )

        response = completion['choices'][0]['message']['content']

        paper_summaries.append(response)
        paper_urls.append(paper_url)
        paper_titles.append(getPaperTitle(paper))
    # Define your function here
    return paper_titles, paper_summaries, paper_urls


if __name__ == '__main__':
    app.run(debug=True)
