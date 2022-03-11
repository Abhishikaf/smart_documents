# Imports
import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import hashlib
import sqlite3
import pandas as pd
from fpdf import FPDF
from datetime import datetime

from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json
from crypto_funcs import encrypt_data, decrypt_data
from login_funcs import sign_up, sign_in, check_user

load_dotenv()
# Connection with SQL database
conn=sqlite3.connect("data.db")

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

# Page configuration
st.set_page_config(
    layout="wide",
)

################################################################################
# Contract Helper function:
# 1. Loads the contract once using cache
# 2. Connects to the contract using the contract address and ABI
################################################################################



@st.cache(allow_output_mutation=True)
# Function to load the Smart Contract
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

# Function to get files to be notarized

def get_files_to_notarize(license,pending_file_container):

    pending_file_container.empty()
    pendingFiles = contract.functions.getPendingFiles(license).call()
    with pending_file_container.container():
        if pendingFiles:
            df = pd.DataFrame(pendingFiles).T
            df.columns = ['Document Hash', 'Owner Wallet Address']
            st.table(df)

        else:
            st.write("No files pending notarization")


# Getting notarized files
def get_notarized_files():
    notarizedFiles = contract.functions.getNotarizedFiles().call()
    if notarizedFiles:
        df = pd.DataFrame(notarizedFiles).T
        df.columns = ['Doc Hash', 'Notarized Hash']
        st.table(df)


# Function to get account history from blockchain using user wallet address
# and displaying it under account history container
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


# Creatin a 'pdf' receipt for the notarized document and saving it

def generate_receipt(date, user_wallet, f_hash, notary_wallet, license, n_hash, filename):
    pdf = FPDF(orientation='P', unit='pt', format='A4')
    pdf.add_page()


    pdf.set_font("Times", "B", 24)
    pdf.cell(0,80, "Notarized Document Receipt", 0, 1, "C")

    pdf.set_font("Times", "B", 14)
    pdf.cell(100,25, "Notarized Date:")

    pdf.set_font("Times", "", 12)
    pdf.cell(0,25, "{}".format(date), 0, 1,)
    pdf.cell(0,5, "", 0, 1)

    pdf.set_font("Times", "B", 14)
    pdf.cell(100,25, "User Wallet:")
    pdf.set_font("Times", "", 12)
    pdf.cell(0,25, "{}".format(user_wallet), 0, 1,)

    pdf.set_font("Times", "B", 14)
    pdf.cell(100,25, "File Hash:")
    pdf.set_font("Times", "", 12)
    pdf.cell(0,25, "{}".format(f_hash), 0, 1,)

    pdf.set_font("Times", "B", 14)
    pdf.cell(100,25, "Notary License:")
    pdf.set_font("Times", "", 12)
    pdf.cell(0,25, "{}".format(license), 0, 1,)

    pdf.set_font("Times", "B", 14)
    pdf.cell(100,25, "Notary Wallet:")
    pdf.set_font("Times", "", 12)
    pdf.cell(0,25, "{}".format(notary_wallet), 0, 1,)

    pdf.set_font("Times", "B", 14)
    pdf.cell(100,25, "Notary Hash:")
    pdf.set_font("Times", "", 12)
    pdf.cell(0,25, "{}".format(n_hash), 0, 1,)
    f_name=f"{filename}_receipt.pdf"
    return pdf.output(f_name, "F")



################################################################################
# Helper functions to pin files and json to Pinata
################################################################################


def pin_file(file_name, file_data, encrypted, notarized, license, doc_hash):
    token_json = {}

    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(file_data)

    # Build a token metadata file for the artwork
    token_json["file_name"] = file_name
    token_json["file_hash"] = ipfs_file_hash
    token_json["file_data_hash"] = doc_hash

    if encrypted:
        token_json["encrypted"] = True
    else:
        token_json["encrypted"] = False
    if notarized:
        token_json["notarized"] = True
    else:
        token_json["notarized"] = False

    token_json["notary_id"] = license

    json_data = convert_data_to_json(token_json)

    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    # This doc_hash must be used because encryption may have happened here
    return json_ipfs_hash, ipfs_file_hash


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

# Insert picture 
st.image('images/Title.jpg', use_column_width='auto')

st.sidebar.title("Select a page")

page = st.sidebar.selectbox('', options=st.session_state.page_options, index=st.session_state.page_index )

st.sidebar.markdown("""---""")

# Setting accounts to user, notary and verifier 
accounts = w3.eth.accounts
user_options = accounts[0:6]
verifier_options = accounts[6:8]
notary_options = accounts[8:10]
#notary_licence = ['1234', '5678']
notary_licence = ['123456', '654321']


