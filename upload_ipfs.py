import requests
import os # Tambahin ini di baris paling atas (di bawah import requests)

# 1. SETUP KUNCI GUDANG (PINATA API)
# Paste API Key dan Secret lo di sini (jangan sampai kebalik ya)
PINATA_API_KEY = " "
PINATA_SECRET_KEY = " "

# 2. TARGET FILE YANG MAU DI-UPLOAD
# Pastikan file ini beneran ada di folder yang sama dengan script Python lo
FILE_PATH = "ijazah_dummy.txt"

def upload_to_ipfs(file_path):
    print(f"Menyiapkan roket... Mengunggah '{file_path}' ke jaringan IPFS via Pinata...")
    
    # Endpoint resmi Pinata buat upload file
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    
    # Header untuk otentikasi bahwa lo adalah pemilik akun
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_KEY
    }
    
    # Buka file dalam mode 'rb' (read binary)
    try:
        with open(file_path, 'rb') as file:
            # Tembak file-nya pakai metode POST
            response = requests.post(url, files={'file': file}, headers=headers)
            
            if response.status_code == 200:
                # Ambil Hash unik (CID) dari respon JSON
                ipfs_hash = response.json()['IpfsHash']
                print("\nBERHASIL MENDARAT DI IPFS!")
                print("=========================================")
                print(f"Link IPFS murni : ipfs://{ipfs_hash}")
                print(f"Cek di Browser  : https://gateway.pinata.cloud/ipfs/{ipfs_hash}")
                print("=========================================")
                return ipfs_hash
            else:
                print("\nGAGAL UPLOAD. Cek lagi API Key lo.")
                print(response.text)
                return None
    except FileNotFoundError:
        print(f"\nERROR: File '{file_path}' gak ketemu Bro. Bikin dulu filenya!")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🎓 SISTEM PENERBITAN IJAZAH DIGITAL JABIR 🎓")
    print("="*50)

    while True:
        # 1. Rektor input manual nama file dari terminal
        file_target = input("\nMasukkan nama file Ijazah (contoh: ijazah.pdf) atau ketik 'exit' buat keluar: ")
        
        if file_target.lower() == 'exit':
            print("Sistem dimatikan. Selamat istirahat, Pak Rektor!")
            break

        # 2. Cek apakah filenya beneran ada di laptop
        if os.path.exists(file_target):
            # 3. Kalau ada, jalankan fungsi upload ke IPFS!
            hash_hasil = upload_to_ipfs(file_target)
            
            if hash_hasil:
                # NANTI DI SINI KITA TAMBAHIN KODE WEB3.PY BUAT MINTING KE BLOCKCHAIN!
                print(f"Ijazah siap dicetak ke Blockchain dengan CID: {hash_hasil}")
        else:
            print(f"ERROR: File '{file_target}' gak ketemu di laptop lo. Cek lagi ketikannya!")