import os
import uuid
import json
import requests
from datetime import datetime
from web3 import Web3
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# ============================================================
# IjazahChain — Backend API Server v2.0
# Author  : Jabir Firdaus
# GitHub  : github.com/jabirfirdaus
# ============================================================

app = Flask(__name__)
CORS(app)
load_dotenv()

# ==========================================
# KONFIGURASI — Baca dari .env
# ==========================================
PINATA_API_KEY    = os.getenv("PINATA_API_KEY")
PINATA_SECRET_KEY = os.getenv("PINATA_SECRET_KEY")
ALCHEMY_URL       = os.getenv("ALCHEMY_URL", "https://eth-sepolia.g.alchemy.com/v2/3Hqma1gJQiIPesucX5YAi")
PRIVATE_KEY       = os.getenv("PRIVATE_KEY")
ALAMAT_KONTRAK    = os.getenv("ALAMAT_KONTRAK", "0xd1eD6112A65492a761C8Fe68666a1f8cd32e49A0")

# ==========================================
# DETEKSI VERSI CONTRACT (V1 lama vs V2 baru)
# ==========================================
# V1 (deployed): issueCertificate(address, uint256, string)  → NIM sebagai ID
# V2 (baru)    : issueCertificate(string, uint256, address, string, string) → nama + foto
#
# Kita default ke V1 jika contract address yang dipakai adalah address lama,
# dan V2 jika sudah di-deploy ulang.
#
# Cara override: tambahkan CONTRACT_VERSION=2 di .env

CONTRACT_VERSION = int(os.getenv("CONTRACT_VERSION", "1"))

