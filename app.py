import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import time
import pandas as pd
import hashlib

load_dotenv()

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

@st.cache(allow_output_mutation=True)
def load_contract():

    # Load the contract ABI
    with open(Path('./contracts/compiled/smartdocuments_abi.json')) as f:
        contract_abi = json.load(f)

    # Set the contract address (this is the address of the deployed contract)
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=contract_abi
    )

    return contract


# Load the contract
contract = load_contract()


st.markdown("## Calculate Document Hash")

#st.write(dt.datetime.now())
doc_name = st.text_input("Enter the name of the document")
doc_hash = ""
sha256_hash = hashlib.sha256()
file = st.file_uploader("Upload Document")

if file is not None:
    st.write(file.name)

if st.button("Calculate Document Hash"):
    
    
    if file is not None:
        bytes_data = file.getvalue()
        sha256_hash.update(bytes_data)      
        doc_hash = sha256_hash.hexdigest()
        st.session_state.doc_hash = doc_hash
st.write(doc_hash)

st.markdown("---")

st.write("Choose an account to get started")
accounts = w3.eth.accounts
address = st.selectbox("Select Account", options=accounts)



if st.button("Save Document on Blockchain"):
    doc_hash = st.session_state.doc_hash
    try:
        tx_hash = contract.functions.createDoc(address, doc_hash).transact({'from': address, 'gas': 1000000})
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write("Transaction receipt mined:")
        st.write(dict(receipt))
    except:
        st.write("File is alreay saved on the blockchain!")
    
    
st.markdown("---")

st.markdown("## Account history")

if st.button("Get All Documents"):
    st.write(address)
    document_filter = contract.events.DocumentCreated.createFilter(fromBlock="0x0", argument_filters={"docOwner": address})
    reports = document_filter.get_all_entries()

    if reports:
        for report in reports:
            report_dictionary = dict(report)
            st.write(report_dictionary)
            st.markdown("### Document Log")
            st.write(report_dictionary['args']['fileHash'])
        
    else:
        st.write("This account has not uploaded any documents")


