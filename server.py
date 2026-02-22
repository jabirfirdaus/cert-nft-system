import os
import requests
from web3 import Web3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Mengizinkan Frontend HTML ngobrol sama server ini

# ==========================================
# 1. KONFIGURASI IPFS & WEB3
# ==========================================
PINATA_API_KEY = " "
PINATA_SECRET_KEY = " "

w3 = Web3(Web3.HTTPProvider("https://eth-sepolia.g.alchemy.com/v2/3Hqma1gJQiIPesucX5YAi"))

PRIVATE_KEY = " "
REKTOR_WALLET = w3.eth.account.from_key(PRIVATE_KEY).address
ALAMAT_KONTRAK = w3.to_checksum_address("0xd1eD6112A65492a761C8Fe68666a1f8cd32e49A0")

cert_abi = [
    {
        "inputs": [
            {"internalType": "address", "name": "studentWallet", "type": "address"},
            {"internalType": "uint256", "name": "certificateId", "type": "uint256"},
            {"internalType": "string", "name": "documentURI", "type": "string"}
        ],
        "name": "issueCertificate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
cert_contract = w3.eth.contract(address=ALAMAT_KONTRAK, abi=cert_abi)

# ==========================================
# 2. FUNGSI CORE (Sama kayak tadi, cuma gue rapihin return-nya)
# ==========================================
def upload_to_ipfs(file_path):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {"pinata_api_key": PINATA_API_KEY, "pinata_secret_api_key": PINATA_SECRET_KEY}
    with open(file_path, 'rb') as file:
        res = requests.post(url, files={'file': file}, headers=headers)
        if res.status_code == 200:
            return res.json()['IpfsHash']
    return None

def mint_certificate(student_wallet, nim, ipfs_hash):
    document_uri = f"ipfs://{ipfs_hash}"
    student_address = w3.to_checksum_address(student_wallet)
    nonce = w3.eth.get_transaction_count(REKTOR_WALLET)
    
    # 1. Suruh Python ngecek harga bensin pasar saat ini secara otomatis
    harga_bensin_sekarang = w3.eth.gas_price
    
    # 2. Rakit peluru dengan bensin hemat
    tx = cert_contract.functions.issueCertificate(student_address, int(nim), document_uri).build_transaction({
        'chainId': 11155111, # Tetap ID Sepolia
        'gas': 500000,       
        'gasPrice': harga_bensin_sekarang, # Pake harga pasar, jangan hardcode!
        'nonce': nonce,
    })
    
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return w3.to_hex(tx_hash)
    
# ==========================================
# 3. JEMBATAN API UNTUK FRONTEND
# ==========================================
@app.route('/api/terbitkan', methods=['POST'])
def terbitkan_api():
    # Frontend bakal ngirim file dan data ke endpoint ini
    file = request.files.get('fileIjazah')
    nim = request.form.get('nimMahasiswa')
    wallet = request.form.get('dompetMahasiswa')

    if not file or not nim or not wallet:
        return jsonify({"status": "error", "pesan": "Data tidak lengkap!"}), 400

    # Simpan file sementara di laptop buat di-upload
    temp_filename = file.filename
    file.save(temp_filename)

    try:
        # 1. Upload IPFS
        hash_ipfs = upload_to_ipfs(temp_filename)
        if not hash_ipfs:
            raise Exception("Gagal Pinata IPFS")

        # 2. Cetak ke Blockchain
        tx_hash = mint_certificate(wallet, nim, hash_ipfs)

        # Hapus file sementara biar laptop lo gak penuh
        os.remove(temp_filename)

        return jsonify({
            "status": "sukses",
            "pesan": "Ijazah Berhasil Diterbitkan!",
            "ipfs": hash_ipfs,
            "hash_transaksi": tx_hash
        }), 200

    except Exception as e:
        if os.path.exists(temp_filename): os.remove(temp_filename)
        return jsonify({"status": "error", "pesan": str(e)}), 500

if __name__ == '__main__':
    print("API Backend Server Menyala di http://localhost:5000")
    app.run(port=5000, debug=True)
