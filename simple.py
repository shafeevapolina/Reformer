import streamlit as st
import sys

st.set_page_config(page_title="Simple Test")
st.title("Simple Test App")
st.write("Python version:", sys.version)
st.write("If you see this, Streamlit is working!")
