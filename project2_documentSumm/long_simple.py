from transformers import pipeline, AutoTokenizer
import torch
import re

class SimpleRobustSummarizer:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        self.device = 0 if torch.cuda.is_available() else -1
        self.summarizer = pipeline('summarization', model=model_name, device=self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_input_length = 1024  # BART's max input length
        
    def smart_chunk_summarization(self, document, target_length=200):
        """
        Improved chunking that maintains context and narrative flow
        """
        # Clean the document
        document = self._clean_text(document)
        
        # Check if document is short enough for direct summarization
        word_count = len(document.split())
        if word_count <= 400:
            return self._safe_summarize(document, target_length)
        
        # Split into sentences for better boundary detection
        sentences = self._split_into_sentences(document)
        
        # Create overlapping chunks that respect sentence boundaries
        chunks = self._create_smart_chunks(sentences)
        
        if len(chunks) == 1:
            return self._safe_summarize(chunks[0], target_length)
        
        # Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}...")
            summary = self._safe_summarize(chunk, target_length // len(chunks) + 50)
            if summary:
                chunk_summaries.append(summary)
        
        # Combine summaries with improved transitions
        if not chunk_summaries:
            return "Could not generate summary."
        
        combined = self._combine_with_transitions(chunk_summaries)
        
        # Final pass if the combined summary is still too long
        if len(combined.split()) > target_length * 1.2:
            combined = self._safe_summarize(combined, target_length)
        
        return combined
    
    def _clean_text(self, text):
        """Clean and normalize text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove any special characters that might cause issues
        text = re.sub(r'[^\w\s.,!?;:()-]', '', text)
        return text
    
    def _split_into_sentences(self, text):
        """Simple sentence splitting that works without NLTK"""
        # Split on sentence endings, but be careful with abbreviations
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Clean up sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Filter out very short fragments
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _create_smart_chunks(self, sentences):
        """Create chunks that respect sentence boundaries and maintain context"""
        chunks = []
        current_chunk = []
        current_length = 0
        target_chunk_size = 300  # words per chunk
        overlap_sentences = 2  # sentences to overlap between chunks
        
        for i, sentence in enumerate(sentences):
            sentence_length = len(sentence.split())
            
            # If adding this sentence would exceed our target, start a new chunk
            if current_length + sentence_length > target_chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append(chunk_text)
                
                # Start new chunk with overlap from previous chunk
                if len(current_chunk) > overlap_sentences:
                    current_chunk = current_chunk[-overlap_sentences:]
                    current_length = sum(len(s.split()) for s in current_chunk)
                else:
                    current_chunk = []
                    current_length = 0
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        # Add the last chunk if it has content
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(chunk_text)
        
        return chunks
    
    def _safe_summarize(self, text, target_length):
        """Safely summarize text with proper error handling"""
        if not text or not text.strip():
            return ""
        
        word_count = len(text.split())
        
        # If text is already shorter than target, return as-is
        if word_count <= target_length:
            return text
        
        try:
            # Calculate safe min/max lengths
            max_length = min(target_length, max(20, word_count // 2))
            min_length = min(10, max_length - 5)
            
            # Ensure min_length is less than max_length
            if min_length >= max_length:
                min_length = max(1, max_length - 5)
            
            result = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                clean_up_tokenization_spaces=True
            )
            
            return result[0]['summary_text']
        
        except Exception as e:
            print(f"Summarization error: {e}")
            # Fallback: return first portion of text
            words = text.split()
            fallback_length = min(target_length, len(words))
            return ' '.join(words[:fallback_length]) + ("..." if len(words) > target_length else "")
    
    def _combine_with_transitions(self, summaries):
        """Combine summaries with natural transitions"""
        if len(summaries) <= 1:
            return ' '.join(summaries)
        
        result = [summaries[0]]
        
        for i, summary in enumerate(summaries[1:]):
            # Add transition words for better flow
            transitions = {
                1: "Subsequently,",
                2: "Additionally,", 
                3: "Furthermore,",
                4: "Moreover,",
                5: "Later,"
            }
            
            # Check if summary already starts with a transition word
            starts_with_transition = any(summary.startswith(word) for word in 
                                       ["After", "During", "In", "When", "Following", 
                                        "Subsequently", "Additionally", "Furthermore", 
                                        "Moreover", "Later", "Meanwhile", "However"])
            
            if not starts_with_transition and (i + 1) in transitions:
                # Make first letter lowercase and add transition
                summary = summary[0].lower() + summary[1:] if len(summary) > 1 else summary.lower()
                summary = f"{transitions[i + 1]} {summary}"
            
            result.append(summary)
        
        return ' '.join(result)

def test_summarizer():
    """Test the summarizer with the Steve Jobs example"""
    
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
    
    print("=" * 80)
    print("TESTING ROBUST DOCUMENT SUMMARIZER")
    print("=" * 80)
    
    summarizer = SimpleRobustSummarizer()
    
    print(f"Original document: {len(document.split())} words")
    print("\nGenerating summary...")
    print("-" * 50)
    
    summary = summarizer.smart_chunk_summarization(document, target_length=150)
    
    print("\n📋 FINAL SUMMARY:")
    print("-" * 30)
    print(summary)
    print(f"\nSummary length: {len(summary.split())} words")
    
    print("\n" + "=" * 80)
    print("DONE!")
    print("=" * 80)

if __name__ == "__main__":
    test_summarizer()