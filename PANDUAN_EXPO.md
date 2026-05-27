# 🚀 PANDUAN DEMO EXPO — IjazahChain
# Untuk: Teman yang membawa demo di expo kampus
# Dibuat oleh: Jabir Firdaus

---

## ✅ Yang Sudah Siap

- Smart Contract deployed di Ethereum Sepolia
- Contract Address: 0xd1eD6112A65492a761C8Fe68666a1f8cd32e49A0
- Lihat di Etherscan: https://sepolia.etherscan.io/address/0xd1eD6112A65492a761C8Fe68666a1f8cd32e49A0

---

## 🖥️ CARA MENJALANKAN (Langkah per Langkah)

### PRASYARAT (Install sekali saja)

1. Install Python 3.10+: https://python.org/downloads
   - CENTANG "Add Python to PATH" saat install!

2. Buka Command Prompt / Terminal, jalankan:
   ```
   pip install flask flask-cors web3 python-dotenv requests
   ```

---

### LANGKAH DEMO

**Langkah 1: Buka folder project**
```
cd C:\Users\[nama]\cert-nft-system\backend
```

**Langkah 2: Jalankan server**
```
python server.py
```

Kalau berhasil, akan muncul:
```
=======================================================
  IjazahChain Backend API — Jabir Firdaus
  Server: http://localhost:5000
  Network: Ethereum Sepolia Testnet
=======================================================
```

**Langkah 3: Buka frontend**
- Klik dua kali file: `frontend/index.html`
- Atau buka di browser: `file:///C:/Users/[nama]/cert-nft-system/frontend/index.html`

---

## 🎯 ALUR DEMO (5 Menit)

### Demo 1: Terbitkan Ijazah (Tab Pertama)

1. Isi form:
   - Nama: [Nama dummy] misal "Ahmad Rifai"
   - NIM: [angka unik] misal "240511001"
   - Wallet: `0x70997970C51812dc3A010C7d01b50e0d17dc79C8`
   - Upload: file PDF atau JPG apapun

2. Klik "Terbitkan ke Blockchain"

3. Tunggu ~15-30 detik (proses blockchain)

4. Akan muncul:
   - ✅ Konfirmasi sukses
   - Link ke Etherscan (klik untuk lihat transaksi!)
   - Link ke IPFS (klik untuk lihat dokumen!)

### Demo 2: Verifikasi Ijazah (Tab Kedua)

1. Pindah ke tab "Verifikasi Ijazah"

2. Masukkan NIM yang baru saja diterbitkan

3. Klik "Verifikasi Keaslian Ijazah"

4. Akan muncul:
   - ✅ IJAZAH ASLI & TERVERIFIKASI
   - Nama lengkap mahasiswa
   - NIM
   - Tanggal terbit
   - Wallet pemilik
   - Preview dokumen ijazah
   - Link Etherscan

### Demo 3: Coba NIM Palsu

1. Masukkan NIM random yang belum terdaftar

2. Hasilnya: ❌ IJAZAH TIDAK DITEMUKAN

---

## ⚠️ TROUBLESHOOTING

**"Gagal terhubung ke server"**
→ Pastikan server Python sudah jalan (lihat Langkah 2)

**"Gagal upload ke IPFS"**
→ Cek koneksi internet

**"Error transaksi blockchain"**
→ Kemungkinan wallet admin kehabisan ETH Sepolia
→ Minta ETH Sepolia di: https://sepoliafaucet.com

**Server error / crash**
→ Kirim WhatsApp ke Jabir untuk troubleshoot live

---

## 📞 Kontak Darurat

Jabir Firdaus — [masukkan nomor WA/kontak kamu]
GitHub: github.com/jabirfirdaus

---

> 💡 Tips: Siapkan 2-3 data mahasiswa dummy sebelum demo agar terlihat lancar!
