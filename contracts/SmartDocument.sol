pragma solidity ^0.5.0;
//pragma experimental ABIEncoderV2;

contract SmartDocument {

    struct Notary{
        address notary;
        string license;
    }

    struct Document {
        string fileName;
        string docType;
        address docOwner;
        string fileHash;
        Notary notaryInfo;
        string ipfsHash;
        bool encrypt;
        string status; // NotNotarized, PendingNotarization, Notarized
       
        uint timestamp_created;
        uint timestamp_notarized;
        uint owner_DID; //Decentralized identifier
    }

    mapping (string => Document) public documentList;

    event DocumentCreated(address indexed docOwner, string fileHash, uint timestamp);

    function createDoc(address docOwner, string memory hash) public {
        require(!checkDoc(hash));
        documentList[hash] = Document(docOwner, hash, block.timestamp);

        emit DocumentCreated(docOwner, hash, block.timestamp);

    }

    function checkDoc(string memory hash) view internal returns (bool) {
        return documentList[hash].timestamp_created > 0;
    }


}