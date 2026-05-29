// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title  DigitalCertificate — IjazahChain
/// @author Jabir Firdaus (github.com/jabirfirdaus)
/// @notice Kontrak ini menyimpan referensi ijazah digital mahasiswa di blockchain Ethereum.
///         Setiap ijazah diidentifikasi oleh NIM, dan URI yang disimpan mengarah ke
///         metadata JSON di IPFS yang berisi nama, institusi, dan link ke file dokumen.
/// @dev    Menggunakan pola penyimpanan URI off-chain (IPFS) agar gas tetap efisien.
///         Kontrak ini di-deploy di Ethereum Sepolia Testnet oleh Universitas Muhammadiyah Cirebon.
///         Network : Ethereum Sepolia Testnet
///         Version : 1.0.0 — May 2026
contract DigitalCertificate {

    // ─── State Variables ──────────────────────────────────────────────────────

    /// @notice Nama koleksi sertifikat ini.
    string public name = "Sertifikat Kelulusan UMC";

    /// @notice Simbol koleksi, mengikuti konvensi token.
    string public symbol = "CERT-UMC";

    /// @notice Alamat admin yang berhak menerbitkan ijazah.
    /// @dev    Di-set ke msg.sender saat deploy. Bisa dipindahkan via transferAdmin().
    address public admin;

    /// @dev Menyimpan pemilik tiap sertifikat: NIM => wallet mahasiswa.
    mapping(uint256 => address) private _owners;

    /// @dev Menyimpan URI metadata tiap sertifikat: NIM => ipfs://CID.
    mapping(uint256 => string) private _tokenURIs;

    // ─── Events ───────────────────────────────────────────────────────────────

    /// @notice Dipancarkan setiap kali ijazah baru berhasil diterbitkan.
    /// @param  student       Alamat wallet mahasiswa penerima.
    /// @param  certificateId NIM mahasiswa, digunakan sebagai ID sertifikat.
    /// @param  tokenURI      URI metadata IPFS yang berisi detail ijazah.
    event CertificateIssued(
        address indexed student,
        uint256 indexed certificateId,
        string  tokenURI
    );

    // ─── Constructor ──────────────────────────────────────────────────────────

    /// @dev Menetapkan deployer sebagai admin awal.
    constructor() {
        admin = msg.sender;
    }

    // ─── Modifiers ────────────────────────────────────────────────────────────

    /// @dev Membatasi akses fungsi hanya untuk admin yang terdaftar.
    modifier onlyAdmin() {
        require(msg.sender == admin, "Akses ditolak: bukan admin.");
        _;
    }

    // ─── Write Functions ──────────────────────────────────────────────────────

    /// @notice Menerbitkan ijazah baru ke blockchain.
    /// @dev    Hanya bisa dipanggil oleh admin. NIM berfungsi sebagai ID unik.
    ///         URI yang disimpan adalah CID IPFS metadata JSON, bukan file ijazah langsung.
    /// @param  studentWallet Alamat wallet Ethereum mahasiswa.
    /// @param  certificateId NIM mahasiswa (harus unik, belum pernah digunakan).
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

    /// @notice Memindahkan hak admin ke alamat lain.
    /// @dev    Hanya bisa dipanggil oleh admin aktif saat ini.
    /// @param  newAdmin Alamat wallet admin baru.
    function transferAdmin(address newAdmin) public onlyAdmin {
        require(newAdmin != address(0), "Alamat admin baru tidak valid.");
        admin = newAdmin;
    }

    // ─── View Functions ───────────────────────────────────────────────────────

    /// @notice Mengembalikan alamat wallet pemilik sertifikat berdasarkan NIM.
    /// @dev    Revert jika NIM tidak terdaftar.
    /// @param  certificateId NIM mahasiswa.
    /// @return Alamat wallet mahasiswa pemilik sertifikat.
    function verifyOwner(uint256 certificateId) public view returns (address) {
        address owner = _owners[certificateId];
        require(owner != address(0), "Sertifikat tidak ditemukan.");
        return owner;
    }

    /// @notice Mengembalikan URI metadata IPFS dari sertifikat berdasarkan NIM.
    /// @dev    URI dalam format `ipfs://<CID>`. CID mengarah ke JSON metadata
    ///         yang menyimpan nama, NIM, institusi, dan link file ijazah.
    /// @param  certificateId NIM mahasiswa.
    /// @return URI metadata dalam format string.
    function getCertificateData(uint256 certificateId) public view returns (string memory) {
        require(_owners[certificateId] != address(0), "Sertifikat tidak ditemukan.");
        return _tokenURIs[certificateId];
    }
}