if 'login_status' not in st.session_state:
    st.session_state.login_status = login_status


#Sign up and Sign in using functions from login_funcs.py
if page == 'Client Login':
    userType = "User"
    # Even if user sign_in() fails, we want this index
    st.session_state.page_index = USER
    menu=["Sign In","Sign Up"]
    choice=st.selectbox("Menu",menu)
    if choice == "Sign Up":
        st.write("Choose a User account to get started")
        address = st.selectbox("Select User Account", user_options)
        st.session_state.address = address
        sign_up(conn, userType, address)
    elif choice == "Sign In":
        st.session_state.login_status[USER] = sign_in(conn, userType)
        if st.session_state.login_status[USER]:
            # Only one login can be active at a time
            st.session_state.login_status[NOTARY] = []
            st.session_state.login_status[THIRD_PARTY] = []
            st.session_state.page_options = ['Client File Selection', 'Notary Login', 'Verification Login']
            st.experimental_rerun()


# File selection
if page == 'Client File Selection':
    doEncrypt=False
    st.session_state.address = st.session_state.login_status[USER][0][4]
    st.markdown("## Select File")
    
    st.markdown("---")

    # email_addr = st.text_input("Please register with email address:")
    # st.write("Email entered:", email_addr)
#    registered = contract.functions.newClient(email_addr)
    # Save for use on other pages
    # st.session_state.client = email_addr

# Printing the history log on sidebar
    if 'address' in st.session_state:
        address = st.session_state.address
        st.sidebar.markdown("### Client Wallet Address:")
        st.sidebar.markdown(f"""<p style = "line-height:50%; font-size:14px">{address}</p>""",unsafe_allow_html=True)
        st.sidebar.markdown("### Account History")

        account_history = st.sidebar.empty()
        get_account_history(address, account_history)


    doc_type = st.text_input("Enter the type of the document to be uploaded")
    #st.write(" Document Type:", doc_type)
    st.session_state.doc_type = doc_type

    st.write("Select a file to be uploaded:")
    file = st.file_uploader("")
    st.session_state.file = file
    password = ""
    st.session_state.password = password
    
    # if "doEncrypt" in st.session_state:
    #     st.sidebar.write("Client: state.doEncrypt:", st.session_state.doEncrypt)
    
# Choosing options for uploaded file
# 1st option - encrepted before the file is pinned to IPFS 
# Can be only uploaded in IPFS or notarized before pinning to IPFS  
    if file:
        st.write("Optional before IPFS upload:")

        doEncrypt = st.checkbox("Encrypt " + file.name )
        if doEncrypt:
            password = st.text_input("Enter password:", type="password")
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

        choice = st.radio("", ("IPFS and Notarize", "Only IPFS"))

        
        if choice == "IPFS and Notarize":
            notary = st.selectbox("Select Notary Address", notary_options)
            index = notary_options.index(notary)
            st.session_state.index = index
        
        

        if st.button("Submit"):   
            doc_hash = calculate_file_hash(st.session_state.file_data)
            
            if choice == "Only IPFS":
                doNotarize = False
                license = ""
                st.session_state.license = license        
            else:
                
                license = notary_licence[st.session_state.index] # get_notary_license(notary) --- pull from notary database
                st.session_state.license = license
                doNotarize = True
                
            metadata_ipfs_hash, file_ipfs_hash = pin_file(
                    st.session_state.file.name,
                    st.session_state.file_data,
                    st.session_state.doEncrypt,
                    doNotarize,
                    st.session_state.license,
                    doc_hash
                 )  
            st.write("IPFS Gateway Link to file metadata:")
            st.markdown(f"[Pinned metadata for file](https://ipfs.io/ipfs/{metadata_ipfs_hash})")
            st.markdown(f"[Pinned File](https://ipfs.io/ipfs/{file_ipfs_hash})")
            
           
            try:
                doc_hash = calculate_file_hash(file.getvalue())
                tx_hash = contract.functions.createDoc(file.name, doc_type, 
                                        address, doc_hash,
                                        file_ipfs_hash, doEncrypt, doNotarize, st.session_state.license,
                                        ).transact({'from': address, 'gas': 1000000})
                receipt = w3.eth.waitForTransactionReceipt(tx_hash)
                st.write("Blockchain transaction complete, available for Notary")            
            except:
                st.write("File is already saved on the blockchain and available for Notary!")
    

    get_account_history(st.session_state.address, account_history)

