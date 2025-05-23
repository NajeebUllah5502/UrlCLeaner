import streamlit as st
import re
from urllib.parse import urlparse


# ---------- Helper Functions ----------

def extract_domain(url):
    """
    Normalize a URL or domain by removing protocol and www., and extracting the domain part.
    """
    if not url.strip():
        return None
    parsed = urlparse(url.strip().lower())
    netloc = parsed.netloc if parsed.netloc else parsed.path
    # Remove www and subdomains (e.g., restaurants.subway.com -> subway.com)
    netloc = re.sub(r'^www\.', '', netloc)
    domain_parts = netloc.split('.')
    
    # We remove subdomains (e.g., "restaurants" from "restaurants.subway.com")
    if len(domain_parts) > 2:
        netloc = '.'.join(domain_parts[-2:])  # Get the last two parts (subdomain removal)
    
    return netloc.strip()


def load_file_lines(file):
    """
    Load and decode a text file with support for utf-8, utf-16, and cp1252.
    """
    try:
        content = file.getvalue().decode("utf-8")
    except UnicodeDecodeError:
        try:
            content = file.getvalue().decode("utf-16")
        except UnicodeDecodeError:
            content = file.getvalue().decode("cp1252")
    return [line.strip() for line in content.splitlines() if line.strip()]


def domain_in_url(url, domain_list):
    """
    Check if any domain in domain_list matches the end of the URL domain.
    """
    url_domain = extract_domain(url)
    return any(url_domain.endswith(blocked) for blocked in domain_list)


# ---------- Streamlit App ----------

def main():
    st.title("🧹 URL Filter App — Remove URLs by Domain Match")

    st.markdown(""" 
    Upload two `.txt` files:
    - 📄 **File 1**: List of URLs to be filtered.
    - 🚫 **File 2**: Blocklist of domains or full URLs.

    The app removes any URL from File 1 that matches or ends with any normalized domain in File 2.
    """)

    url_file = st.file_uploader("📄 Upload Main URL List (File 1)", type=["txt"])
    block_file = st.file_uploader("🚫 Upload Blocklist File (File 2)", type=["txt"])

    if url_file and block_file:
        urls = load_file_lines(url_file)
        raw_blocklist = load_file_lines(block_file)

        # Extract the domain from each blocklist URL
        blocklist_domains = {extract_domain(url) for url in raw_blocklist if extract_domain(url)}

        st.write(f"🔢 Total URLs in File 1: **{len(urls)}**")
        st.write(f"🛑 Total blocklist domains: **{len(blocklist_domains)}**")

        # Filter
        kept_urls = []
        removed_urls = []

        for url in urls:
            if domain_in_url(url, blocklist_domains):
                removed_urls.append(url)
            else:
                kept_urls.append(url)

        st.success(f"✅ URLs after filtering: **{len(kept_urls)}**")
        st.error(f"❌ URLs removed: **{len(removed_urls)}**")

        # Previews
        st.subheader("✅ Kept URLs (Sample)")
        st.text_area("Kept URLs", "\n".join(kept_urls[:20]), height=200)

        st.subheader("❌ Removed URLs (Sample)")
        st.text_area("Removed URLs", "\n".join(removed_urls[:20]), height=200)

        # Downloads
        if kept_urls:
            st.download_button(
                label="📥 Download Cleaned URLs (Kept)",
                data="\n".join(kept_urls),
                file_name="cleaned_urls.txt",
                mime="text/plain"
            )
        if removed_urls:
            st.download_button(
                label="📥 Download Removed URLs",
                data="\n".join(removed_urls),
                file_name="removed_urls.txt",
                mime="text/plain"
            )


if __name__ == "__main__":
    main()
