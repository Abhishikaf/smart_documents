

import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json

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
    with open(Path('./compiled/smartDocs_abi.json')) as f:
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


################################################################################
# Helper functions to pin files and json to Pinata
################################################################################


def pin_file(file_name, file, notary_sign, password=""):
    token_json = {}
    if password:
        # file_data = encrypt(file.getvalue(), password)
        token_json["encrypted"] = True
        # Clear password
        password = ""
    else:
        file_data = file.getvalue()

    # Abhishikas hash function
    data_hash = get_hash(file_data)
    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(file_data)

    # Build a token metadata file for the artwork
    token_json["file_name"] = file_name
    token_json["file_hash"] = ipfs_file_hash
    token_json["file_data_hash"] = data_hash
    token_json["notary_sign"] = notary_sign
 
    json_data = convert_data_to_json(token_json)

    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    return json_ipfs_hash



##########
## MAIN ##
##########

notary1 = os.getenv("NOTARY1")
notary2 = os.getenv("NOTARY2")
notaries = [notary1, notary2]

# st.title("ALGORITHMIC, MACHINE LEARNING, AND NEURAL TRADING TOOLS WITH ESG SENTIMENT FOCUS")
# Had to use literal path here. Objected to Path('images/Title.jpg')

#st.image('images/Title.jpg', use_column_width='auto')

st.sidebar.title("Select a page")

page = st.sidebar.radio('', options=['Client Register and File Selection', 'Notary Signature', 'Verification'], key='1')

st.sidebar.markdown("""---""")

if page == 'Client Register and File Selection':
    doEncrypt=False

    st.markdown("## Register Client and Select File")
    st.write("Choose an account to get started")
    accounts = w3.eth.accounts
    address = st.selectbox("Select Account", options=accounts)
    st.markdown("---")

    email_addr = st.text_input("Please register with email address:")
    st.write("Email entered:", email_addr)
#    registered = contract.functions.newClient(email_addr)
    # Save for use on other pages
    st.session_state.client = email_addr

    st.write("Select a file to be notarized:")
    file = st.file_uploader("Add file")
    st.session_state.file = file
    if file:
        doEncrypt = st.checkbox("Optional: Encrypt " + file.name + " before IPFS upload")

    if doEncrypt:
        password = st.text_input("Enter password:")
        if password:
            st.write("Encrypt with password:", password)
            st.session_state.encrypt = True

    notary = st.selectbox("Select a Notary:", notaries)
    st.session_state.notary = notary
    st.write("Selected:", notary)

if page == 'Notary Signature':
    st.title("Notarize File")
    st.write("Notary chosen:", st.session_state.notary)
    st.write("Client email:", st.session_state.client)
    st.write("File name:", st.session_state.file.name)
    st.write("Do encrypt:", st.session_state.encrypt)

    # pin_file(...)
    # contract.functions.notarizeFile(...)


if page == 'Verification':
    st.title("Verify Authenticity")

