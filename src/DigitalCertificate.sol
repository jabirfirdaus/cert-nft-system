// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// ============================================================
// Project   : IjazahChain — Sistem Verifikasi Ijazah Digital
// Author    : Jabir Firdaus
// GitHub    : github.com/jabirfirdaus
// Universitas: Universitas Muhammadiyah Cirebon (UMC)
// Version   : 2.0.0
// Network   : Ethereum Sepolia Testnet
// Date      : May 2026
// License   : MIT
// ============================================================
// Kontrak ini menyimpan data ijazah mahasiswa secara permanen
// di blockchain Ethereum. Setiap ijazah memiliki ID unik,
// nama mahasiswa, NIM, dan link ke dokumen asli di IPFS.
// ============================================================

contract DigitalCertificate {

    // ==========================================
    // IDENTITAS KOLEKSI SERTIFIKAT
    // ==========================================
    string public name   = "IjazahChain — UMC";
    string public symbol = "IJAZAH-UMC";
    string public university = "Universitas Muhammadiyah Cirebon";
    string public author = "Jabir Firdaus";

    // Admin (Rektor / Operator) yang berhak menerbitkan ijazah
    address public admin;

    // Counter otomatis untuk ID Sertifikat
    uint256 private _totalIssued;

    // ==========================================
    // STRUKTUR DATA IJAZAH
    // ==========================================
    struct CertificateData {
        string  namaMahasiswa;   // Nama lengkap mahasiswa
        uint256 nim;             // Nomor Induk Mahasiswa
        address walletMahasiswa; // Alamat dompet Ethereum mahasiswa
        string  ipfsHash;        // CID/Hash file ijazah di IPFS
        string  fotoIpfsHash;    // CID/Hash foto ijazah (gambar/PDF)
        uint256 tanggalTerbit;   // Timestamp penerbitan (Unix time)
        bool    valid;           // Status keabsahan
    }

    // ==========================================
    // PENYIMPANAN DATA (THE LEDGER)
    // ==========================================
    // NIM -> Data Ijazah Lengkap
    mapping(uint256 => CertificateData) private _certificates;

    // NIM -> Certificate ID (untuk kompatibilitas dengan sistem lama)
    mapping(uint256 => uint256) private _nimToCertId;

    // ==========================================
    // EVENTS — Alarm Blockchain
    // ==========================================
    event IjazahDiterbitkan(
        address indexed mahasiswa,
        uint256 indexed nim,
        uint256 certificateId,
        string  namaMahasiswa,
        string  ipfsHash,
        uint256 timestamp
    );

    event IjazahDinonaktifkan(
        uint256 indexed nim,
        uint256 timestamp
    );

    // ==========================================
    // CONSTRUCTOR
    // ==========================================
    constructor() {
        admin = msg.sender;
        _totalIssued = 0;
    }

    // ==========================================
    // MODIFIER — Penjaga Akses
    // ==========================================
    modifier onlyAdmin() {
        require(
            msg.sender == admin,
            "AKSES DITOLAK: Hanya Admin/Rektor yang bisa menerbitkan ijazah!"
        );
        _;
    }

    // ==========================================
    // FUNGSI UTAMA 1: MENERBITKAN IJAZAH (MINTING)
    // ==========================================
    // Dipanggil oleh Admin/Rektor untuk menerbitkan ijazah baru
    // Params:
    //   - namaMahasiswa : Nama lengkap mahasiswa
    //   - nim           : Nomor Induk Mahasiswa (unik, jadi Certificate ID)
    //   - walletAddr    : Alamat dompet Ethereum mahasiswa
    //   - ipfsHash      : CID file ijazah (JSON metadata) di IPFS
    //   - fotoIpfsHash  : CID file foto/PDF ijazah di IPFS
    function issueCertificate(
        string  memory namaMahasiswa,
        uint256        nim,
        address        walletAddr,
        string  memory ipfsHash,
        string  memory fotoIpfsHash
    ) public onlyAdmin {
        // Validasi: NIM belum pernah terdaftar
        require(
            !_certificates[nim].valid,
            "ERROR: NIM ini sudah memiliki ijazah terdaftar!"
        );

        // Validasi: Wallet address tidak kosong
        require(
            walletAddr != address(0),
            "ERROR: Alamat dompet mahasiswa tidak valid!"
        );

        // Validasi: Nama tidak boleh kosong
        require(
            bytes(namaMahasiswa).length > 0,
            "ERROR: Nama mahasiswa tidak boleh kosong!"
        );

        // Validasi: IPFS hash tidak boleh kosong
        require(
            bytes(ipfsHash).length > 0,
            "ERROR: IPFS hash tidak boleh kosong!"
        );

        // Increment counter ID
        _totalIssued++;
        uint256 certId = _totalIssued;

        // Simpan data ijazah ke blockchain
        _certificates[nim] = CertificateData({
            namaMahasiswa:   namaMahasiswa,
            nim:             nim,
            walletMahasiswa: walletAddr,
            ipfsHash:        ipfsHash,
            fotoIpfsHash:    fotoIpfsHash,
            tanggalTerbit:   block.timestamp,
            valid:           true
        });

        _nimToCertId[nim] = certId;

        // Emit event — tercatat permanen di blockchain
        emit IjazahDiterbitkan(
            walletAddr,
            nim,
            certId,
            namaMahasiswa,
            ipfsHash,
            block.timestamp
        );
    }

    // ==========================================
    // FUNGSI UTAMA 2: VERIFIKASI IJAZAH
    // ==========================================
    // Siapapun bisa memanggil fungsi ini untuk memverifikasi
    // keaslian ijazah berdasarkan NIM mahasiswa
    function verifyCertificate(uint256 nim) public view returns (
        string  memory namaMahasiswa,
        uint256        nimResult,
        address        walletMahasiswa,
        string  memory ipfsHash,
        string  memory fotoIpfsHash,
        uint256        tanggalTerbit,
        bool           isValid
    ) {
        CertificateData memory cert = _certificates[nim];
        require(cert.valid, "IJAZAH TIDAK DITEMUKAN: NIM tidak terdaftar atau ijazah tidak valid!");

        return (
            cert.namaMahasiswa,
            cert.nim,
            cert.walletMahasiswa,
            cert.ipfsHash,
            cert.fotoIpfsHash,
            cert.tanggalTerbit,
            cert.valid
        );
    }

    // ==========================================
    // FUNGSI LAMA (Kompatibilitas Backend Lama)
    // ==========================================
    // Verifikasi owner berdasarkan NIM (sama seperti Certificate ID)
    function verifyOwner(uint256 nim) public view returns (address) {
        require(_certificates[nim].valid, "Sertifikat Tidak Ditemukan!");
        return _certificates[nim].walletMahasiswa;
    }

    // Ambil data dokumen IPFS berdasarkan NIM
    function getCertificateData(uint256 nim) public view returns (string memory) {
        require(_certificates[nim].valid, "Sertifikat Tidak Ditemukan!");
        return _certificates[nim].ipfsHash;
    }

    // ==========================================
    // FUNGSI STATISTIK (READ-ONLY)
    // ==========================================
    function totalIssued() public view returns (uint256) {
        return _totalIssued;
    }

    function getUniversity() public view returns (string memory) {
        return university;
    }

    function getAuthor() public view returns (string memory) {
        return author;
    }

    // ==========================================
    // FUNGSI ADMIN
    // ==========================================
    // Transfer hak admin ke wallet lain (misal: Rektor baru)
    function transferAdmin(address newAdmin) public onlyAdmin {
        require(newAdmin != address(0), "Alamat admin baru tidak valid!");
        admin = newAdmin;
    }
}