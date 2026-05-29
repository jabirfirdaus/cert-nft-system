import os
import json
import uuid
import requests
from web3 import Web3
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)
load_dotenv()

PINATA_API_KEY    = os.getenv("PINATA_API_KEY")
PINATA_SECRET_KEY = os.getenv("PINATA_SECRET_KEY")
ALCHEMY_URL       = os.getenv("ALCHEMY_URL")
PRIVATE_KEY       = os.getenv("PRIVATE_KEY")

w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))

REKTOR_WALLET  = w3.eth.account.from_key(PRIVATE_KEY).address
ALAMAT_KONTRAK = w3.to_checksum_address("0xd1eD6112A65492a761C8Fe68666a1f8cd32e49A0")
NAMA_KAMPUS    = "Universitas Muhammadiyah Cirebon"

cert_abi = [
    {
        "inputs": [
            {"internalType": "address", "name": "studentWallet", "type": "address"},
            {"internalType": "uint256", "name": "certificateId", "type": "uint256"},
            {"internalType": "string",  "name": "documentURI",   "type": "string"}
        ],
        "name": "issueCertificate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "certificateId", "type": "uint256"}],
        "name": "verifyOwner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "certificateId", "type": "uint256"}],
        "name": "getCertificateData",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    }
]
cert_contract = w3.eth.contract(address=ALAMAT_KONTRAK, abi=cert_abi)


def upload_file_to_ipfs(file_path):
    url     = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key":        PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_KEY
    }
    with open(file_path, 'rb') as f:
        res = requests.post(url, files={'file': f}, headers=headers)
    if res.status_code == 200:
        return res.json()['IpfsHash']
    raise Exception(f"Gagal upload file ke IPFS: {res.text}")


def upload_json_to_ipfs(data: dict):
    url     = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    headers = {
        "pinata_api_key":        PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_KEY,
        "Content-Type":          "application/json"
    }
    res = requests.post(url, json={"pinataContent": data}, headers=headers)
    if res.status_code == 200:
        return res.json()['IpfsHash']
    raise Exception(f"Gagal upload JSON ke IPFS: {res.text}")


def fetch_metadata_from_ipfs(cid: str):
    url = f"https://gateway.pinata.cloud/ipfs/{cid}"
    res = requests.get(url, timeout=10)
    if res.status_code == 200:
        return res.json()
    return None


def mint_certificate(student_wallet, nim, metadata_cid):
    document_uri    = f"ipfs://{metadata_cid}"
    student_address = w3.to_checksum_address(student_wallet)
    nonce           = w3.eth.get_transaction_count(REKTOR_WALLET)
    gas_price       = w3.eth.gas_price

    tx = cert_contract.functions.issueCertificate(
        student_address, int(nim), document_uri
    ).build_transaction({
        'chainId':  11155111,
        'gas':      500000,
        'gasPrice': gas_price,
        'nonce':    nonce,
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash   = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return w3.to_hex(tx_hash)


@app.route('/api/terbitkan', methods=['POST'])
def terbitkan_api():
    file   = request.files.get('fileIjazah')
    nim    = request.form.get('nimMahasiswa')
    wallet = request.form.get('dompetMahasiswa')
    nama   = request.form.get('namaMahasiswa')

    if not all([file, nim, wallet, nama]):
        return jsonify({"status": "error", "pesan": "Data tidak lengkap!"}), 400

    safe_filename = f"temp_{uuid.uuid4().hex}_{os.path.basename(file.filename)}"
    file.save(safe_filename)

    try:
        doc_cid = upload_file_to_ipfs(safe_filename)

        metadata = {
            "nama":         nama,
            "nim":          nim,
            "institusi":    NAMA_KAMPUS,
            "document_cid": doc_cid,
            "document_url": f"https://gateway.pinata.cloud/ipfs/{doc_cid}"
        }
        metadata_cid = upload_json_to_ipfs(metadata)

        tx_hash = mint_certificate(wallet, nim, metadata_cid)

        os.remove(safe_filename)

        return jsonify({
            "status":         "sukses",
            "pesan":          "Ijazah Berhasil Diterbitkan!",
            "metadata_cid":   metadata_cid,
            "doc_cid":        doc_cid,
            "hash_transaksi": tx_hash
        }), 200

    except Exception as e:
        if os.path.exists(safe_filename):
            os.remove(safe_filename)
        return jsonify({"status": "error", "pesan": str(e)}), 500


@app.route('/api/verifikasi/<int:nim>', methods=['GET'])
def verifikasi_api(nim):
    try:
        owner_wallet = cert_contract.functions.verifyOwner(nim).call()
        document_uri = cert_contract.functions.getCertificateData(nim).call()

        metadata_cid = document_uri.replace("ipfs://", "")
        metadata     = fetch_metadata_from_ipfs(metadata_cid)

        if not metadata:
            return jsonify({
                "status":        "sukses",
                "pesan":         "Sertifikat Asli Ditemukan!",
                "nama":          "Data lama (tidak tersedia)",
                "nim":           str(nim),
                "institusi":     NAMA_KAMPUS,
                "pemilik":       owner_wallet,
                "doc_url":       f"https://gateway.pinata.cloud/ipfs/{metadata_cid}",
                "etherscan_url": f"https://sepolia.etherscan.io/address/{owner_wallet}"
            }), 200

        return jsonify({
            "status":        "sukses",
            "pesan":         "Sertifikat Asli Ditemukan!",
            "nama":          metadata.get("nama", "-"),
            "nim":           metadata.get("nim", str(nim)),
            "institusi":     metadata.get("institusi", NAMA_KAMPUS),
            "pemilik":       owner_wallet,
            "doc_url":       metadata.get("document_url", ""),
            "doc_cid":       metadata.get("document_cid", ""),
            "etherscan_url": f"https://sepolia.etherscan.io/address/{owner_wallet}"
        }), 200

    except Exception as e:
        print(f"ERROR VERIFIKASI: {str(e)}")
        return jsonify({
            "status": "error",
            "pesan":  "Sertifikat Palsu atau NIM Tidak Terdaftar!"
        }), 404


if __name__ == '__main__':
    print(f"Server aktif -> http://localhost:5000")
    app.run(port=5000, debug=True)
