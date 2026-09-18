import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import io

# Set page layout and title
st.set_page_config(page_title="Price Scraper Tool", layout="wide")

st.title("🏷️ Price Scraper & Matcher Tool")
st.write("I-paste ang iyong mga Reference Code/Product Names at ang Website URL para kunin ang mga presyo.")

# --- INPUT SECTION (MGA BOX SA IBABAW) ---
col1, col2 = st.columns(2)

with col1:
    # Box 1: Paste option para sa Multiple References
    references_input = st.text_area(
        "1. I-paste ang mga Reference (Kada linya ay isang reference):",
        height=180,
        placeholder="Halimbawa:\nREF-001\nREF-002\niPhone 13\nSamsung S21"
    )

with col2:
    # Box 2: Website URL na kukunan ng detalye
    url_input = st.text_input(
        "2. Ilagay ang Website URL na iko-scrape:",
        placeholder="https://example-store.com/products"
    )
    
    st.info("💡 Note: Ang scraper na ito ay naghahanap ng mga karaniwang HTML elements para sa mga produkto at presyo.")

# Function para mag-convert ng DataFrame papuntang Excel bytes
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Price Results')
    return output.getvalue()

# --- SCRAPING PROCESS ---
if st.button("🚀 Simulan ang Scraping", type="primary"):
    if not references_input.strip():
        st.warning("Paki-lagay ang kahit isang Reference sa unang box.")
    elif not url_input.strip():
        st.warning("Paki-lagay ang Website URL sa ikalawang box.")
    else:
        # Kunin ang listahan ng references mula sa text area (hiwalay kada linya)
        ref_list = [line.strip() for line in references_input.split('\n') if line.strip()]
        
        st.write(f"🔍 **Naghahanap para sa {len(ref_list)} reference(s)...**")
        
        try:
            # Mag-send ng request sa Website
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url_input, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # HALIMBAWA NG GENERIC SCRAPING LOGIC
                # Inihahanap nito ang mga karaniwang tags kung saan nakalagay ang presyo
                results = []
                
                # Kukunin ang buong text ng page para sa simpleng paghahanap
                page_text = soup.get_text()
                
                for ref in ref_list:
                    # Dito ilalagay ang logic ng paghahanap
                    # Note: Sa totoong buhay, depende sa HTML structure ng target website ang pagsulat ng selector.
                    matched = False
                    
                    # Halimbawang simpleng pag-check kung nahanap ang reference sa page:
                    if ref.lower() in page_text.lower():
                        status = "Found on Page"
                        # Subukang maghanap ng katabing price pattern ($ o ₱)
                        price = "Kailangan ng custom selector para sa site na ito"
                    else:
                        status = "Not Found"
                        price = "N/A"
                        
                    results.append({
                        "Reference Input": ref,
                        "Status": status,
                        "Found Price / Info": price,
                        "Source URL": url_input
                    })
                
                # Gawan ng DataFrame
                df = pd.DataFrame(results)
                
                # --- RESULT SECTION (SA IBABA) ---
                st.subheader("📊 Resulta ng Scraping")
                st.dataframe(df, use_container_width=True)
                
                # --- DOWNLOAD OPTION ---
                excel_data = convert_df_to_excel(df)
                st.download_button(
                    label="📥 Download Result in Excel (.xlsx)",
                    data=excel_data,
                    file_name="scraped_prices.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
            else:
                st.error(f"Hindi ma-access ang website. HTTP Status Code: {response.status_code}")
                
        except Exception as e:
            st.error(f"Nagkaroon ng error sa pag-scrape: {e}")