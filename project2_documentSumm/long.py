from transformers import pipeline, AutoTokenizer
import torch
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.cluster import KMeans
import nltk
from nltk.tokenize import sent_tokenize
from transformers.utils import logging
logging.set_verbosity_error()


# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading NLTK punkt tokenizer...")
    nltk.download('punkt')


class AdvancedDocumentSummarizer:
    def __init__(self, model_name="facebook/bart-large-cnn", debug=False):
        self.device = 0 if torch.cuda.is_available() else -1
        self.debug = debug

        if self.debug:
            print("Loading summarizer and tokenizer...")
        self.summarizer = pipeline('summarization', model=model_name, device=self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        if self.debug:
            print("Loading sentence embedding model...")
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

    def method1_hierarchical_summarization(self, document, target_length=200):
        if self.debug:
            print("\n🔄 Using Hierarchical Summarization...")

        sections = [p.strip() for p in document.split('\n\n') if p.strip()]
        if len(sections) <= 2:
            return self._direct_summarize(document, target_length)

        section_summaries = []
        for i, section in enumerate(sections):
            if len(section.split()) > 50:
                try:
                    max_len = min(100, max(30, len(section.split()) // 3))
                    min_len = min(15, max_len - 5)
                    summary = self.summarizer(section, max_length=max_len, min_length=min_len, do_sample=False)[0]['summary_text']
                    section_summaries.append(summary)
                except Exception as e:
                    if self.debug:
                        print(f"Warning: Could not summarize section {i+1}: {e}")
                    words = section.split()
                    section_summaries.append(' '.join(words[:50]) + "..." if len(words) > 50 else section)

        combined = self._add_transitions(section_summaries)
        if len(combined.split()) > target_length:
            return self._direct_summarize(combined, target_length)
        return combined

    def method2_extractive_then_abstractive(self, document, target_length=200):
        if self.debug:
            print("\n🔄 Using Extractive + Abstractive Summarization...")

        sentences = sent_tokenize(document)
        if len(sentences) <= 5:
            return self._direct_summarize(document, target_length)

        sentence_embeddings = self.sentence_model.encode(sentences)
        doc_embedding = np.mean(sentence_embeddings, axis=0)

        similarities = [np.dot(emb, doc_embedding) / (np.linalg.norm(emb) * np.linalg.norm(doc_embedding)) for emb in sentence_embeddings]
        position_weights = [1.0 - (i / len(sentences)) * 0.3 for i in range(len(sentences))]
        combined_scores = [sim * pos for sim, pos in zip(similarities, position_weights)]

        top_indices = sorted(range(len(combined_scores)), key=lambda i: combined_scores[i], reverse=True)[:min(len(sentences) // 2, 8)]
        top_indices.sort()
        key_sentences = [sentences[i] for i in top_indices]

        return self._direct_summarize(' '.join(key_sentences), target_length)

    def method3_topic_aware_summarization(self, document, target_length=200):
        if self.debug:
            print("\n🔄 Using Topic-Aware Summarization...")

        sentences = sent_tokenize(document)
        if len(sentences) <= 6:
            return self._direct_summarize(document, target_length)

        sentence_embeddings = self.sentence_model.encode(sentences)
        n_clusters = min(max(2, len(sentences) // 4), 4)

        try:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(sentence_embeddings)
        except:
            return self.method1_hierarchical_summarization(document, target_length)

        cluster_sentences = {i: [] for i in range(n_clusters)}
        sentence_order = []
        for idx, (sent, cluster) in enumerate(zip(sentences, clusters)):
            cluster_sentences[cluster].append(sent)
            sentence_order.append((idx, cluster))

        cluster_summaries = []
        for cluster_id in range(n_clusters):
            cluster_text = ' '.join(cluster_sentences[cluster_id])
            if len(cluster_text.split()) > 30:
                try:
                    max_len = min(80, max(25, len(cluster_text.split()) // 2))
                    min_len = min(10, max_len - 5)
                    summary = self.summarizer(cluster_text, max_length=max_len, min_length=min_len, do_sample=False)[0]['summary_text']
                    cluster_summaries.append((cluster_id, summary))
                except Exception as e:
                    if self.debug:
                        print(f"Warning: Could not summarize cluster {cluster_id}: {e}")
                    words = cluster_text.split()
                    fallback = ' '.join(words[:30]) + "..." if len(words) > 30 else cluster_text
                    cluster_summaries.append((cluster_id, fallback))

        cluster_first_appearance = {}
        for idx, cluster in sentence_order:
            if cluster not in cluster_first_appearance:
                cluster_first_appearance[cluster] = idx

        sorted_clusters = sorted(cluster_first_appearance.items(), key=lambda x: x[1])
        ordered_summaries = [summary for cid, _ in sorted_clusters for cid2, summary in cluster_summaries if cid == cid2]

        combined = self._add_transitions(ordered_summaries)
        return self._direct_summarize(combined, target_length) if len(combined.split()) > target_length else combined

    def _direct_summarize(self, text, target_length):
        return self.summarizer(text, max_length=target_length, min_length=target_length // 2, do_sample=False)[0]['summary_text']

    def _add_transitions(self, summaries):
        if len(summaries) <= 1:
            return ' '.join(summaries)
        transitions = ["Additionally,", "Furthermore,", "Subsequently,", "Moreover,", "Later,"]
        result = [summaries[0]]
        for i, summary in enumerate(summaries[1:], 1):
            if not any(summary.startswith(word) for word in ["After", "During", "In", "When", "Following"]):
                if i - 1 < len(transitions):
                    result.append(f"{transitions[i-1]} {summary}")
                else:
                    result.append(summary)
            else:
                result.append(summary)
        return ' '.join(result)


# Example usage and comparison
def compare_summarization_methods():
    # Sample long document about Steve Jobs
    document = """
    Steven Paul Jobs was born on February 24, 1955, in San Francisco, California. He was adopted by Paul and Clara Jobs, who raised him in Mountain View, California, in the heart of what would later become known as Silicon Valley. From an early age, Jobs showed an interest in electronics and craftsmanship, often working with his adoptive father in the garage.

    In 1976, at the age of 21, Jobs co-founded Apple Computer Company with his friend Steve Wozniak in the famous garage of his childhood home. Their first product, the Apple I, was a revolutionary personal computer that helped launch the personal computer revolution. The success of the Apple II in 1977 made Apple one of the fastest-growing companies in history and established Jobs as a visionary leader in the technology industry.

    However, in 1985, following internal power struggles and disagreements with the board of directors, Jobs was forced to resign from Apple, the company he had co-founded. This setback, rather than defeating him, spurred him to new heights of innovation. He founded NeXT Computer, a company focused on high-end workstations for business and educational markets. Although NeXT never achieved mainstream commercial success, its advanced operating system and development tools would later prove crucial to Apple's future.

    During this period, Jobs also acquired the computer graphics division of Lucasfilm for $10 million, transforming it into Pixar Animation Studios. Under his leadership, Pixar revolutionized the animation industry with groundbreaking computer-animated films. The release of "Toy Story" in 1995, the first fully computer-animated feature film, was a massive success and established Pixar as a major force in Hollywood.

    In 1997, Apple acquired NeXT for $429 million, bringing Jobs back to the company he had co-founded. Apple was struggling at the time, nearly bankrupt and losing market share to competitors. Jobs' return marked the beginning of one of the most remarkable corporate turnarounds in business history. He streamlined Apple's product line, focusing on a few key products with exceptional design and user experience.

    The launch of the iMac in 1998 signaled Apple's resurgence. Its innovative design and user-friendly interface helped restore the company's reputation for innovation. This was followed by a series of revolutionary products that transformed entire industries: the iPod in 2001 revolutionized the music industry, the iPhone in 2007 redefined the smartphone market, and the iPad in 2010 created the tablet computing category.

    Jobs was known for his perfectionist approach to product design and his demanding leadership style. He believed in simplicity, elegance, and intuitive user interfaces. His famous attention to detail extended to every aspect of Apple's products, from the internal components that users would never see to the packaging design. His presentations, known as "stevenotes," became legendary events in the technology world.

    Unfortunately, Jobs' health began to decline in the 2000s. He was diagnosed with a rare form of pancreatic cancer in 2003 and underwent surgery in 2004. Despite his illness, he continued to lead Apple through some of its most successful years. He took medical leave several times but remained deeply involved in the company's strategic decisions and product development.

    On October 5, 2011, Steve Jobs passed away at the age of 56, leaving behind a legacy that transformed multiple industries. His influence extended far beyond technology, affecting design, retail, entertainment, and corporate culture. Today, Apple continues to be one of the world's most valuable companies, and Jobs is remembered as one of the greatest innovators and entrepreneurs of the modern era.
    """
    
    # Initialize summarizer
    summarizer = AdvancedDocumentSummarizer()
    
    print("=" * 80)
    print("COMPARING DIFFERENT SUMMARIZATION METHODS")
    print("=" * 80)
    
    # Method 1: Hierarchical
    print("\n📋 METHOD 1: HIERARCHICAL SUMMARIZATION")
    print("-" * 50)
    summary1 = summarizer.method1_hierarchical_summarization(document, target_length=200)
    print(summary1)
    
    # Method 2: Extractive + Abstractive
    print("\n📋 METHOD 2: EXTRACTIVE + ABSTRACTIVE")
    print("-" * 50)
    summary2 = summarizer.method2_extractive_then_abstractive(document, target_length=150)
    print(summary2)
    
    # Method 3: Topic-Aware
    print("\n📋 METHOD 3: TOPIC-AWARE SUMMARIZATION")
    print("-" * 50)
    summary3 = summarizer.method3_topic_aware_summarization(document, target_length=150)
    print(summary3)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE - Choose the method that works best for your use case!")
    print("=" * 80)

if __name__ == "__main__":
    compare_summarization_methods()

# from transformers import pipeline, BartTokenizer
# import textwrap

# import torch

# # device=0 if torch.cuda.is_available() else -1

# def summarize_long_document(document, max_chunk_size=1000, overlap=100):
#     # Split into chunks with some overlap
#     chunks = textwrap.wrap(document, max_chunk_size, break_long_words=False)
    
#     # Ensure overlap between chunks
#     overlapped_chunks = []
#     for i, chunk in enumerate(chunks):
#         if i > 0:
#             # Add some text from the previous chunk
#             start = max(0, len(chunks[i-1]) - overlap)
#             chunk = chunks[i-1][start:] + chunk
#         overlapped_chunks.append(chunk)
    
#     # Initialize summarizer
#     summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=0 if torch.cuda.is_available() else -1)
    
#     # Summarize each chunk
#     summaries = [summarizer(chunk, max_length=150, min_length=40)[0]['summary_text'] for chunk in overlapped_chunks]
    
#     # Combine the summaries
#     combined_summary = " ".join(summaries)
    
#     # If the combined summary is still long, summarize it again
#     if len(combined_summary.split()) > 250:
#         combined_summary = summarizer(combined_summary, max_length=150, min_length=40)[0]['summary_text']

#     return combined_summary

# text = '''
# Steve Jobs (1955-2011) was an American entrepreneur, inventor, and business magnate best known as the co-founder, chairman, and CEO of Apple Inc. Jobs is widely recognized as a pioneer of the personal computer revolution of the 1970s and 1980s, along with Apple co-founder Steve Wozniak. Born in San Francisco and raised in the San Francisco Bay Area, Jobs dropped out of Reed College in 1972 and traveled through India in 1974 seeking enlightenment before co-founding Apple in 1976 to sell Wozniak's Apple I personal computer. Together, the duo gained fame and wealth a year later with the Apple II, one of the first highly successful mass-produced microcomputers.

# In the early 1980s, Jobs saw the commercial potential of the Xerox Alto, a computer with a graphical user interface (GUI) and mouse, which led to the development of the Macintosh. Launched in 1984, the Macintosh was the first mass-market personal computer to feature an integral GUI and mouse. However, following a power struggle with the board of directors in 1985, Jobs was forced out of Apple. He founded NeXT, a computer platform development company targeting higher-education and business markets. He also acquired the computer graphics division of Lucasfilm, which was spun off as Pixar. Jobs served as CEO and majority shareholder of Pixar, which produced the first fully computer-animated film, Toy Story (1995), and became a major animation studio that produced multiple box-office hits.

# Apple bought NeXT in 1997, and Jobs returned to the company he co-founded. He was largely responsible for revitalizing Apple, leading to the development of the iMac, iTunes, iPod, iPhone, and iPad, and transforming Apple into one of the world’s most valuable companies. Jobs’ vision and innovation are credited with reshaping entire industries — from personal computing and animated movies to music, phones, tablet computing, and digital publishing. His leadership style, product intuition, and perfectionism made him a controversial but revered figure in business and tech.

# In 2003, Jobs was diagnosed with a rare form of pancreatic cancer. He initially resisted conventional medical treatment and attempted alternative therapies, which delayed surgery and may have worsened his condition. Despite his illness, Jobs remained involved in Apple’s product strategy and public launches until he resigned as CEO in August 2011, succeeded by Tim Cook. Jobs died on October 5, 2011, at the age of 56.

# Jobs was posthumously awarded the Presidential Medal of Freedom in 2022. He has been memorialized in books, films, and museums, and his influence continues to shape modern computing and consumer technology.
# '''
# print(summarize_long_document(text))