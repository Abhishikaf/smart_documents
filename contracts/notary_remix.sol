pragma solidity ^0.5.0;

// TODO: add IPFS stuff

contract NotaryProject {
    address admin;

    // TODO:  add address signature field, which will be the Notary's eth address?
    // TODO:  add ipfs_hash field
    // TODO:  If encryption option is added, do we need a boolean field, for retrieval (and decrypting)

    struct notarizedFile {
        string fileURI;
        uint timeStamp;
    }

    mapping (bytes32 => notarizedFile) notarizedFiles;
    bytes32[] filesHashArray;

    // Client is the customer who wants docs to be notarized
    struct Client {
        string name;
        bytes32[] clientFiles;
    }

    mapping (address=> Client) Clients;
    address[] clientsByAddress;

    function newClient(string memory name) public returns(bool success) {
        address thisClient = msg.sender;

        if (bytes(Clients[msg.sender].name).length == 0 && bytes(name).length != 0) {
            Clients[thisClient].name = name;
            clientsByAddress.push(thisClient);

            return true;
        } else {
            return false;
        }
    }

    function  notarizeFile(string memory fileURI, bytes32 SHA256notaryHash) public returns (bool) {

    	// TODO: require that msg.sender is in the list of authorized Notaries.

        address thisAddress = msg.sender;
        // newClient() must have been called first
        if (bytes(Clients[thisAddress].name).length != 0) {
            if (bytes(fileURI).length != 0) {
                // Do not allow changing ownership of a previously notarized file
                if (bytes(notarizedFiles[SHA256notaryHash].fileURI).length == 0) {
                    // Record hash in master list
                    filesHashArray.push(SHA256notaryHash);
                }
                notarizedFiles[SHA256notaryHash].fileURI = fileURI;
                notarizedFiles[SHA256notaryHash].timeStamp = block.timestamp;
		// TODO: ...signature = msg.sender; which is a Notary
                Clients[thisAddress].clientFiles.push(SHA256notaryHash);

                return true;
            } else {
                return false;
            }

            //return true;
        } else {
            return false;
        }
    }

    // TODO: Some of these getter functions should be called ONLY by Notaries
    // TODO: Some by either Notaries or Clients
    function getClients () view public returns (address[] memory) {
        return clientsByAddress;
    }

    // TODO: Maybe use the clientFiles hashes to call getfile() to dump fileURI, ipfs_hash, etc. ?
    function getClient (address clientAddress) view public returns(string memory , bytes32[] memory) {
        return(Clients[clientAddress].name, Clients[clientAddress].clientFiles);
    }

    function getAllFles() view public returns (bytes32[] memory) {
        return filesHashArray;
    }

    function getFile (bytes32 SHA256notaryHash) view public returns(string memory, uint) {
        return(notarizedFiles[SHA256notaryHash].fileURI, notarizedFiles[SHA256notaryHash].timeStamp);
    }
}

