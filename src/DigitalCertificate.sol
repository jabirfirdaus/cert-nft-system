// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract DigitalCertificate {
    // Nama & Simbol dari Koleksi Sertifikat ini
    string public name = "Sertifikat Kelulusan UMC";
    string public symbol = "CERT-UMC";

    // Siapa yang berhak mencetak sertifikat? (Misal: Rektor / Admin)
    address public admin;

    // --- STRUKTUR DATA UTAMA (THE LEDGER) ---
    // 1. Pemilik Sertifikat: Nomor Sertifikat (ID) -> Alamat Dompet Mahasiswa
    mapping(uint256 => address) private _owners;

    // 2. Data Dokumen: Nomor Sertifikat (ID) -> Link IPFS (Isi PDF/Nilai)
    mapping(uint256 => string) private _tokenURIs;

    // Event/Alarm yang berbunyi ketika sertifikat baru diterbitkan
    event CertificateIssued(address indexed student, uint256 indexed certificateId, string tokenURI);

    constructor() {
        admin = msg.sender; // Yang nge-deploy kontrak otomatis jadi Admin
    }

    // Penjaga Pintu: Cuma Admin yang boleh mengeksekusi
    modifier onlyAdmin() {
        require(msg.sender == admin, "AKSES DITOLAK: Lo bukan Admin/Rektor!");
        _;
    }

    // ==========================================
    // FUNGSI UTAMA 1: MENCETAK SERTIFIKAT (MINTING)
    // ==========================================
    function issueCertificate(address studentWallet, uint256 certificateId, string memory documentURI) public onlyAdmin {
        // Syarat 1: Sertifikat ID ini belum pernah dicetak sebelumnya
        require(_owners[certificateId] == address(0), "ERROR: Nomor Sertifikat ini sudah terdaftar!");
        
        // Syarat 2: Alamat dompet mahasiswa gak boleh kosong
        require(studentWallet != address(0), "ERROR: Alamat dompet tidak valid!");

        // Eksekusi Pencatatan ke Blockchain
        _owners[certificateId] = studentWallet;
        _tokenURIs[certificateId] = documentURI;

        // Bunyikan alarm bahwa sertifikat sah telah terbit
        emit CertificateIssued(studentWallet, certificateId, documentURI);
    }

    // ==========================================
    // FUNGSI UTAMA 2: VERIFIKASI KEASLIAN
    // ==========================================
    // HRD atau Perusahaan tinggal masukin Nomor Sertifikat buat ngecek siapa pemilik aslinya
    function verifyOwner(uint256 certificateId) public view returns (address) {
        address owner = _owners[certificateId];
        require(owner != address(0), "Sertifikat Palsu / Tidak Ditemukan!");
        return owner;
    }

    // Fungsi untuk melihat link dokumen (IPFS) dari sertifikat tersebut
    function getCertificateData(uint256 certificateId) public view returns (string memory) {
        require(_owners[certificateId] != address(0), "Sertifikat Palsu / Tidak Ditemukan!");
        return _tokenURIs[certificateId];
    }
}