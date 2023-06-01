<h1 align="center">
📖 The Latest 📖
</h1>

Get the very latest in any field, from research to news, delivered right to your inbox to read over breakfast. The Latest provides you with the absolute most up-to-date research and developments by grabbing and summarising the most recent research papers from arXiv. Future chain-of-thought-based features will enable The Latest to be multi-modal, including using graphs and images from papers to provide input into summaries.

## 🔧 Features

- Intuitive UI to select which catagories are of interest.
- Mix and match how you would like the papers to be summarised, from the number of papers (based on the cost and time it would take to read them all!), the length of each summary (single to sentence to a whole paragraph) and the reading level.
- The server will run 

## 📩 Subscribe to TheLatest

Coming soon to a hosted web app near you. 

## 💻 Running Locally

1. Clone the repository📂

```bash
git clone https://github.com/AlexanderOllman/TheLatest
cd TheLatest
```

2. Install dependencies 🔨

```bash
pip3 install -r requirements.txt
```

3. Run the app! 🚀

If you're just looking to try it out, run:

```bash
run main.py
```

If you're setting up a local server

## 🚀 Upcoming Features

- Add more catagories.
- Style better.
- Host app on EC2 instance to save user preferences and send out emails to users, based on my own OpenAI key. 
- Upgrade the EC2 to run a local LLM (Alpaca, Vicuna, etc) to generate summaries.
- Add email function (users can add this if they want to run their own TheLatest server locally). 
- Add support for scraping and summarising more sources (e.g. webpages 🕸️, relevant sub-Reddits 📊, news articles, etc.)
- Add specific sources, such as Microsoft, Google and OpenAI publications (most are already on arXiv)
- Feature and prioritise sources.
- Multi-modal summarising. 
