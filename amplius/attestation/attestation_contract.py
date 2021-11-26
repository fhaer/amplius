from web3 import Web3

ADDRESS_STR = "0x5627da24A01B5799AbC84300ACBf2A778933bEed"
ADDRESS = Web3.toChecksumAddress(ADDRESS_STR)

ABI = [

	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "linkID",
				"type": "bytes32"
			},
			{
				"internalType": "bytes32",
				"name": "merkleRoot",
				"type": "bytes32"
			},
			{
				"internalType": "bytes32",
				"name": "parentLinkID",
				"type": "bytes32"
			}
		],
		"name": "link",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "merkleRoot",
				"type": "bytes32"
			},
			{
				"internalType": "uint8[]",
				"name": "schemeIDs",
				"type": "uint8[]"
			},
			{
				"internalType": "uint16[]",
				"name": "authorityIDs",
				"type": "uint16[]"
			},
			{
				"internalType": "bytes32[]",
				"name": "paths",
				"type": "bytes32[]"
			},
			{
				"internalType": "uint8[]",
				"name": "fileSetExtensionMarker",
				"type": "uint8[]"
			},
			{
				"internalType": "uint8",
				"name": "mimeTypeID",
				"type": "uint8"
			}
		],
		"name": "recordClaim",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "merkleRoot",
				"type": "bytes32"
			},
			{
				"internalType": "uint8",
				"name": "claimRecordID",
				"type": "uint8"
			},
			{
				"internalType": "uint8[]",
				"name": "schemeIDs",
				"type": "uint8[]"
			},
			{
				"internalType": "uint16[]",
				"name": "authorityIDs",
				"type": "uint16[]"
			},
			{
				"internalType": "bytes32[]",
				"name": "paths",
				"type": "bytes32[]"
			},
			{
				"internalType": "uint8[]",
				"name": "fileSetExtensionMarker",
				"type": "uint8[]"
			}
		],
		"name": "recordClaimURI",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "mimeType",
				"type": "bytes32"
			}
		],
		"name": "registerMimeType",
		"outputs": [
			{
				"internalType": "uint8",
				"name": "",
				"type": "uint8"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "uriAuthority",
				"type": "bytes32"
			}
		],
		"name": "registerUriAuthority",
		"outputs": [
			{
				"internalType": "uint16",
				"name": "",
				"type": "uint16"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "uriScheme",
				"type": "bytes32"
			}
		],
		"name": "registerUriScheme",
		"outputs": [
			{
				"internalType": "uint8",
				"name": "",
				"type": "uint8"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			}
		],
		"name": "claimRegistry",
		"outputs": [
			{
				"internalType": "uint8",
				"name": "nClaimRecords",
				"type": "uint8"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "merkleRoot",
				"type": "bytes32"
			},
			{
				"internalType": "uint8",
				"name": "claimRecordID",
				"type": "uint8"
			}
		],
		"name": "getIssuerMetadata",
		"outputs": [
			{
				"internalType": "address",
				"name": "accountAddress",
				"type": "address"
			},
			{
				"internalType": "bytes32",
				"name": "externalDID",
				"type": "bytes32"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "merkleRoot",
				"type": "bytes32"
			}
		],
		"name": "getNClaimRecords",
		"outputs": [
			{
				"internalType": "uint8",
				"name": "",
				"type": "uint8"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "merkleRoot",
				"type": "bytes32"
			},
			{
				"internalType": "uint8",
				"name": "claimRecordID",
				"type": "uint8"
			}
		],
		"name": "getStorageMetadata",
		"outputs": [
			{
				"internalType": "bytes32",
				"name": "mimeType",
				"type": "bytes32"
			},
			{
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "merkleRoot",
				"type": "bytes32"
			},
			{
				"internalType": "uint8",
				"name": "claimRecordID",
				"type": "uint8"
			},
			{
				"internalType": "uint8",
				"name": "uriID",
				"type": "uint8"
			}
		],
		"name": "getStorageMetadataURIs",
		"outputs": [
			{
				"internalType": "uint8",
				"name": "fileSetExtensionMarker",
				"type": "uint8"
			},
			{
				"internalType": "uint8",
				"name": "schemeID",
				"type": "uint8"
			},
			{
				"internalType": "uint16",
				"name": "authorityID",
				"type": "uint16"
			},
			{
				"internalType": "bytes32",
				"name": "path",
				"type": "bytes32"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			}
		],
		"name": "linkRegistry",
		"outputs": [
			{
				"internalType": "bytes32",
				"name": "merkleRoot",
				"type": "bytes32"
			},
			{
				"internalType": "address",
				"name": "linkIssuer",
				"type": "address"
			},
			{
				"internalType": "bytes32",
				"name": "parentLinkID",
				"type": "bytes32"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint8",
				"name": "",
				"type": "uint8"
			}
		],
		"name": "mimeTypeRegistry",
		"outputs": [
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "nMimeTypeRegistry",
		"outputs": [
			{
				"internalType": "uint8",
				"name": "",
				"type": "uint8"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "nUriAuthorityRegistry",
		"outputs": [
			{
				"internalType": "uint16",
				"name": "",
				"type": "uint16"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "nUriSchemeRegistry",
		"outputs": [
			{
				"internalType": "uint8",
				"name": "",
				"type": "uint8"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "linkID",
				"type": "bytes32"
			}
		],
		"name": "resolveLink",
		"outputs": [
			{
				"internalType": "bytes32",
				"name": "merkleRoot",
				"type": "bytes32"
			},
			{
				"internalType": "address",
				"name": "linkIssuer",
				"type": "address"
			},
			{
				"internalType": "bytes32",
				"name": "parentLinkID",
				"type": "bytes32"
			},
			{
				"internalType": "uint8",
				"name": "nClaimRecords",
				"type": "uint8"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "mimeType",
				"type": "bytes32"
			}
		],
		"name": "retrieveMimeTypeIndex",
		"outputs": [
			{
				"internalType": "uint8",
				"name": "",
				"type": "uint8"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "uriAuthority",
				"type": "bytes32"
			}
		],
		"name": "retrieveUriAuthorityIndex",
		"outputs": [
			{
				"internalType": "uint16",
				"name": "",
				"type": "uint16"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "uriScheme",
				"type": "bytes32"
			}
		],
		"name": "retrieveUriSchemeIndex",
		"outputs": [
			{
				"internalType": "uint8",
				"name": "",
				"type": "uint8"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint16",
				"name": "",
				"type": "uint16"
			}
		],
		"name": "uriAuthorityRegistry",
		"outputs": [
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint8",
				"name": "",
				"type": "uint8"
			}
		],
		"name": "uriSchemeRegistry",
		"outputs": [
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "merkleRoot",
				"type": "bytes32"
			},
			{
				"internalType": "uint8",
				"name": "claimRecordID",
				"type": "uint8"
			},
			{
				"internalType": "bytes32",
				"name": "merkleRootPrime",
				"type": "bytes32"
			}
		],
		"name": "validateClaim",
		"outputs": [
			{
				"internalType": "bool",
				"name": "attestationResultValid",
				"type": "bool"
			},
			{
				"internalType": "address",
				"name": "claimIssuer",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "blockTimestamp",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
