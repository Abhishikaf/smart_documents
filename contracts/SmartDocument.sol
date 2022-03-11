pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

contract SmartDocument {

    enum DocumentStatus {NotNotarized, PendingNotarization, Notarized}

    struct Notary{
        address notary;
        string license;
        uint timestamp_notarized;
        string notarized_hash;
    }

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
           
        //uint owner_DID; //Decentralized identifier
    }

    mapping (uint => string) documentHash;
    mapping (string => Document) documentList;
    mapping (string =>Notary) notaryInfo;

    event DocumentCreated(address indexed docOwner, string fileHash, string fileName, string docType, uint timestamp);
    event DocumentNotarized(string docHash, address indexed notary, string license, uint timestamp);

    uint public docCount;
    uint public pendingCount;

    constructor() public{
        docCount = 0;
        pendingCount = 0;
    }

    function createDoc(string memory fileName, string memory docType, 
                        address docOwner, string memory hash,
                        string memory ipfsHash, bool encrypt, bool notarize, string memory license) public {

        require(!checkDoc(hash));

        if(notarize) {
            documentList[hash] = Document(fileName, docType, docOwner, hash, ipfsHash, encrypt,notarize, DocumentStatus.PendingNotarization, block.timestamp, license);   
            pendingCount++;         
        }
        else{
            documentList[hash] = Document(fileName, docType, docOwner, hash, ipfsHash, encrypt, notarize, DocumentStatus.NotNotarized, block.timestamp, license);                      
        }

        documentHash[docCount] = hash;
        docCount++;

        emit DocumentCreated(docOwner, hash, fileName, docType, block.timestamp);

    }


    function notarizeDoc(address notary, string memory license, string memory docHash) public {
        require(documentList[docHash].status == DocumentStatus.PendingNotarization);
        
        notaryInfo[docHash].notary = notary;
        notaryInfo[docHash].license = license;
        notaryInfo[docHash].timestamp_notarized = block.timestamp;
        documentList[docHash].status = DocumentStatus.Notarized;

        pendingCount--;

        emit DocumentNotarized(docHash, notary, license, block.timestamp);

    }

    function getDocuments() public view returns (Document [] memory){

        Document [] memory document = new Document[](docCount);
        for(uint i=0; i< docCount; i++) {
            Document storage doc = documentList[documentHash[i]];
            document[i] = doc;
        }
        return document;
    }

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

    function getDocState(string calldata hash) external view returns (uint) {
        return uint(documentList[hash].status);
    }

    function checkDoc(string memory hash) view internal returns (bool) {
        return(documentList[hash].timestamp_created > 0);
    }


}