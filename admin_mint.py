import os
import requests
from web3 import Web3

# ==========================================
# 1. KONFIGURASI IPFS (PINATA)
# ==========================================
PINATA_API_KEY = " "
PINATA_SECRET_KEY = " "

# ==========================================
# 2. KONFIGURASI WEB3 (BLOCKCHAIN)
# ==========================================
# Sambung ke Localhost Anvil
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Dompet Rektor (Pakai Private Key Anvil No. 0)
PRIVATE_KEY = " "
REKTOR_WALLET = w3.eth.account.from_key(PRIVATE_KEY).address

# PASTE ALAMAT DEPLOY SMART CONTRACT LO DI SINI
ALAMAT_KONTRAK = w3.to_checksum_address(" ")

# Kamus Fungsi (ABI) untuk issueCertificate
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
# 3. FUNGSI UPLOAD KE IPFS
# ==========================================
def upload_to_ipfs(file_path):
    print(f"\n[1/2] Mengunggah '{file_path}' ke jaringan IPFS via Pinata...")
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {"pinata_api_key": PINATA_API_KEY, "pinata_secret_api_key": PINATA_SECRET_KEY}
    
    with open(file_path, 'rb') as file:
        response = requests.post(url, files={'file': file}, headers=headers)
        if response.status_code == 200:
            ipfs_hash = response.json()['IpfsHash']
            print(f"File Mendarat di IPFS! CID: {ipfs_hash}")
            return ipfs_hash
        else:
            print("GAGAL UPLOAD IPFS.")
            return None

# ==========================================
# 4. FUNGSI MINTING NFT KE BLOCKCHAIN
# ==========================================
def mint_certificate(student_wallet, nim, ipfs_hash):
    print(f"[2/2] Mempersiapkan Transaksi Blockchain untuk NIM: {nim}...")
    document_uri = f"ipfs://{ipfs_hash}"
    student_address = w3.to_checksum_address(student_wallet)

    # Rakit Peluru
    nonce = w3.eth.get_transaction_count(REKTOR_WALLET)
    tx = cert_contract.functions.issueCertificate(
        student_address,
        int(nim),
        document_uri
    ).build_transaction({
        'chainId': 31337, # Chain ID standar Anvil Localhost
        'gas': 2000000,
        'gasPrice': w3.to_wei('50', 'gwei'),
        'nonce': nonce,
    })

    # Tanda tangan & Tembak!
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    print("\n=========================================")
    print(f"SAH! IJAZAH DIGITAL RESMI DITERBITKAN! 🎓")
    print(f"Hash Transaksi : {w3.to_hex(tx_hash)}")
    print(f"Dompet Tujuan  : {student_address}")
    print("=========================================\n")

# ==========================================
# 5. MESIN UTAMA (CLI INTERAKTIF)
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🎓 SISTEM PENERBITAN IJAZAH NFT JABIR 🎓")
    print("="*50)

    while True:
        file_target = input("\n1. Masukkan nama file Ijazah (atau ketik 'exit'): ")
        if file_target.lower() == 'exit':
            break

        if os.path.exists(file_target):
            nim_input = input("2. Masukkan NIM Mahasiswa (contoh: 240511067): ")
            
            # Kita pinjem Dompet Anvil No. 1 buat jadi dompet mahasiswa (address dummy)
            default_student = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
            wallet_input = input(f"3. Masukkan Dompet Mahasiswa (Enter untuk default {default_student}): ")
            if wallet_input.strip() == "":
                wallet_input = default_student

            # --- EKSEKUSI FULL AUTOMATIS ---
            hash_ipfs = upload_to_ipfs(file_target)
            if hash_ipfs:
                mint_certificate(wallet_input, nim_input, hash_ipfs)
        else:
            print(f"ERROR: File '{file_target}' gak ketemu di laptop lo!")