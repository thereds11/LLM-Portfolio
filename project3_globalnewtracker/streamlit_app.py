import pandas as pd
import streamlit as st
import ollama
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from app import getNewsData
import os

@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_data
def load_data():
    df = pd.read_csv("news_data.csv", encoding="utf-8")
    df.dropna(subset=["title", "keywords"], inplace=True)
    df["text_for_embedding"] = df["title"] + ". Keywords: " + df["keywords"]
    return df

def summarize_cluster(texts):
    joined_text = "\n".join(f"- {text}" for text in texts[:10])
    prompt = (
        "Given the following news headlines, generate a short, descriptive topic title (less than 10 words) that captures the common theme or subject. Return just the title — no sentences or explanation.\n\n"
        f"{joined_text}\n\nTopic:"
    )
    try:
        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()
    except Exception as e:
        return "Summary not available."

# UI
st.title("🌍 Global News Trends")
query = st.text_input("🔍 Enter a topic to fetch news about:", value="amazon")

if st.button("Fetch Latest News"):
    with st.spinner(f"Scraping Google News for '{query}'..."):
        getNewsData(query)
        st.success("News data updated! Please reload the page.")
    st.stop()  # Prevent loading old CSV after scrape

# Handle missing CSV
if not os.path.exists("news_data.csv"):
    st.warning("No data found. Please fetch news to get started.")
    st.stop()

# Load + Embed + Cluster
df = load_data()
model = load_model()
embeddings = model.encode(df["text_for_embedding"].tolist(), show_progress_bar=False)

k = st.sidebar.slider("Choose number of clusters", min_value=2, max_value=10, value=5)
kmeans = KMeans(n_clusters=k, random_state=42)
df["cluster"] = kmeans.fit_predict(embeddings)

# Show clusters
for cluster_id in sorted(df["cluster"].unique()):
    cluster_df = df[df["cluster"] == cluster_id]
    texts = (cluster_df["title"] + ". " + cluster_df["snippet"]).tolist()
    summary = summarize_cluster(texts)

    with st.expander(f"🧠 {summary} ({len(cluster_df)} articles)"):
        for _, row in cluster_df.iterrows():
            st.markdown(f"- [{row['title']}]({row['link']}) — *{row['source']}*")
