// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title  DigitalCertificate — IjazahChain
/// @author Jabir Andika (@jabirandika)
/// @notice Kontrak untuk menerbitkan dan memverifikasi ijazah digital mahasiswa
///         Universitas Muhammadiyah Cirebon di blockchain Ethereum.
///         Setiap ijazah diidentifikasi oleh NIM sebagai ID unik, dan menyimpan
///         URI IPFS yang mengarah ke metadata JSON berisi detail lengkap ijazah.
/// @dev    Deployed di Ethereum Sepolia Testnet. URI yang disimpan mengikuti
///         format `ipfs://<CID>` di mana CID adalah hash metadata JSON di Pinata IPFS.
///         Metadata JSON berisi: nama mahasiswa, NIM, institusi, dan URL file dokumen.
///         Pola ini umum dipakai di NFT agar gas biaya tetap rendah (off-chain storage).
///         Repository: github.com/jabirfirdaus/cert-nft-system
///         Version: 1.0.0 — May 2026
contract DigitalCertificate {

    // ─── State Variables ──────────────────────────────────────────────────────

    /// @notice Nama koleksi sertifikat ini.
    string public name = "Sertifikat Kelulusan UMC";

    /// @notice Simbol koleksi, mengikuti konvensi standar token.
    string public symbol = "CERT-UMC";

    /// @notice Alamat admin yang berhak menerbitkan ijazah baru.
    /// @dev    Ditetapkan ke msg.sender saat deploy. Dapat diganti via transferAdmin().
    ///         Hanya satu admin yang aktif pada satu waktu.
    address public admin;

    /// @dev Memetakan NIM mahasiswa ke alamat wallet pemilik sertifikat.
    ///      Digunakan untuk verifikasi kepemilikan: siapa yang memegang ijazah ini.
    mapping(uint256 => address) private _owners;

    /// @dev Memetakan NIM mahasiswa ke URI metadata IPFS.
    ///      URI dalam format `ipfs://<CID>` yang mengarah ke JSON berisi detail ijazah.
    mapping(uint256 => string) private _tokenURIs;

    // ─── Events ───────────────────────────────────────────────────────────────

    /// @notice Dipancarkan setiap kali ijazah baru berhasil diterbitkan ke blockchain.
    /// @param  student       Alamat wallet Ethereum mahasiswa penerima ijazah.
    /// @param  certificateId NIM mahasiswa, digunakan sebagai ID unik sertifikat.
    /// @param  tokenURI      URI metadata IPFS dalam format `ipfs://<CID>`.
    event CertificateIssued(
        address indexed student,
        uint256 indexed certificateId,
        string  tokenURI
    );

    // ─── Constructor ──────────────────────────────────────────────────────────

    /// @dev Menetapkan alamat yang men-deploy kontrak sebagai admin pertama.
    constructor() {
        admin = msg.sender;
    }

    // ─── Modifiers ────────────────────────────────────────────────────────────

    /// @dev Membatasi eksekusi fungsi hanya untuk alamat yang terdaftar sebagai admin.
    ///      Digunakan di issueCertificate() dan transferAdmin().
    modifier onlyAdmin() {
        require(msg.sender == admin, "Akses ditolak: bukan admin.");
        _;
    }

    // ─── Write Functions ──────────────────────────────────────────────────────

    /// @notice Menerbitkan ijazah baru ke blockchain.
    /// @dev    Menyimpan pasangan (NIM => wallet) dan (NIM => URI) ke storage.
    ///         NIM dipakai sebagai certificateId karena bersifat unik per mahasiswa.
    ///         URI yang dioper harus sudah dalam format `ipfs://<CID>` — backend
    ///         yang bertanggung jawab membuat URI ini sebelum memanggil fungsi ini.
    ///         Fungsi ini akan revert jika NIM sudah pernah digunakan sebelumnya.
    /// @param  studentWallet Alamat wallet Ethereum milik mahasiswa penerima.
    /// @param  certificateId NIM mahasiswa. Harus unik dan belum terdaftar sebelumnya.
    /// @param  documentURI   URI metadata dalam format `ipfs://<CID>`.
    function issueCertificate(
        address studentWallet,
        uint256 certificateId,
        string  memory documentURI
    ) public onlyAdmin {
        require(_owners[certificateId] == address(0), "NIM sudah terdaftar.");
        require(studentWallet != address(0), "Wallet address tidak valid.");

        _owners[certificateId]    = studentWallet;
        _tokenURIs[certificateId] = documentURI;

        emit CertificateIssued(studentWallet, certificateId, documentURI);
    }

    /// @notice Memindahkan hak admin ke alamat wallet lain.
    /// @dev    Setelah fungsi ini dipanggil, admin lama langsung kehilangan akses.
    ///         Pastikan newAdmin adalah alamat yang benar-benar dikuasai sebelum memanggil ini.
    /// @param  newAdmin Alamat wallet yang akan menjadi admin baru.
    function transferAdmin(address newAdmin) public onlyAdmin {
        require(newAdmin != address(0), "Alamat admin baru tidak valid.");
        admin = newAdmin;
    }

    // ─── View Functions ───────────────────────────────────────────────────────

    /// @notice Mengembalikan alamat wallet pemilik sertifikat berdasarkan NIM.
    /// @dev    Cocok dipakai oleh HRD atau pihak ketiga yang ingin memastikan
    ///         bahwa wallet tertentu benar-benar memiliki ijazah dengan NIM tersebut.
    ///         Fungsi ini revert jika NIM tidak ditemukan di storage.
    /// @param  certificateId NIM mahasiswa yang ingin diverifikasi.
    /// @return Alamat wallet Ethereum pemilik sertifikat.
    function verifyOwner(uint256 certificateId) public view returns (address) {
        address owner = _owners[certificateId];
        require(owner != address(0), "Sertifikat tidak ditemukan.");
        return owner;
    }

    /// @notice Mengembalikan URI metadata IPFS dari sertifikat berdasarkan NIM.
    /// @dev    URI dalam format `ipfs://<CID>`. Untuk mengakses kontennya,
    ///         ganti prefix `ipfs://` dengan URL gateway Pinata:
    ///         `https://gateway.pinata.cloud/ipfs/<CID>`.
    ///         Fungsi ini revert jika NIM tidak ditemukan di storage.
    /// @param  certificateId NIM mahasiswa.
    /// @return URI metadata dalam format string `ipfs://<CID>`.
    function getCertificateData(uint256 certificateId) public view returns (string memory) {
        require(_owners[certificateId] != address(0), "Sertifikat tidak ditemukan.");
        return _tokenURIs[certificateId];
    }
}