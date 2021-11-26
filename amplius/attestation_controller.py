import sys

from .attestation import attestation_node
from .attestation import merkle_tree_hashing
from .attestation import data_coding

def issue_claim(identity, file_set, addresses_by_file_set):

    w3a = attestation_node.Web3Attestation(identity)
    if not w3a.w3.isConnected():
        print("web3 not connected, exiting")
        sys.exit()

    merkle_root = merkle_tree_hashing.calculate_merkle_root(file_set)
    mime_type = data_coding.get_mime_type(file_set)
    mime_type_id = w3a.register_mime_type(mime_type)
    #external_DID = ""

    uri_scheme_IDs = []
    uri_authority_IDs = []
    uri_paths = []
    file_set_ext_marker = []

    # for each file set located in the storage network
    for file_set_addresses in addresses_by_file_set:

        n_file_set_addresses = len(file_set_addresses)

        # for each address in a file set (pointing to a partial file, one file, or multiple files)
        for i in range(n_file_set_addresses):

            (s, a, p) = data_coding.parse_uri(file_set_addresses[i])
            (s_id, a_id) = w3a.register_uri_scheme_authority(s, a)

            if s == 'ipfs':
                p = data_coding.encode_cid_bytes32(p)
                print(p)

            path_parts = data_coding.split_path(p, 32)
            n_path_parts = len(path_parts)

            for j in range(n_path_parts):

                file_set_ext_marker_int = int(i != 0)
                file_set_ext_marker_int = file_set_ext_marker_int << 1
                file_set_ext_marker_int |= int(j > 0)

                uri_scheme_IDs.append(s_id)
                uri_authority_IDs.append(a_id)
                uri_paths.append(path_parts[j])

                file_set_ext_marker.append(file_set_ext_marker_int)

    print(uri_scheme_IDs)    
    w3a.issue_claim(merkle_root, uri_scheme_IDs, uri_authority_IDs, uri_paths, file_set_ext_marker, mime_type_id)

def link(identity, link_id, merkle_root, parent_link_id):

    w3a = attestation_node.Web3Attestation(identity)

    if not w3a.w3.isConnected():
        print("web3 not connected, exiting")
        sys.exit()

    w3a.link(link_id, merkle_root, parent_link_id)

def resolve_link(identity, link_id):

    w3a = attestation_node.Web3Attestation(identity)

    if not w3a.w3.isConnected():
        print("web3 not connected, exiting")
        sys.exit()

    return w3a.resolve_link(link_id)

def retrieve(identity, merkle_root, record_id):

    w3a = attestation_node.Web3Attestation(identity)

    if not w3a.w3.isConnected():
        print("web3 not connected, exiting")
        sys.exit()

    addresses_by_file_set = []

    (mime, ts) = w3a.get_storage_metadata(merkle_root, record_id)
    (claim_issuer, ext_id) = w3a.get_issuer_metadata(merkle_root, record_id)

    uri_id = 0
    has_uri = True

    scheme_cache = ""
    authority_cache = ""

    while has_uri:

        (file_set_ext_marker, sh_id, auth_id, path_b) = w3a.get_storage_metadata_uris(merkle_root, record_id, uri_id)

        scheme = w3a.get_uri_schema(sh_id)
        authority = w3a.get_uri_authority(auth_id)
        
        path = ""
        if scheme == 'ipfs':
            path = data_coding.decode_cid_bytes32(path_b)
        else:
            path = data_coding.decode_str_bytes32(path_b)

        has_uri = len(path_b.rstrip(b'\x00')) > 0

        if has_uri:

            if sh_id == 0:
                scheme = scheme_cache
            if auth_id == 0:
                authority = authority_cache

            is_file_set = (file_set_ext_marker >> 1) == 0
            is_ext = (file_set_ext_marker & 1) == 1

            if is_file_set and not is_ext:
                # create file set with first URI
                file_set = [ data_coding.construct_uri(scheme, authority, path) ]
                addresses_by_file_set.append(file_set)
            elif not is_file_set and not is_ext:
                # add additional address to file set
                if len(addresses_by_file_set) > 0:
                    addresses_by_file_set[-1].append( data_coding.construct_uri(scheme, authority, path) )
            elif not is_file_set and is_ext:
                # extend existing path entry
                if len(addresses_by_file_set) > 0 and len(addresses_by_file_set[-1] > 0):
                    addresses_by_file_set[-1][-1] += path

            scheme_cache = scheme
            authority_cache = authority
            uri_id += 1

    return (mime, ts, claim_issuer, ext_id, addresses_by_file_set)

def validate_claim(identity, files, record_id):

    merkle_root = merkle_tree_hashing.calculate_merkle_root(files)

    w3a = attestation_node.Web3Attestation(identity)

    if not w3a.w3.isConnected():
        print("web3 not connected, exiting")
        sys.exit()

    claim_validation_result = w3a.validate_claim(merkle_root, record_id)
    
    return (merkle_root, claim_validation_result)

def validate_claim_issuer(identity, files, issuer_addr):

    merkle_root = merkle_tree_hashing.calculate_merkle_root(files)

    w3a = attestation_node.Web3Attestation(identity)
    
    if not w3a.w3.isConnected():
        print("web3 not connected, exiting")
        sys.exit()

    n_claim_records = w3a.get_n_claim_records(merkle_root)

    for i in range(n_claim_records, -1, -1):

        (is_valid, ci_account_address, timestamp) = w3a.validate_claim(merkle_root, i)

        if ci_account_address == issuer_addr:
            claim_validation_result = (is_valid, ci_account_address, timestamp)
            return (merkle_root, claim_validation_result)

    claim_validation_result = (False, issuer_addr, 0)
    return (merkle_root, claim_validation_result)
