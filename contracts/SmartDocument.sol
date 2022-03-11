pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;


// Smart Contract to store Document Hash on the blockchain and subsequently notarize it and also verify it
contract SmartDocument {

    // Document's notarization status
    enum DocumentStatus {NotNotarized, PendingNotarization, Notarized}

    // Structure to hold the notary information - Notary wallet address, notary license number, timestamp of notarization, hash of notarized document

    struct Notary{
        address notary;
        string license;
        uint timestamp_notarized;
        string notarized_hash;
    }


    // Structure to hold the documetn information - document filename, doc description, owner wallet address, document hash, document ipfs hash, 
    // weather encrypted on ipfs, weather it needs notarization, notarization status of the document, timestamp of document creation, 
    // notary wallet address(if applicable otherwise an empty string)

        struct Document {

        string fileName;
        string docType;
        address docOwner;
        string fileHash;
        string ipfsHash;
        bool encrypt;
        bool notarize;
        DocumentStatus status; // NotNotrized, PendingNotarization, Notarized
        uint timestamp_created;
        string notary;
           
        //uint owner_DID; //Decentralized identifier -  for future development of identity 
    }

    // mapping of the document count to the document hash
    mapping (uint => string) documentHash;

    // mapping document hash to the document structure
    mapping (string => Document) documentList;

    // mapping notary address with Notary structure
    mapping (string =>Notary) notaryInfo;

    // Event to log created document on the blockchain
    event DocumentCreated(address indexed docOwner, string fileHash, string fileName, string docType, uint timestamp);

    // Event to log notarized document on the blockchain
    event DocumentNotarized(string docHash, address indexed notary, string license, string notaryHash, uint timestamp);

    uint public docCount; // count of total documents
    uint public pendingCount; // count of pending documents
    uint public notarizedCount; // count of notarized documents

    constructor() public{
        docCount = 0;
        pendingCount = 0;
        notarizedCount = 0;
    }


    // Function for creating a document and storing it on blockchain
    function createDoc(string memory fileName, string memory docType, 
                        address docOwner, string memory hash,
                        string memory ipfsHash, bool encrypt, bool notarize, string memory license) public {

        // Check if the document hash already exists on the blockchain
        require(!checkDoc(hash));

        // If notarize set the document status to pending otherwise not notarized
        if(notarize) {
            documentList[hash] = Document(fileName, docType, docOwner, hash, ipfsHash, encrypt,notarize, DocumentStatus.PendingNotarization, block.timestamp, license);   
            pendingCount++;         
        }
        else{
            documentList[hash] = Document(fileName, docType, docOwner, hash, ipfsHash, encrypt, notarize, DocumentStatus.NotNotarized, block.timestamp, license);                      
        }

        // store the hash and map it to the doc count
        documentHash[docCount] = hash;
        docCount++;

        // save the creadted document log
        emit DocumentCreated(docOwner, hash, fileName, docType, block.timestamp);

    }

    // Function to notarize the document
    function notarizeDoc(address notary, string memory license, string memory docHash, string memory notaryHash, uint timestamp) public {
        
        // The document status has to be pending
        require(documentList[docHash].status == DocumentStatus.PendingNotarization);
        
        // assign the notary info to the struct  notary
        notaryInfo[docHash].notary = notary;
        notaryInfo[docHash].license = license;
        notaryInfo[docHash].timestamp_notarized = timestamp;
        notaryInfo[docHash].notarized_hash = notaryHash;

        // change the document staus to notarized
        documentList[docHash].status = DocumentStatus.Notarized;
        
        // decrease the count of pending notarization files
        pendingCount--;

        // increase the count of notarized docs
        notarizedCount++;

        // save notarized docs on the blockchcain
        emit DocumentNotarized(docHash, notary, license,notaryHash, timestamp);
    }

    // Function to get all the documents information
    function getDocuments() public view returns (Document [] memory){

        Document [] memory document = new Document[](docCount);
        for(uint i=0; i< docCount; i++) {
            Document storage doc = documentList[documentHash[i]];
            document[i] = doc;
        }
        return document;
    }

    // Function to get all the pending notarization files filtered by the notary license. 
    //The function returns an array of document hashes and an array of the related owner addresses

    function getPendingFiles(string memory license) public view returns (string[] memory, address[] memory){

        string[] memory dochashes = new string[](pendingCount);
        address[] memory ownerAddress = new address[](pendingCount);

        uint j = 0;

        for(uint i=0; i<docCount && j< pendingCount; i++){
            Document storage doc = documentList[documentHash[i]];
            if(doc.status == DocumentStatus.PendingNotarization && (keccak256(abi.encodePacked(doc.notary)) == keccak256(abi.encodePacked(license)))){
                dochashes[j] = doc.fileHash;
                ownerAddress[j] = doc.docOwner;
                j++;
            }
        }

        return (dochashes, ownerAddress);
    }

    // Function to get all the notarized files 
    //The function returns an array of document hashes and an array of the related notarized document hashes
    function getNotarizedFiles() public view returns (string[] memory, string[] memory){

        string[] memory dochashes = new string[](notarizedCount);
        string[] memory notaryhashes = new string[](notarizedCount);

        uint j = 0;

        for(uint i=0; i<docCount && j< notarizedCount; i++){
            Document storage doc = documentList[documentHash[i]];
            Notary storage notary = notaryInfo[documentHash[i]];
            if(doc.status == DocumentStatus.Notarized){
                dochashes[j] = doc.fileHash;
                notaryhashes[j] = notary.notarized_hash;
                j++;
            }
        }

        return (dochashes, notaryhashes);
    }

    // Function to return document information for the third party verifier
    function getVerifyData(string calldata hash) external view returns (address, address , string memory, string memory, uint){

        // checking for the document status. True if notarized else the function does not execute
        require(documentList[hash].status == DocumentStatus.Notarized);
               
        return(documentList[hash].docOwner, notaryInfo[hash].notary, documentList[hash].docType, notaryInfo[hash].license, notaryInfo[hash].timestamp_notarized);
    }

    // Function to get the File name for a document hash stored on the blockchain
    function getFileName(string calldata hash) external view returns (string memory) {
        return(documentList[hash].fileName);
    }

    // Function to get the current state of the document
    function getDocState(string calldata hash) external view returns (uint) {
        return uint(documentList[hash].status);
    }

    // Function to check if the document exists on the blockchain
    function checkDoc(string memory hash) view internal returns (bool) {
        return(documentList[hash].timestamp_created > 0);
    }


}