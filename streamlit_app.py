

import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import hashlib
import sqlite3

from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json
from crypto_funcs import encrypt_data, decrypt_data
from login_funcs import sign_up, sign_in

load_dotenv()

conn=sqlite3.connect("data.db")

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

def get_account_history(address):
    st.markdown("## Account history")
    document_filter = contract.events.DocumentCreated.createFilter(fromBlock="0x0", argument_filters={"docOwner": address})
    reports = document_filter.get_all_entries()

    if reports:
        for report in reports:
            report_dictionary = dict(report)
            st.write(report_dictionary['args']['fileHash'])
            st.write(report_dictionary['args']['fileName'])
            st.write(report_dictionary['args']['docType'])
            st.write(report_dictionary['args']['status'] )
        
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

# Be able to change page_options according to Login status
USER = 0
NOTARY = 1
THIRD_PARTY = 2
login_status = [ [],  [],  [] ]
if 'page_options' not in st.session_state:
    st.session_state.page_options = ['Client Login', 'Notary Login', 'Verification: Login']
    st.session_state.page_index = USER

st.image('images/Title.jpg', use_column_width='auto')

st.sidebar.title("Select a page")

#page = st.sidebar.selectbox('', options=['Client Register and File Selection', 'Notary Signature', 'Verification'], key='1')
page = st.sidebar.selectbox('', options=st.session_state.page_options, index=st.session_state.page_index )

st.sidebar.markdown("""---""")

if 'login_status' not in st.session_state:
    st.session_state.login_status = login_status

if page == 'Client Login':
    userType = "User"
    menu=["Sign Up","Sign In"]
    choice=st.selectbox("Menu",menu)
    if choice == "Sign Up":
        sign_up(conn, userType)
    elif choice == "Sign In":
        st.session_state.login_status[USER] = sign_in(conn, userType)
        if st.session_state.login_status[USER]:
            st.session_state.page_options[USER] = 'Client Register and File Selection'
            st.experimental_rerun()



if page == 'Client Register and File Selection':
    doEncrypt=False
    st.markdown("## Register Client and Select File")
    st.write("Choose an account to get started")
    accounts = w3.eth.accounts
    address = st.selectbox("Select Account", options=accounts)
    st.session_state.address = address
    st.markdown("---")

    # email_addr = st.text_input("Please register with email address:")
    # st.write("Email entered:", email_addr)
#    registered = contract.functions.newClient(email_addr)
    # Save for use on other pages
    # st.session_state.client = email_addr

    
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
        # if doNotarize:
        #     notary = st.selectbox("Select a Notary:", notaries)
        #     st.session_state.notary = notary
        #     st.write("Selected:", notary)

        
        if st.button("Submit"):   
            doc_hash = calculate_file_hash(file)
            st.session_state.doc_hash = doc_hash
            file_ipfs_hash = pin_file(
                st.session_state.file.name,
                st.session_state.file,
                password
             )  
            try:
                tx_hash = contract.functions.createDoc(file.name, doc_type, 
                                                    address, doc_hash,
                                                    file_ipfs_hash, doEncrypt, doNotarize
                                                    ).transact({'from': address, 'gas': 1000000})
                receipt = w3.eth.waitForTransactionReceipt(tx_hash)
                st.write("Transaction receipt mined:")            
            except:
                st.write("File is alreay saved on the blockchain!")
    

#get_account_history(st.session_state.address)

if page == 'Notary Login':
    userType = "Notary"
    menu=["Sign Up","Sign In"]
    choice=st.selectbox("Menu",menu)
    if choice == "Sign Up":
        st.write("Choose an account to get started")
        accounts = w3.eth.accounts
        address = st.selectbox("Select Account", options=accounts)
        st.session_state.notary = address
        # address should be passed to sign_up and saved in add_data()
        sign_up(conn, userType)
    elif choice == "Sign In":
        st.session_state.login_status[NOTARY] = sign_in(conn, userType)
        if st.session_state.login_status[NOTARY]:
            st.session_state.page_options[NOTARY] = 'Notary Signature'
            st.session_state.page_index = NOTARY
            st.experimental_rerun()

if page == 'Notary Signature':
    userType = "Notary"
    st.title("Notarize File")
    #st.write("Notary chosen:", st.session_state.notary)
    # Unclear if we're going to ask for Email Address
    #st.write("Client email:", st.session_state.client)
    st.write("File name:", st.session_state.file.name)
    if 'password' in st.session_state:
        st.write("Do encrypt:", st.session_state.password)
        password = st.session_state.password
    else:
        password = ""

    if st.button("Confirm and notarize"):
        file_ipfs_hash = pin_file(
            st.session_state.file.name,
            st.session_state.file,
            #st.session_state.notary,
            password
            )

        # If we want to display link to file itself, we need pin_file() to return ipfs_file_hash
        #   Otherwise, that ipfs_file_hash can be read from the metadata
        st.write("IPFS Gateway Link to notarized file metadata:")
        st.markdown(f"[Pinned metadata for notarized file](https://ipfs.io/ipfs/{file_ipfs_hash})")
        # contract.functions.notarizeFile(...)

if page == 'Verification':
    userType = "thirdParty"
    st.title("Verify Authenticity")

