import streamlit as st
import time
import pandas as pd
import hashlib

st.markdown("## Calculate Document Hash")

#st.write(dt.datetime.now())
doc_name = st.text_input("Enter the name of the document")
sha256_hash = hashlib.sha256()
file = st.file_uploader("Upload Document")

if file is not None:
    st.write(file.name)

if st.button("Calculate Document Hash"):
    
    
    if file is not None:
        bytes_data = file.getvalue()
        sha256_hash.update(bytes_data)
        sha256_hash.update(str(time.time()).encode())

    st.write(sha256_hash.hexdigest())
    
st.markdown("---")






