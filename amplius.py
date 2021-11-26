import sys
import uuid
import getopt

from amplius import attestation_controller
from amplius import transfer_controller
from amplius import identity_controller

def print_usage():
    print("Usage: amplius.py <command> [argument]*")
    print("")
    print("Amplius a user interface for creating and verifying attested multi-protocol links (AMPL). The prototype supports the transfer clients IPFS, Git, and HTTP.")
    print("")
    print("<command> is one of the following attestation, identity_acc, or transfer commands.")
    print("")
    print("Attestation Commands:")
    print("--attest [file]*                     create an identity if none is present, distribute all files, issue a content-based claim")
    print("--issue-claim [uri]*                 issue a content-based claim for all files retrievable under the given URIs")
    print("--link=UUID <merkle-root> [p]        create a link with a new UUID v4 as ID pointing to claim <merkle-root>, parent link ID <p>")
    print("--link=<link-id> <merkle-root> [p]   create a link <link-id> pointing to the claim <merkle-root> with parent link ID <p>")
    print("--resolve=<link-id>                  resolve the claim Merkle root linked by <link-id>")
    print("--retrieve <merkle-root> <record-id> retrieve data of the claim identified by <merkle-root>, <record-id>")
    print("--validate-claim [file]*             validate a claim using the Merkle root of all files")
    print("--validate-claim=<record-id> [file]* validate a claim under the specified record ID using the Merkle root of all files")
    print("--validate-claim=<issuer> [file]*    validate claims issued by account address <issuer> with all given files")
    print("")
    print("Identity Commands:")
    print("--eth-account-new                    create an identity for attestations")
    print("--eth-account-show                   show the current identity for attestations")
    print("")
    print("Transfer Commands:")
    print("--distribute [file]*                 distribute all files using all transfer clients with example repositores")
    print("--distribute=ipfs [file]*            add files to IPFS and pin at a remote node")
    print("--distribute=<GIT_URL> [file]*       commit and push all files with Git to <GIT_URL> starting with git or http and ending in .git")
    print("--distribute=<HTTP_URL> [file]*      send all files with HTTP PUT requests to <HTTP_URL> starting with http")
    print("--retrieve <URI>                     retrieve all files from an ipfs, git, or HTTP <URI>")
    sys.exit()

def attest(files):
    identity_acc = identity_controller.get_identity()
    if len(identity_acc.address) < 40:
        identity_eth_account_new()
    addresses_by_file_set = distribute(files)
    issue_claim(files, addresses_by_file_set)

def retrieve_claim(merkle_root, record_id_arg):
    identity_acc = identity_controller.get_identity()
    record_id = 1
    if isinstance(record_id_arg, int) or record_id_arg.isnumeric():
        record_id = int(record_id_arg)
    else:
        print("Error: record ID is not numeric")
        sys.exit()
    (mime, ts, claim_issuer, ext_id, addr_by_file_set) = attestation_controller.retrieve(identity_acc, merkle_root, record_id)
    
    print("\nAttestation Claim\n")
    print_claim_record(mime, ts, claim_issuer, ext_id, addr_by_file_set)
    print()

    print("\nRetrieving Files\n")
    file_sets = []
    for file_set_i in range(len(addr_by_file_set)):
        for storage_i in range(len(addr_by_file_set[file_set_i])):
            uri = addr_by_file_set[file_set_i][storage_i]
            t_file_set = transfer_controller.retrieve(uri)
            print("FS", t_file_set)
            file_sets.append(t_file_set)
    
    for file_set in file_sets:
        print("FS", file_set)
        validate_claim(record_id, file_set)

def print_claim_record(mime, ts, claim_issuer, ext_id, addr_by_file_set):
    print("Timestamp            ", ts, sep="")
    print("Claim Issuer         ", claim_issuer, sep="")
    print("MIME type            ", mime, sep="")
    print()
    for file_set_i in range(len(addr_by_file_set)):
        #print("Storage Entry    ", str(file_set_i+1), sep="")
        for storage_i in range(len(addr_by_file_set[file_set_i])):
            uri = addr_by_file_set[file_set_i][storage_i]
            print("Storage MD ", str(file_set_i+1), ", URI ", str(storage_i+1), "  ", uri, sep="")

def issue_claim(files, addresses_by_file_set):
    identity_acc = identity_controller.get_identity()
    if len(identity_acc.address) < 40:
        print("Error: claim issuer identity account address not set")
        sys.exit()
    attestation_controller.issue_claim(identity_acc, files, addresses_by_file_set)

def issue_claim_from_uris(uris):
    addresses_by_file_set = []
    files = []
    for uri in uris:
        # each URI is one address of the file set
        address = [ uri ]
        addresses_by_file_set.append(address)
        # retrieve file
        files.extend(transfer_controller.retrieve(uri))
    
    print("\n\nFiles retrieved:\n")
    print(files)
    issue_claim(files, addresses_by_file_set)


def resolve_link(link_arg):
    link_id = link_arg

    identity_acc = identity_controller.get_identity()
    (merkle_root, link_issuer, parent_link_id, n_records) = attestation_controller.resolve_link(identity_acc, link_id)
    print("Merkle root:", merkle_root)
    print("Link issuer:", link_issuer)
    print("Parent link ID:", parent_link_id)    
    print("Number of records:", n_records)

    print("\n\nClaim records issued by link issuer:\n")
    for record_id in range(1, n_records+1):
        (mime, ts, claim_issuer, ext_id, addr_by_file_set) = attestation_controller.retrieve(identity_acc, merkle_root, record_id)
        if link_issuer == claim_issuer:
            print("\nClaim Record         ", record_id, sep="")
            print("Merkle Root          ", merkle_root, sep="")
            print_claim_record(mime, ts, claim_issuer, ext_id, addr_by_file_set)
            print()

    print("\n\nClaim records issued by third parties:\n")
    for record_id in range(1, n_records+1):
        (mime, ts, claim_issuer, ext_id, addr_by_file_set) = attestation_controller.retrieve(identity_acc, merkle_root, record_id)
        if link_issuer != claim_issuer:
            print("\nClaim Record         ", record_id, sep="")
            print("Merkle Root          ", merkle_root, sep="")
            print_claim_record(mime, ts, claim_issuer, ext_id, addr_by_file_set)
            print()


