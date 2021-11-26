## Amplius

The Amplius prototype is intended to demonstrate the feasibility of a multi-protocol attestation and distribution system. It allows for the attestation of files on the web using the Ethereum blockchain, the creation of links, as well as resolving and validating links with the associated claims.


## Usage

```
Usage: amplius.py <command> [argument]*

Amplius a user interface for creating and verifying attested multi-protocol links (AMPL). The prototype supports the transfer clients IPFS, Git, and HTTP.

<command> is one of the following attestation, identity_acc, or transfer commands.

Attestation Commands:
--attest [file]*                     create an identity if none is present, distribute all files, issue a content-based claim
--issue-claim [uri]*                 issue a content-based claim for all files retrievable under the given URIs
--link=UUID <merkle-root> [p]        create a link with a new UUID v4 as ID pointing to claim <merkle-root>, parent link ID <p>
--link=<link-id> <merkle-root> [p]   create a link <link-id> pointing to the claim <merkle-root> with parent link ID <p>
--resolve=<link-id>                  resolve the claim Merkle root linked by <link-id>
--retrieve <merkle-root> <record-id> retrieve data of the claim identified by <merkle-root>, <record-id>
--validate-claim [file]*             validate a claim using the Merkle root of all files
--validate-claim=<record-id> [file]* validate a claim under the specified record ID using the Merkle root of all files
--validate-claim=<issuer> [file]*    validate claims issued by account address <issuer> with all given files

Identity Commands:
--eth-account-new                    create an identity for attestations
--eth-account-show                   show the current identity for attestations

Transfer Commands:
--distribute [file]*                 distribute all files using all transfer clients with example repositores
--distribute=ipfs [file]*            add files to IPFS and pin at a remote node
--distribute=<GIT_URL> [file]*       commit and push all files with Git to <GIT_URL> starting with git or http and ending in .git
--distribute=<HTTP_URL> [file]*      send all files with HTTP PUT requests to <HTTP_URL> starting with http
--retrieve <URI>                     retrieve all files from an ipfs, git, or HTTP <URI>
```

# Requirements

Amplius requires an up-to-date distribution of Python 3 for Linux or macOS with the additional modules requests, base58, web3 and bs4.

