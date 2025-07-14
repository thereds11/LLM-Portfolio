import json
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import ollama
import time
import re
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer

def getNewsData(query):
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }
    response = requests.get(
        f"https://www.google.com/search?q={query}&gl=us&tbm=nws&num=100", headers=headers
    )
    soup = BeautifulSoup(response.content, "html.parser")
    news_results = []
    for el in soup.select("div.SoaBEf"):
        title = el.select_one("div.MBeuO").getText(strip=True)
        snippet = el.select_one(".GI74Re").getText(strip=True)
        combined_text = f"{title} {snippet}"
        keywords = extract_keywords_with_llama(combined_text)

        news_results.append({
                "title": title,
                "link": el.select_one("a").get("href"),
                "source": el.select_one("div.NUnG9d span").getText(strip=True),
                "snippet": snippet,
                "date": el.select_one(".LfVVr").getText(strip=True),
                "keywords": keywords
            })
        time.sleep(1) 

    print(json.dumps(news_results, indent=2))
    with open("news_data.csv", "w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["title", "link", "source", "snippet", "date", "keywords"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(news_results)
        print("Data saved to news_data.csv")

def extract_keywords_with_llama(text):
    try:
        prompt = (
            "Extract 3 to 5 short, relevant keywords from the following news headline and snippet. "
            "Return only the keywords, separated by commas — no explanations, no preamble, no formatting hints:\n\n"
            f"{text}\n\n"
            "Keywords:"
        )

        response = ollama.chat(
            model='llama3',
            messages=[{"role": "user", "content": prompt}]
        )
        raw_output = response['message']['content']
        keywords_line = re.findall(r"[A-Za-z0-9\s,\-]+", raw_output)
        if keywords_line:
            clean_keywords = [kw.strip() for kw in keywords_line[-1].split(",")]
            print(clean_keywords)
            return ", ".join(clean_keywords)
        else:
            return ""

    except Exception as e:
        print(f"Keyword extraction failed for: {text[:60]}... \nError: {e}")
        return ""

# def cluster_news():
#     # Read the news data and pick out title and keywords for embedding
#     df = pd.read_csv("news_data.csv", encoding="utf-8")
#     df.dropna(subset=["title", "keywords"], inplace=True)
    
#     # Combine title and keywords for embedding
#     df["text_for_embedding"] = df["title"] + "Keywords: " + df["keywords"]
#     texts = df["text_for_embedding"].tolist()

#     # Initialize the SentenceTransformer model
#     model = SentenceTransformer("all-MiniLM-L6-v2")
#     embeddings = model.encode(texts, show_progress_bar=True)

#     # Apply KMeans Clustering
#     kmeans = KMeans(n_clusters=5, random_state=42)
#     df["clusters"] = kmeans.fit_predict(embeddings)

#     for cluster_id in sorted(df["clusters"].unique()):
#         print(f"Cluster {cluster_id}:")
#         cluster_df = df[df["clusters"] == cluster_id]
#         texts = (cluster_df["title"] + ". " + cluster_df["snippet"]).tolist()

#         summary = summerize_cluster(texts)
#         print(f"Summary: {summary}\n")
#         for _, row in cluster_df.iterrows():
#             print(f"• {row['title']}")

# def summerize_cluster(texts):
#     joined_text = "\n".join(f"- {text}" for text in texts[:10])
#     prompt = (
#         "summerize the following news headlines into a short paragraph(2-3 sentences)"
#         "Do not list individual articles. Be concise and clear. \n\n"
#         f"{joined_text}\n\n"
#         "Summary:"
#     )

#     try:
#         response = ollama.chat(
#             model='llama3',
#             messages=[{"role": "user", "content": prompt}]
#         )
#         return response['message']['content'].strip()
#     except Exception as e:
#         print(f"Failed to summarize cluster: {e}")
#         return "Summary not available."
getNewsData("openAI")
# cluster_news()