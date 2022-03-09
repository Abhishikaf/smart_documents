# Smart Documents: Notarization with IFPS File Storage

This application was conceived to be a means to upload and have access to documents. The additional functionality it implements is blockchain based verification, IFPS (Inter-Planetary File System) based storage, optional encryption, and ability to get documents notarized with payments made through ETH (Ethereum) to a verified notary. The app is implemented with a user interface using Streamlit.

## Technologies and Installation Guide:

This application was written in Python, Solidity, and SQL. It uses the following technologies:

- streamlit

Please verify you have installed all of the requirements.

- The application uses Remix IDE to implement a smart contract. This can be run in the online version on their website.
- The application uses Ganache to simulate an Ethereum payment network. You must install Ganache.
- The application uses Metamask to connect the Ganache test network to the smart contract deployed in Remix IDE.
- The application uses Remix IDE to implement a smart contract. This can be run in the online version on their website.
- The application requires a Pinata account. You will need to acquire a PINATA_API_KEY and PINATA_SECRET_API_KEY.

## Usage:

This program was designed to use an Ethereum test network simulated by Ganache. Please follow these steps:

You will need to start the program Ganache to simulate a local Ethereum network.

Open the program Metamask and enter several accounts from the Ganache test network.

Open the web application Remix IDE. Upload the smart contract file ```SmartDocument.sol```. 

Compile the contract. Use the compiler version 0.5.0.

Deploy the contract. For the enviornment select Web3 Provider and enter the RPC Server address displayed on Ganache into the box that asks for the Web3 Provider Endpoint. Choose an account that corresponds to one of the accounts in Ganache. Select the SmartDocument contract. Push the Deploy button.

Get the contract address by hitting the copy button to the right of the deployed contract.

Create a file named ```.env``` in the application folder. You will need to edit it to look like this:

```
PINATA_API_KEY='yourpinataapikeyhere'
PINATA_SECRET_API_KEY='yourpinatasecretkeyhere'
WEB3_PROVIDER_URI=http://127.0.0.1:7545
SMART_CONTRACT_ADDRESS=0xA5637079F4313db0AB0ddb50f50662771A9F3C94
```
Note that the Pinata API Key and Pinata Secret Key are enclosed in single quotes. The Web3 Provider URI will be the RPC Server Address visible in your Ganache application. The Smart Contract Address will be the address copied from the deployed smart contract in your Remix IDE application.

Once you have followed the above steps, the app can be run with the command ```streamlit run app.py``` in the application folder.





## Future Development:

## Acknowledgements:

## Conception and Coding:

Abhishika Fatehpuria (abhishika@gmail.com)

David Jonathan (djonathan@cox.net)

Preston Hodsman (phodsman@yahoo.com)

Nara Arakelyan 

David Thomas Hall III

## License

MIT
