
![](https://github.com/Abhishikaf/smart_documents/blob/main/banner4.jpg?raw=true)

# Smart Documents: Notarization with IFPS File Storage

This application was conceived to be a means to upload and have access to documents. The additional functionality it implements is blockchain based verification, IFPS (Inter-Planetary File System) based storage, optional encryption, and ability to get documents notarized with payments made through ETH (Ethereum) to a verified notary. The app is implemented with a user interface using Streamlit.

The application uses a Ganache test network, which is used to test applications to be applied to real Ethereum network transactions.

## Technologies and Installation Guide:

This application was written in Python 3.7, Solidity 0.5.0, and SQL. It uses the following technologies:

- streamlit
- web3
- pandas
- hashlib
- cryptography
- sqlite3
- pinata

Please verify you have installed all of the requirements.

In addition, there are several other programs and accounts that need to be set up:

- The application uses Remix IDE to implement a smart contract. This can be run in the online version on their website.
- The application uses Ganache to simulate an Ethereum payment network. You must install Ganache.
- The application uses Metamask to connect the Ganache test network to the smart contract deployed in Remix IDE. You must install Metamask and set up an account.
- The application requires a Pinata account. You will need to acquire a PINATA_API_KEY and PINATA_SECRET_API_KEY.

In addition, two libraries of functions specific to this application have been written:

- crypto_funcs
- login_funcs

These libraries are included.

## Usage:

This program was designed to use an Ethereum test network simulated by Ganache. Please follow these steps:

You will need to start the program Ganache to simulate a local Ethereum network.

Open the program Metamask and import one or several accounts from the Ganache test network, using their private keys which can be accessed by clicking the key icon to the right of the account.

Open the web application Remix IDE. Upload the smart contract file ```SmartDocument.sol```. 

Compile the contract. Use the compiler version 0.5.0.

Deploy the contract: For the enviornment select Injected Web3 and enter an address displayed on Ganache into the box that says ```At Address```.

Get the contract address by hitting the copy button to the right of the deployed contract.

Create a file named ```.env``` in the application folder. You will need to edit it to look like this:

```
PINATA_API_KEY='yourpinataapikeyhere'
PINATA_SECRET_API_KEY='yourpinatasecretkeyhere'
WEB3_PROVIDER_URI=http://127.0.0.1:7545
SMART_CONTRACT_ADDRESS=0xA5637079F4313db0AB0ddb50f50662771A9F3C94
```
Note that the Pinata API Key and Pinata Secret Key are enclosed in single quotes. The Web3 Provider URI will be the RPC Server Address visible in your Ganache application. The Smart Contract Address will be the address copied from the deployed smart contract in your Remix IDE application.

### Running the Program

Once you have followed the above steps, the app can be run with the command ```streamlit run streamlit_app.py``` in the application folder.

The pages can be selected from the left frame's pulldown bar.

#### Client Login

To create a user, use the menu pulldown bar and select Sign Up. Choose a Username and Passord and click SignUp.

To login, select Sign In from the pulldown bar. Enter your username and password and click Login.

After you have logged in, you will be taken to the Select File Page.

#### Select File

Select the account corresponding to a Ganache account.

Enter the type of document to be uploaded.

Drag and drop a file, or click browse files and use the File Browser to select a document.

If you would like the file encrypted, click the encrypt checkbox.

Choose whether you would like the file sent to IFPS and Notarized, or only uploaded to IFPS.

For the purposes of demonstration, we have selected the last two Ganache accounts to be Notary Accounts. Select one of these.

Click Submit.

#### Notary Signature

We have provided two sample notary login accounts for testing:

Verified Notary 1: 123456
password: 1234

Verified Notary 2: 654321
password: 1234

Enter one of these and push login.

Copy the Document Hash of the Document to be notarized into the Document Hash field. Copy the Owner Wallet Address to the Owner Address Field. Click Confirm and Notarize.

#### Verification Login

Create a User Name and Password as above.

##### Method 1

The Notarized Hash is in the PDF file of the Receipt that will be saved to the application folder.

Upload the file and enter the Notarized Hash to check if it is the same. Click Verify.

##### Method 2

Click the File Hash Radio Button, copy the file hash from the receipt into the slot, then copy the notary hash from the receipt. Click Verify.

## Future Development:

- Implement DID - Decentralized Identification
- Implement verification of Notary credentials using existing databases
- Allow documents to be signed by multiple parties
- Save user accounts on a decentralized platform

## Acknowledgements:

Documents used in the banner graphic are all Public Domain except for one:

https://en.wikipedia.org/wiki/Notary_public#/media/File:Pakistan_Notary_example.jpg
Pakistan Notary Example

This file is licensed under the Creative Commons Attribution-Share Alike 4.0 International license.

The rest are Public Domain:

https://kingcounty.gov/~/media/depts/records-licensing/archives/images/statecert.ashx?la=en
A Marriage Certificate from King County

https://upload.wikimedia.org/wikipedia/commons/6/6c/Constitution_of_the_United_States%2C_page_1.jpg
The Constitution of the United States

https://www.irs.gov/pub/irs-pdf/f1040.pdf
IRS Form 1040 for personal income tax reporting.

https://en.wikipedia.org/wiki/Contract#/media/File:Insurance_Contact_2.jpg
Thomas Boylston to Thomas Jefferson, May 1786, Maritime Insurance Premiums

https://www.hud.gov/sites/documents/1.PDF
HUD Form for Real Estate Sales

https://en.wikipedia.org/wiki/Magna_Carta#/media/File:Magna_Carta_(British_Library_Cotton_MS_Augustus_II.106).jpg
The Magna Carta

## Conception and Coding:

Abhishika Fatehpuria (abhishika@gmail.com)

David Jonathan (djonathan@cox.net)

Nara Arakelyan (n_arakel@yahoo.com)

Preston Hodsman (phodsman@yahoo.com)

Anthony Thomas Hall III (hiflynmedic@aol.com)

## License

MIT
