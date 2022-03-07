pragma solidity ^0.5.0;
//pragma experimental ABIEncoderV2;

contract SmartDocument {

    enum DocumentStatus {NotNotarized, PendingNotarization, Notarized}

    struct Notary{
        address notary;
        string license;
        uint timestamp_notarized;
    }

    struct Document {
        string fileName;
        string docType;
        address docOwner;
        string fileHash;
        //Notary notaryInfo;
        string ipfsHash;
        bool encrypt;
        DocumentStatus status; // NotNotrized, PendingNotarization, Notarized
        uint timestamp_created;
    
        //uint owner_DID; //Decentralized identifier
    }

    mapping (string => Document) documentList;

    event DocumentCreated(address indexed docOwner, string fileHash, string fileName, string docType, DocumentStatus status, uint timestamp);

    function createDoc(string memory fileName, string memory docType, 
                        address docOwner, string memory hash,
                        string memory ipfsHash, bool encrypt, bool notarize) public {

        require(!checkDoc(hash));
        if(notarize) 
            documentList[hash] = Document(fileName, docType, docOwner, hash, ipfsHash, encrypt, DocumentStatus.PendingNotarization, block.timestamp);
            
        else
            documentList[hash] = Document(fileName, docType, docOwner, hash, ipfsHash, encrypt, DocumentStatus.NotNotarized, block.timestamp);      
      

        emit DocumentCreated(docOwner, hash, fileName, docType, documentList[hash].status, block.timestamp);

    }

    function checkDoc(string memory hash) view internal returns (bool) {
        return(documentList[hash].timestamp_created > 0);
    }


}