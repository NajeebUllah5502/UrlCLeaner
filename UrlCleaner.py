import streamlit as st
import re
from urllib.parse import urlparse

# Normalize and extract clean domain from URL
def extract_domain(url):
    if not url.strip():
        return None
    parsed = urlparse(url.strip().lower())
    netloc = parsed.netloc if parsed.netloc else parsed.path
    netloc = re.sub(r'^www\.', '', netloc)  # remove www.
    return netloc.strip()

# Read all lines from uploaded file and clean them
def load_file_lines(file):
    return [line.strip() for line in file if line.strip()]

def domain_in_url(url, domain_list):
    """
    Checks if any domain from domain_list is present in the URL as a full domain or subdomain.
    """
    url_domain = extract_domain(url)
    return any(url_domain.endswith(blocked) for blocked in domain_list)

def main():
    st.title("🔍 URL Filter App — Remove URLs Based on Domains")

    st.markdown("""
    Upload two `.txt` files:
    - **File 1**: A list of URLs (one per line)
    - **File 2**: A list of domains or full URLs to block (they will be normalized)
    """)

    url_file = st.file_uploader("📄 Upload Main URL List (to be filtered)", type=["txt"])
    block_file = st.file_uploader("🚫 Upload Blocklist File (URLs or domains)", type=["txt"])

    if url_file and block_file:
        urls = load_file_lines(url_file)
        raw_blocklist = load_file_lines(block_file)

        # Normalize blocklist to domains
        blocklist_domains = {extract_domain(url) for url in raw_blocklist if extract_domain(url)}
        st.write(f"🧱 Total URLs in main file: **{len(urls)}**")
        st.write(f"🚫 Domains to block: **{len(blocklist_domains)}**")

        # Filter URLs
        filtered_urls = [url for url in urls if not domain_in_url(url, blocklist_domains)]
        st.success(f"✅ Remaining URLs after filtering: {len(filtered_urls)}")

        # Show a sample
        st.text_area("📋 Sample of Cleaned URLs", "\n".join(filtered_urls[:20]), height=200)

        # Download button
        if filtered_urls:
            st.download_button(
                label="📥 Download Filtered URL List",
                data="\n".join(filtered_urls),
                file_name="cleaned_urls.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