if page == 'Notary Login':
    userType = "Notary"
    st.session_state.page_index = NOTARY
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

 
    st.markdown("### Files Pending Notarization")

    license = st.session_state.login_status[NOTARY][0][3]

    for i in range(len(notary_licence)):
        if notary_licence[i] == license:
            notary = notary_options[i]
            st.session_state.notary = notary
    
    pending_file_container = st.empty()
    
    get_files_to_notarize(license, pending_file_container)

    doc_hash = st.text_input("Document Hash")
    address = st.text_input("Owner address")

    time_stamp= datetime.now()
    now = int(datetime.timestamp(time_stamp))
    st.session_state.now = now

    h = hashlib.sha256()
    h.update(str(doc_hash).encode('utf-8'))
    h.update(str(notary).encode('utf-8'))
    h.update(str(license).encode('utf-8'))
    h.update(str(st.session_state.now).encode())

    notary_hash = h.hexdigest()
    
    if st.button("Confirm and notarize"):
        try:            
            tx_hash = contract.functions.notarizeDoc(st.session_state.notary, license, doc_hash,     
                                               notary_hash, st.session_state.now ).transact({'from': address, 'gas': 1000000})
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            st.write("Transaction receipt mined:")            
        except:
            st.write("File is not pending notarization")

        fileName = contract.functions.getFileName(doc_hash).call()
        generate_receipt(st.session_state.now, address, doc_hash, st.session_state.notary, license, notary_hash, fileName)

    get_files_to_notarize(license,pending_file_container)
   
    
if page == 'Verification Login':
    userType = "User"
    # Even if user sign_in() fails, we want this index
    st.session_state.page_index = THIRD_PARTY
    menu=["Sign In","Sign Up"]
    choice=st.selectbox("Menu",menu)
    if choice == "Sign Up":
        sign_up(conn, userType, "")
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

    #get_notarized_files()

    st.sidebar.markdown("""#### Choose an account to get started""")

    verifier = st.sidebar.selectbox("Select Account", verifier_options)

    st.sidebar.markdown("""<br><b> Verify using</b></br>""", unsafe_allow_html=True)
    verify_by = st.sidebar.radio("", ("File Upload", "File Hash"))

    if verify_by == "File Upload":
        st.sidebar.write("Select a file to be uploaded:")
        file = st.file_uploader("")

        if file:
            doc_hash = calculate_file_hash(file.getvalue())
            st.session_state.doc_hash = doc_hash
    elif verify_by == "File Hash":
        doc_hash = st.sidebar.text_input("Enter Hash of the document to be verified")
        st.session_state.doc_hash = doc_hash

    st.sidebar.markdown("""<br> <b>Notarized Hash </b></br>""", unsafe_allow_html=True)
    notary_hash = st.sidebar.text_input(" Enter the Notarized Hash of the Document for verification:")
    
    if st.sidebar.button("Verify"):
        verification_data = contract.functions.getVerifyData(doc_hash).call()
                
        h = hashlib.sha256()
        h.update(str(st.session_state.doc_hash).encode('utf-8'))
        h.update(str(verification_data[1]).encode('utf-8'))
        h.update(str(verification_data[3]).encode('utf-8'))
        h.update(str(verification_data[4]).encode())
        notary_hash_from_blkchain = h.hexdigest()
        st.markdown("""<b> Generated Notarized Hash </b>""", unsafe_allow_html=True)
        st.write(notary_hash_from_blkchain)

        if(notary_hash == notary_hash_from_blkchain):
            st.markdown(" #### File Verification was a success ")
        else:
            #st.markdown(""" #### File Verification <p style = "font-size: 14px;color:red">failed!</p>""", unsafe_allow_html=True)
            new_title = '<p style="font-family:sans-serif; color:Red; font-size: 24;">File Verification Failed</p>'
            st.markdown(new_title, unsafe_allow_html=True)

        st.markdown("""<b>File Details Retrieved from the Blockchain:</b>""", unsafe_allow_html=True)
        st.markdown("""<b>File Type: </b>""" + verification_data[2],unsafe_allow_html=True)
        st.markdown("""<b>Owner Address: </b>""" + verification_data[0],unsafe_allow_html=True)
        st.markdown("""<b>Notary Address: </b>""" + verification_data[1],unsafe_allow_html=True)
        st.markdown("""<b>Notary License: </b>""" + verification_data[3],unsafe_allow_html=True)
        st.markdown("""<b>Notarization timestamp: </b>""" + datetime.utcfromtimestamp(verification_data[4]).strftime('%Y-%m-%d %H:%M:%S'),unsafe_allow_html=True)
