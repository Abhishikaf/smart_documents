

import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import hashlib
import pandas as pd

from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json
from crypto_funcs import encrypt_data, decrypt_data

load_dotenv()

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

st.set_page_config(
    layout="wide",
)

################################################################################
# Contract Helper function:
# 1. Loads the contract once using cache
# 2. Connects to the contract using the contract address and ABI
################################################################################


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

# Function to calculate the SHA256 hash of a document

def calculate_file_hash(file):
    sha256_hash = hashlib.sha256()
    bytes_data = file.getvalue()
    sha256_hash.update(bytes_data)  
    doc_hash = sha256_hash.hexdigest()
    return doc_hash


# Function to get account history

def get_files_to_notarize(pending_file_container):

    pending_file_container.empty()
    pendingFiles = contract.functions.getPendingFiles().call()
    with pending_file_container.container():
        if pendingFiles:
            df = pd.DataFrame(pendingFiles).T
            df.columns = ['Document Hash', 'Owner Wallet Address']
            st.table(df)

        else:
            st.write("No files pending notarization")





def get_account_history(address, account_history):
    
    account_history.empty()
    document_filter = contract.events.DocumentCreated.createFilter(fromBlock="0x0", argument_filters={"docOwner": address})
    reports = document_filter.get_all_entries()

    with account_history.container():
        if reports:
            for report in reports:
                report_dictionary = dict(report)
                html_str = f"""<p style = "line-height:50%; font-size:14px"><b> Document hash </b></p>"""
                st.markdown(html_str, unsafe_allow_html=True)
                st.markdown(f"""<p style = "line-height:50%; font-size:12px">{report_dictionary['args']['fileHash']}</p>""",
                                        unsafe_allow_html=True)
                status = contract.functions.getDocState(report_dictionary['args']['fileHash']).call()
                if status == 0:
                    file_status = "Not Notarized"
                elif status == 1:
                    file_status = "Pending Notarization "
                elif status == 2:
                    file_status = "Notarized"
                         
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""<p style = "line-height:50%; font-size:12px"><b> File name :</b></p>""",
                                        unsafe_allow_html=True ) 
                    st.markdown(f"""<p style = "line-height:50%; font-size:12px"><b> File Desc :</b></p>""",
                                        unsafe_allow_html=True ) 
                    st.markdown(f"""<p style = "line-height:50%; font-size:12px"><b> Status :</b></p>""",
                                        unsafe_allow_html=True ) 
                
                with col2:
                    st.markdown(f"""<p style = "line-height:50%; font-size:12px">{report_dictionary['args']['fileName']}</p>""",
                                        unsafe_allow_html=True ) 
                    st.markdown(f"""<p style = "line-height:50%; font-size:12px">{report_dictionary['args']['docType']}</p>""",
                                        unsafe_allow_html=True ) 
                    st.markdown(f"""<p style = "line-height:50%; font-size:12px">{file_status}</p>""",
                                        unsafe_allow_html=True ) 
                
                st.markdown(f"""<p style = "line-height:50%; font-size:12px">---</p>""",unsafe_allow_html=True)
        
        else:
            st.write("This account has not uploaded any documents")


################################################################################
# Helper functions to pin files and json to Pinata
################################################################################


def pin_file(file_name, file, password=""):
    token_json = {}
    if password:
        st.write("pin_file(): Encrypting file")
        file_data = encrypt_data(file.getvalue(), password)
        token_json["encrypted"] = True
        # Clear password
        password = ""
    else:
        st.write("pin_file(): NOT encrypting file")
        file_data = file.getvalue()

    # Abhishikas hash function
    # data_hash = get_hash(file_data)
    data_hash = 0x1234
    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(file_data)

    # Build a token metadata file for the artwork
    token_json["file_name"] = file_name
    token_json["file_hash"] = ipfs_file_hash
    token_json["file_data_hash"] = data_hash
     
    json_data = convert_data_to_json(token_json)

    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    return json_ipfs_hash


##########
## MAIN ##
##########

# st.title("ALGORITHMIC, MACHINE LEARNING, AND NEURAL TRADING TOOLS WITH ESG SENTIMENT FOCUS")
# Had to use literal path here. Objected to Path('images/Title.jpg')

st.image('images/Title.jpg', use_column_width='auto')

st.sidebar.title("Select a page")

page = st.sidebar.radio('', options=['Client Register and File Selection', 'Notary Signature', 'Verification'], key='1')

st.sidebar.markdown("""---""")

accounts = w3.eth.accounts



if page == 'Client Register and File Selection':
    
    
    doEncrypt=False

    st.markdown("## Register Client and Select File")
    st.write("Choose an account to get started")
    
    address = st.selectbox("Select Account", options=accounts[0:8])
    st.markdown("---")

    st.sidebar.markdown("### Client Wallet Address:")
    st.sidebar.markdown(f"""<p style = "line-height:50%; font-size:14px">{address}</p>""",unsafe_allow_html=True)
    st.sidebar.markdown("### Account History")

    account_history = st.sidebar.empty()
    get_account_history(address, account_history)

    doc_type = st.text_input("Enter the type of the document to be uploaded")
    st.write(" Document Type:", doc_type)
    st.session_state.doc_type = doc_type

    st.write("Select a file to be uploaded:")
    file = st.file_uploader("Add file")
    st.session_state.file = file
    password = ""
    st.session_state.password = password
    
    if file:
        st.write("Optional before IPFS upload:")

        doEncrypt = st.checkbox("Encrypt " + file.name )
        if doEncrypt:
            password = st.text_input("Enter password:")
            if password:
                st.write("Encrypt with password:", password)
                st.session_state.password = password

        doNotarize = st.checkbox("Notarize " + file.name )
                
        if st.button("Submit"):   
            doc_hash = calculate_file_hash(file)
            st.session_state.doc_hash = doc_hash
            if(not doNotarize):
                file_ipfs_hash = pin_file(
                    st.session_state.file.name,
                    st.session_state.file,
                    password
                )
            else:
                file_ipfs_hash = ""  
            try:
                tx_hash = contract.functions.createDoc(file.name, doc_type, 
                                                    address, doc_hash,
                                                    file_ipfs_hash, doEncrypt, doNotarize
                                                    ).transact({'from': address, 'gas': 1000000})
                receipt = w3.eth.waitForTransactionReceipt(tx_hash)
                st.write("Transaction receipt mined:")            
            except:
                 st.write("File is alreay saved on the blockchain!")
    

    get_account_history(address, account_history)



if page == 'Notary Signature':
    st.title("Notarize File")

    st.markdown("### Files Pending Notarization")

    pending_file_container = st.empty()

    get_files_to_notarize(pending_file_container)


    notary = st.selectbox("Select Notary Address", options = accounts[8:10])
    license = st.text_input("Notary License Number")
    doc_hash = st.text_input("Document Hash")
    address = st.text_input("Owner address")
    if(st.button("Notarize")):
        st.write(notary, license,doc_hash, address)
        try:
            tx_hash = contract.functions.notarizeDoc(notary, license, doc_hash     
                                                ).transact({'from': address, 'gas': 1000000})
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            st.write("Transaction receipt mined:")            
        except:
            st.write("File is not pending notarization")

    get_files_to_notarize(pending_file_container)

    # st.markdown("## Files Notarized")
    # st.write("Notary chosen:", st.session_state.notary)
    # st.write("Client email:", st.session_state.client)
    # st.write("File name:", st.session_state.file.name)
    # if 'password' in st.session_state:
    #     st.write("Do encrypt:", st.session_state.password)
    #     password = st.session_state.password
    # else:
    #     password = ""

    # if st.button("Confirm and notarize"):
    #     file_ipfs_hash = pin_file(
    #         st.session_state.file.name,
    #         st.session_state.file,
    #         st.session_state.notary,
    #         password
    #         )

    #     # If we want to display link to file itself, we need pin_file() to return ipfs_file_hash
    #     #   Otherwise, that ipfs_file_hash can be read from the metadata
    #     st.write("IPFS Gateway Link to notarized file metadata:")
    #     st.markdown(f"[Pinned metadata for notarized file](https://ipfs.io/ipfs/{file_ipfs_hash})")
        # contract.functions.notarizeFile(...)

# if page == 'Verification':
#     st.title("Verify Authenticity")