# ABI V1 (contract lama yang sudah deployed)
cert_abi_v1 = [
    {
        "inputs": [
            {"internalType": "address", "name": "studentWallet", "type": "address"},
            {"internalType": "uint256", "name": "certificateId",  "type": "uint256"},
            {"internalType": "string",  "name": "documentURI",    "type": "string"}
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

# ABI V2 (contract baru dengan field nama + foto)
cert_abi_v2 = [
    {
        "inputs": [
            {"internalType": "string",  "name": "namaMahasiswa", "type": "string"},
            {"internalType": "uint256", "name": "nim",           "type": "uint256"},
            {"internalType": "address", "name": "walletAddr",    "type": "address"},
            {"internalType": "string",  "name": "ipfsHash",      "type": "string"},
            {"internalType": "string",  "name": "fotoIpfsHash",  "type": "string"}
        ],
        "name": "issueCertificate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "nim", "type": "uint256"}],
        "name": "verifyCertificate",
        "outputs": [
            {"internalType": "string",  "name": "namaMahasiswa",  "type": "string"},
            {"internalType": "uint256", "name": "nimResult",       "type": "uint256"},
            {"internalType": "address", "name": "walletMahasiswa", "type": "address"},
            {"internalType": "string",  "name": "ipfsHash",        "type": "string"},
            {"internalType": "string",  "name": "fotoIpfsHash",    "type": "string"},
            {"internalType": "uint256", "name": "tanggalTerbit",   "type": "uint256"},
            {"internalType": "bool",    "name": "isValid",          "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalIssued",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# ==========================================
# KONEKSI WEB3
# ==========================================
w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))
REKTOR_WALLET = w3.eth.account.from_key(PRIVATE_KEY).address

cert_abi = cert_abi_v2 if CONTRACT_VERSION == 2 else cert_abi_v1
cert_contract = w3.eth.contract(
    address=w3.to_checksum_address(ALAMAT_KONTRAK),
    abi=cert_abi
)

print(f"[IjazahChain] Contract V{CONTRACT_VERSION} di {ALAMAT_KONTRAK}")
print(f"[IjazahChain] Admin Wallet: {REKTOR_WALLET}")

# ==========================================
# HELPER: Upload File ke Pinata IPFS
# ==========================================
def upload_to_ipfs(file_path, filename="file"):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_KEY
    }
    try:
        with open(file_path, 'rb') as f:
            res = requests.post(url, files={'file': (filename, f)}, headers=headers, timeout=30)
        if res.status_code == 200:
            return res.json()['IpfsHash']
        else:
            print(f"[IPFS ERROR] {res.status_code}: {res.text}")
            return None
    except Exception as e:
        print(f"[IPFS EXCEPTION] {e}")
        return None

# ==========================================
# HELPER: Mint ke Blockchain (V1 — contract lama)
# ==========================================
def mint_v1(nim, wallet_addr, ipfs_uri):
    """V1: issueCertificate(address wallet, uint256 nim, string uri)"""
    student_address = w3.to_checksum_address(wallet_addr)
    nonce     = w3.eth.get_transaction_count(REKTOR_WALLET)
    gas_price = w3.eth.gas_price

    tx = cert_contract.functions.issueCertificate(
        student_address,
        int(nim),
        ipfs_uri
    ).build_transaction({
        'chainId': 11155111,
        'gas': 500000,
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    signed = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return w3.to_hex(tx_hash)

# ==========================================
# HELPER: Mint ke Blockchain (V2 — contract baru)
# ==========================================
def mint_v2(nama, nim, wallet_addr, ipfs_hash, foto_hash):
    """V2: issueCertificate(string nama, uint256 nim, address wallet, string meta, string foto)"""
    student_address = w3.to_checksum_address(wallet_addr)
    nonce     = w3.eth.get_transaction_count(REKTOR_WALLET)
    gas_price = w3.eth.gas_price

    tx = cert_contract.functions.issueCertificate(
        nama, int(nim), student_address, ipfs_hash, foto_hash
    ).build_transaction({
        'chainId': 11155111,
        'gas': 500000,
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    signed = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return w3.to_hex(tx_hash)

# ==========================================
# ENDPOINT 1: TERBITKAN IJAZAH
# POST /api/terbitkan
# ==========================================
@app.route('/api/terbitkan', methods=['POST'])
def terbitkan_api():
    file   = request.files.get('fileIjazah')
    nama   = request.form.get('namaMahasiswa', '').strip()
    nim    = request.form.get('nimMahasiswa',  '').strip()
    wallet = request.form.get('dompetMahasiswa', '').strip()

    # Validasi
    if not file:
        return jsonify({"status": "error", "pesan": "File ijazah wajib diupload!"}), 400
    if not nama:
        return jsonify({"status": "error", "pesan": "Nama mahasiswa wajib diisi!"}), 400
    if not nim or not nim.isdigit():
        return jsonify({"status": "error", "pesan": "NIM wajib diisi dan harus berupa angka!"}), 400
    if not wallet or not wallet.startswith('0x'):
        return jsonify({"status": "error", "pesan": "Wallet address tidak valid!"}), 400

    ext = os.path.splitext(file.filename)[1] if file.filename else '.pdf'
    temp_filename = f"temp_{uuid.uuid4().hex}{ext}"

    try:
        file.save(temp_filename)

        # 1. Upload foto/PDF ke IPFS
        foto_hash = upload_to_ipfs(temp_filename, file.filename or "ijazah.pdf")
        if not foto_hash:
            raise Exception("Gagal upload file ke IPFS. Cek API Pinata.")

        # 2. Buat metadata JSON & upload ke IPFS
        metadata = {
            "name": f"Ijazah — {nama}",
            "description": f"Ijazah resmi UMC untuk {nama} (NIM: {nim})",
            "image": f"ipfs://{foto_hash}",
            "attributes": [
                {"trait_type": "Nama Mahasiswa", "value": nama},
                {"trait_type": "NIM",            "value": nim},
                {"trait_type": "Universitas",    "value": "Universitas Muhammadiyah Cirebon"},
                {"trait_type": "Wallet",         "value": wallet},
                {"trait_type": "Author",         "value": "Jabir Firdaus"}
            ]
        }
        meta_filename = f"meta_{uuid.uuid4().hex}.json"
        with open(meta_filename, 'w', encoding='utf-8') as mf:
            json.dump(metadata, mf, ensure_ascii=False, indent=2)

        meta_hash = upload_to_ipfs(meta_filename, "metadata.json")
        os.remove(meta_filename)

        if not meta_hash:
            raise Exception("Gagal upload metadata ke IPFS.")

        # 3. Mint ke blockchain (V1 atau V2)
        if CONTRACT_VERSION == 2:
            tx_hash = mint_v2(nama, nim, wallet, meta_hash, foto_hash)
        else:
            # V1: simpan metadata URI, nama & foto dicatat di IPFS metadata saja
            ipfs_uri = f"ipfs://{meta_hash}"
            tx_hash  = mint_v1(nim, wallet, ipfs_uri)

        return jsonify({
            "status": "sukses",
            "pesan": f"Ijazah {nama} berhasil diterbitkan!",
            "nama":           nama,
            "nim":            nim,
            "wallet":         wallet,
            "ipfs_foto":      foto_hash,
            "ipfs_meta":      meta_hash,
            "hash_transaksi": tx_hash,
            "link_etherscan": f"https://sepolia.etherscan.io/tx/{tx_hash}",
            "link_ipfs":      f"https://gateway.pinata.cloud/ipfs/{foto_hash}"
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "pesan": str(e)}), 500

    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

# ==========================================
# ENDPOINT 2: VERIFIKASI IJAZAH
# GET /api/verifikasi/<nim>
# ==========================================
@app.route('/api/verifikasi/<int:nim>', methods=['GET'])
def verifikasi_api(nim):
    try:
        if CONTRACT_VERSION == 2:
            result = cert_contract.functions.verifyCertificate(nim).call()
            nama_mhs    = result[0]
            nim_result  = result[1]
            wallet      = result[2]
            ipfs_meta   = result[3]
            ipfs_foto   = result[4]
            timestamp   = result[5]
            is_valid    = result[6]

            if not is_valid:
                return jsonify({"status": "error", "pesan": "Ijazah tidak valid!"}), 404

            tanggal = datetime.utcfromtimestamp(timestamp).strftime('%d %B %Y, %H:%M UTC')

            return jsonify({
                "status":          "sukses",
                "pesan":           "✅ Ijazah ASLI Terverifikasi di Blockchain!",
                "nama_mahasiswa":  nama_mhs,
                "nim":             nim_result,
                "wallet_mahasiswa": wallet,
                "tanggal_terbit":  tanggal,
                "ipfs_meta":       ipfs_meta,
                "ipfs_foto":       ipfs_foto,
                "link_foto":       f"https://gateway.pinata.cloud/ipfs/{ipfs_foto}",
            }), 200

        else:
            # V1: ambil owner + URI, lalu coba fetch metadata dari IPFS
            owner_wallet = cert_contract.functions.verifyOwner(nim).call()
            document_uri = cert_contract.functions.getCertificateData(nim).call()
            ipfs_hash    = document_uri.replace("ipfs://", "")

            # Coba ambil metadata JSON dari IPFS untuk mendapatkan nama & foto
            nama_mhs   = f"(NIM: {nim})"
            ipfs_foto  = ipfs_hash
            tanggal    = "—"

            try:
                meta_res = requests.get(
                    f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}",
                    timeout=10
                )
                if meta_res.status_code == 200:
                    meta     = meta_res.json()
                    nama_mhs = meta.get("attributes", [{}])[0].get("value", nama_mhs) \
                               if meta.get("attributes") else nama_mhs
                    # Ambil nama dari attributes
                    for attr in meta.get("attributes", []):
                        if attr.get("trait_type") == "Nama Mahasiswa":
                            nama_mhs = attr.get("value", nama_mhs)
                    # Ambil foto dari image field
                    img_uri = meta.get("image", "")
                    if img_uri.startswith("ipfs://"):
                        ipfs_foto = img_uri.replace("ipfs://", "")
            except Exception:
                pass  # Jika gagal ambil metadata, tetap return data minimal

            return jsonify({
                "status":           "sukses",
                "pesan":            "✅ Ijazah ASLI Terverifikasi di Blockchain!",
                "nama_mahasiswa":   nama_mhs,
                "nim":              nim,
                "wallet_mahasiswa": owner_wallet,
                "tanggal_terbit":   tanggal,
                "ipfs_meta":        ipfs_hash,
                "ipfs_foto":        ipfs_foto,
                "link_foto":        f"https://gateway.pinata.cloud/ipfs/{ipfs_foto}",
            }), 200

    except Exception as e:
        err_str = str(e)
        if "Tidak Ditemukan" in err_str or "revert" in err_str.lower() or "execution reverted" in err_str.lower():
            return jsonify({
                "status": "error",
                "pesan": "❌ Ijazah PALSU atau NIM Tidak Terdaftar di Blockchain!"
            }), 404
        return jsonify({"status": "error", "pesan": f"Error: {err_str}"}), 500

# ==========================================
# ENDPOINT 3: STATISTIK
# GET /api/stats
# ==========================================
@app.route('/api/stats', methods=['GET'])
def stats_api():
    try:
        if CONTRACT_VERSION == 2:
            total = cert_contract.functions.totalIssued().call()
        else:
            # V1 tidak punya totalIssued — hitung dari events (estimasi)
            total = "—"  # atau bisa query events

        return jsonify({
            "status":   "sukses",
            "total_ijazah": total,
            "network":  "Ethereum Sepolia Testnet",
            "kontrak":  ALAMAT_KONTRAK,
            "versi_kontrak": f"V{CONTRACT_VERSION}",
            "link_etherscan_kontrak": f"https://sepolia.etherscan.io/address/{ALAMAT_KONTRAK}"
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "pesan": str(e)}), 500

# ==========================================
# ENDPOINT 4: HEALTH CHECK
# GET /api/health
# ==========================================
@app.route('/api/health', methods=['GET'])
def health_check():
    connected = w3.is_connected()
    return jsonify({
        "status":              "online",
        "blockchain_connected": connected,
        "network":             "Sepolia Testnet" if connected else "Disconnected",
        "admin_wallet":        REKTOR_WALLET,
        "contract_version":   f"V{CONTRACT_VERSION}",
        "project":             "IjazahChain v2.0",
        "author":              "Jabir Firdaus"
    }), 200

# ==========================================
# JALANKAN SERVER
# ==========================================
if __name__ == '__main__':
    print("=" * 55)
    print("  IjazahChain Backend API v2.0")
    print("  Author  : Jabir Firdaus")
    print("  Server  : http://localhost:5000")
    print("  Network : Ethereum Sepolia Testnet")
    print(f"  Contract: V{CONTRACT_VERSION} — {ALAMAT_KONTRAK}")
    print("=" * 55)
    app.run(host='0.0.0.0', port=5000, debug=True)