def link(l_arg, merkle_root, parent_link_id):
    identity_acc = identity_controller.get_identity()
    link_id = l_arg
    if l_arg == "UUID":
        link_uuid = uuid.uuid4()
        link_id = "0x" + bytes.hex(link_uuid.bytes)
        print("UUID:", link_uuid)
    elif len(link_id) < 5 or len(link_id) > 32:
        print("Link ID length out of range (5-32 characters)")
        sys.exit()
    attestation_controller.link(identity_acc, link_id, merkle_root, parent_link_id)

def validate_claim(id_arg, files):
    record_id = id_arg
    issuer_addr = ""
    if isinstance(id_arg, int) or id_arg.isnumeric():
        record_id = int(id_arg)
    elif id_arg.startswith("0x"):
        issuer_addr = id_arg
    else:
        record_id = 1
    
    identity_acc = identity_controller.get_identity()

    print("Validating claim ...", sep="")

    if len(issuer_addr) > 0:
        (merkle_root, claim_validation_result) = attestation_controller.validate_claim_issuer(identity_acc, files, issuer_addr)
        (is_valid, ci_account_address, timestamp) = claim_validation_result
        print("\nClaim validation result for Merkle root 0x", merkle_root.hex(), ", issuer ", issuer_addr, ":\n", sep="")
        print("Validity:", is_valid)
        print("Claim Issuer Account Address:", ci_account_address)
        print("Timestamp:", timestamp)
        print()

    else:
        (merkle_root, claim_validation_result)  = attestation_controller.validate_claim(identity_acc, files, record_id)
        (is_valid, ci_account_address, timestamp) = claim_validation_result
        print("\nClaim validation result for Merkle root 0x", merkle_root.hex(), ", record ID ", record_id, ":\n", sep="")
        print("Validity:", is_valid)
        print("Claim Issuer Account Address:", ci_account_address)
        print("Timestamp:", timestamp)
        print()

def identity_eth_account_show():
    identity_acc = identity_controller.get_identity()
    print("Address:", identity_acc.address)

def identity_eth_account_new():
    identity_acc = identity_controller.create_identity()
    print("Address:", identity_acc.address)

def distribute(files):
    addresses_http = distribute_http("http://x/amplius/", files)
    addresses_git = distribute_git("https://github.com/fhaer/ampl-case-study-5.git", files)
    addresses_ipfs = distribute_ipfs(files)
    addresses_by_file_set = [ addresses_http, addresses_git, addresses_ipfs ]
    print("Addresses by file set:")
    print(addresses_by_file_set)
    return addresses_by_file_set

def distribute_ipfs(files):
    addresses = transfer_controller.distribute_ipfs(files)
    return addresses

def distribute_git(url, files):
    addresses = transfer_controller.distribute_git(url, files)
    return addresses

def distribute_http(url, files):
    addresses = transfer_controller.distribute_http(url, files)
    return addresses

def retrieve_files(uri):
    transfer_controller.retrieve(uri)

def parse_cli():

    try:
        opts, args = getopt.getopt(sys.argv[1:], "arivedighf", 
            ["attest", "link=", "retrieve=", "resolve=", "issue-claim", "validate-claim=",
            "eth-account-new", "eth-account-show", "distribute="])
    except getopt.GetoptError as err:
        print(err)
        print_usage()

    if len(opts) < 1:
        print_usage()

    for o, a in opts:
        if o in ("-a", "--attest"):
            attest(args)
        elif o in ("-r", "--retrieve"):
            if len(args) == 1:
                merkle_root = a
                record_id = args[0]
                retrieve_claim(merkle_root, record_id)
            elif len(args) == 0:
                uri = a
                retrieve_files(uri)

        elif o in ("--resolve"):
            link_id = a
            resolve_link(a)
        elif o in ("-l", "--link"):
            link_id = a
            if len(args) == 2:
                merkle_root = args[0]
                parent_link_id = args[1]
                link(link_id, merkle_root, parent_link_id)
            elif len(args) == 1:
                merkle_root = args[0]
                link(link_id, merkle_root, "")
            else:
                print("Merkle root missing")
        elif o in ("-i", "--issue-claim"):
            issue_claim_from_uris(args)
        elif o in ("-v", "--validate-claim"):
            id_arg = a
            files = args
            if not id_arg.isnumeric() and not id_arg.startswith("0x"):
                files.append(id_arg)
            validate_claim(id_arg, files)
        elif o in ("-e", "--eth-account-show"):
            identity_eth_account_show()
        elif o in ("-e", "--eth-account-new"):
            identity_eth_account_new()
        elif o in ("-d", "--distribute"):
            uri = a
            if uri.startswith("git") or (uri.startswith("http") and uri.endswith(".git")):
                distribute_git(uri, args)
            elif uri.startswith("http"):
                distribute_http(uri, args)
            elif uri == "ipfs":
                distribute_ipfs(args)
            else:
                distribute(args)
        else:
            print_usage()

parse_cli()
