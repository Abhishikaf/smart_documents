

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
from login_funcs import sign_up, sign_in, check_user,see_users_df

load_dotenv()

conn=sqlite3.connect("data.db")

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))


st.sidebar.image("images/n1133825.png",width=90,output_format="auto")

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

def calculate_file_hash(bytes_data):
    sha256_hash = hashlib.sha256()
    #bytes_data = file.getvalue()
    sha256_hash.update(bytes_data)  
    doc_hash = sha256_hash.hexdigest()
    return doc_hash


def get_files_to_notarize():
    st.markdown("## Files pending notarization")
    document_filter = contract.events.DocumentCreated.createFilter(fromBlock="0x0", argument_filters={"status": 1})
    reports = document_filter.get_all_entries()

    if reports:
        for report in reports:
            report_dictionary = dict(report)
            st.write(report_dictionary['args']['fileHash'])
            st.write(report_dictionary['args']['docType'])
    else:
        st.write("No files pending notarization")

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


def pin_file(file_name, file_data, encrypted, doc_hash):
    token_json = {}

    st.sidebar.write("pin_file encrypted:", encrypted)

    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(file_data)

    # Build a token metadata file for the artwork
    token_json["file_name"] = file_name
    token_json["file_hash"] = ipfs_file_hash
    token_json["file_data_hash"] = doc_hash
    if encrypted:
        token_json["encrypted"] = True
     
    json_data = convert_data_to_json(token_json)

    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    # This doc_hash must be used because encryption may have happened here
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
    st.session_state.page_options = ['Client Login', 'Notary Login', 'Verification Login']
    st.session_state.page_index = USER

st.image('images/Title.jpg', use_column_width='always')

st.sidebar.subheader("Select a page")

page = st.sidebar.selectbox('', options=st.session_state.page_options, index=st.session_state.page_index )

st.sidebar.markdown("""---""")
if st.sidebar.checkbox("See all users"): 
    a=see_users_df()
    st.dataframe(a)

if 'login_status' not in st.session_state:
    st.session_state.login_status = login_status

if page == 'Client Login':
    userType = "User"
    # Even if user sign_in() fails, we want this index
    st.session_state.page_index = USER
    menu=["Sign In","Sign Up"]
    choice=st.selectbox("Menu",menu)
    if choice == "Sign Up":
        sign_up(conn, userType)
    elif choice == "Sign In":
        st.session_state.login_status[USER] = sign_in(conn, userType)
        if st.session_state.login_status[USER]:
            # Only one login can be active at a time
            st.session_state.login_status[NOTARY] = []
            st.session_state.login_status[THIRD_PARTY] = []
            st.session_state.page_options = ['Client File Selection', 'Notary Login', 'Verification Login']
            st.experimental_rerun()


if page == 'Client File Selection':
    doEncrypt=False
    st.markdown("## Select File")
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
    #st.write(" Document Type:", doc_type)
    st.session_state.doc_type = doc_type

    st.write("Select a file to be uploaded:")
    file = st.file_uploader("")
    st.session_state.file = file
    password = ""
    st.session_state.password = password
    
    if "doEncrypt" in st.session_state:
        st.sidebar.write("Client: state.doEncrypt:", st.session_state.doEncrypt)

    if file:
        st.write("Optional before IPFS upload:")

        doEncrypt = st.checkbox("Encrypt " + file.name )
        if doEncrypt:
            password = st.text_input("Enter password:",type="password")
            if password:
                st.session_state.password = password
                st.session_state.file_data = encrypt_data(file.getvalue(), password)
                st.session_state.doEncrypt = True
                password = ""
            else:
                st.write("No password given, not encrypting")
                st.session_state.doEncrypt = False
        else:
            st.session_state.file_data = file.getvalue()
            st.session_state.doEncrypt = False

        if "doEncrypt" in st.session_state:
            st.sidebar.write("Client.2: state.doEncrypt:", st.session_state.doEncrypt)

        choice = st.radio("", ("IPFS and Notarize", "Only IPFS"))
        
        if st.button("Submit"):   
            doc_hash = calculate_file_hash(st.session_state.file_data)
            if choice == "Only IPFS":
                file_ipfs_hash = pin_file(
                    st.session_state.file.name,
                    st.session_state.file_data,
                    st.session_state.doEncrypt,
                    doc_hash
                 )  
                st.write("IPFS Gateway Link to file metadata:")
                st.markdown(f"[Pinned metadata for file](https://ipfs.io/ipfs/{file_ipfs_hash})")
                st.sidebar.write("pinned only IPFS, doc_hash:", doc_hash)
            else:
                file_ipfs_hash = ""
                #doc_hash = calculate_file_hash(file.getvalue())
                st.sidebar.write("not pinned, doc_hash:", doc_hash)

            doNotarize = True
            try:
                tx_hash = contract.functions.createDoc(file.name, doc_type, 
                                        address, doc_hash,
                                        file_ipfs_hash, st.session_state.doEncrypt, doNotarize
                                        ).transact({'from': address, 'gas': 1000000})
                receipt = w3.eth.waitForTransactionReceipt(tx_hash)
                st.write("Blockchain transaction complete, available for Notary")            
            except:
                st.write("File is already saved on the blockchain and available for Notary!")
    

    get_account_history(st.session_state.address)

if page == 'Notary Login':
    userType = "Notary"
    st.session_state.page_index = NOTARY
    menu=["Sign In","Sign Up"]
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
            # Only one login can be active at a time
            st.session_state.login_status[USER] = []
            st.session_state.login_status[THIRD_PARTY] = []
            st.session_state.page_options = ['Client Login', 'Notary Signature', 'Verification Login']
            st.experimental_rerun()

if page == 'Notary Signature':
    userType = "Notary"
    st.title("Notarize File")
    # Unclear if we're going to ask for Email Address
    #st.write("Client email:", st.session_state.client)
    st.write("File name:", st.session_state.file.name)
    st.sidebar.write("Notary: state.doEncrypt:", st.session_state.doEncrypt)
    st.sidebar.write("Notary: state.password:", st.session_state.password)

    get_files_to_notarize()

    if st.button("Confirm and notarize"):
        file_ipfs_hash = pin_file(
            st.session_state.file.name,
            st.session_state.file_data,
            st.session_state.doEncrypt,
            calculate_file_hash(st.session_state.file_data)
            )

        # If we want to display link to file itself, we need pin_file() to return ipfs_file_hash
        #   Otherwise, that ipfs_file_hash can be read from the metadata
        st.write("IPFS Gateway Link to notarized file metadata:")
        st.markdown(f"[Pinned metadata for notarized file](https://ipfs.io/ipfs/{file_ipfs_hash})")

if page == 'Verification Login':
    userType = "User"
    # Even if user sign_in() fails, we want this index
    st.session_state.page_index = THIRD_PARTY
    menu=["Sign In","Sign Up"]
    choice=st.selectbox("Menu",menu)
    if choice == "Sign Up":
        sign_up(conn, userType)
    elif choice == "Sign In":
        st.session_state.login_status[THIRD_PARTY] = sign_in(conn, userType)
        if st.session_state.login_status[THIRD_PARTY]:
            # Only one login can be active at a time
            st.session_state.login_status[NOTARY] = []
            st.session_state.login_status[USER] = []
            st.session_state.page_options = ['Client Login', 'Notary Login', 'Verification']
            st.experimental_rerun()

if page == 'Verification':
    userType = "thirdParty"
    st.title("Verify Authenticity")

