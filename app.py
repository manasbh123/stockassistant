import streamlit as st
import openai
import yfinance as yf
import pandas as pd

openai.api_key = "sk-xxxxxxxxxxxxxxxxxxxxxx"  # Replace with your OpenAI API key

st.set_page_config(page_title="Smart AI Stock Assistant", page_icon="📈", layout="wide")

st.title("📈 Smart AI Stock Assistant")

if "history" not in st.session_state:
    st.session_state.history = []

# User input area
user_input = st.text_input("Ask a finance question or enter a stock ticker (e.g., AAPL)")

if st.button("Send") and user_input:
    answer = ""
    stock_data = None
    stock_info_text = ""

    if user_input.isalpha() and len(user_input) <= 5:
        # It's a stock ticker, get stock info and history
        try:
            stock = yf.Ticker(user_input.upper())
            info = stock.info
            name = info.get("longName", "Unknown Company")
            price = info.get("regularMarketPrice", "N/A")
            sector = info.get("sector", "N/A")
            summary = info.get("longBusinessSummary", "No summary available.")

            stock_info_text = (
                f"**{name} ({user_input.upper()})**  \n"
                f"**Price:** ${price}  \n"
                f"**Sector:** {sector}  \n\n"
                f"{summary}"
            )

            stock_data = stock.history(period="1y")

        except Exception as e:
            answer = f"Error fetching data for {user_input.upper()}: {e}"

    else:
        # Ask OpenAI GPT
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful financial assistant."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=400,
                temperature=0.6,
            )
            answer = response.choices[0].message['content'].strip()
        except Exception as e:
            answer = f"OpenAI API Error: {e}"

    # Save to history
    st.session_state.history.append({"user": user_input, "bot": answer, "stock_info": stock_info_text, "stock_data": stock_data})

# Layout with two columns
col1, col2 = st.columns([3, 2])

with col1:
    st.header("Chat")
    if st.session_state.history:
        for chat in reversed(st.session_state.history):  # latest on top
            st.markdown(f"**You:** {chat['user']}")
            if chat['bot']:
                st.markdown(f"**AI:** {chat['bot']}")
            st.write("---")
    else:
        st.write("Start by asking a question or entering a stock ticker.")

with col2:
    st.header("Stock Info & Chart")
    if st.session_state.history:
        # Show the latest stock info and chart if available
        latest = st.session_state.history[-1]
        if latest["stock_info"]:
            st.markdown(latest["stock_info"])
        if latest["stock_data"] is not None and not latest["stock_data"].empty:
            st.line_chart(latest["stock_data"]["Close"])
    else:
        st.write("Stock information and charts will appear here.")

