// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console} from "forge-std/Test.sol";
import {DigitalCertificate} from "../src/DigitalCertificate.sol";

contract DigitalCertificateTest is Test {
    DigitalCertificate public cert;
    
    // Kita bikin dua dompet aktor (aktor simulasi)
    address rektor = address(0x111);
    address mahasiswa = address(0x222);

    function setUp() public {
        // Rektor (sebagai Admin) men-deploy Smart Contract ini
        vm.prank(rektor);
        cert = new DigitalCertificate();
    }

    // ==========================================
    // SKENARIO 1: REKTOR NERBITIN IJAZAH ASLI
    // ==========================================
    function testIssueCertificateSukses() public {
        // Kita jadikan NIM sebagai ID Sertifikat agar unik dan gak bisa ganda
        uint256 nim = 240511067;
        
        // Ini adalah link desentralisasi (IPFS) yang mengarah ke file PDF Ijazah Cum Laude
        string memory linkIPFS = "ipfs://QmYwAPJzv5CZsnA625s3Xf2sm5DcgXU1rvpG1F"; 

        // Rektor login dan mencetak sertifikat ke dompet mahasiswa
        vm.startPrank(rektor);
        cert.issueCertificate(mahasiswa, nim, linkIPFS);
        vm.stopPrank();

        // --- ZONA HRD (VERIFIKASI) ---
        // HRD dari agensi Social Media Management ngecek keaslian Ijazah pelamarnya
        address pemilikAsli = cert.verifyOwner(nim);
        string memory dataPDF = cert.getCertificateData(nim);
        
        // Mesin Foundry memverifikasi: Apakah dompet pemilik sertifikat = dompet mahasiswa?
        assertEq(pemilikAsli, mahasiswa);
        
        // Mesin Foundry memverifikasi: Apakah link PDF-nya cocok dan belum diubah hacker?
        assertEq(dataPDF, linkIPFS);
    }

    // ==========================================
    // SKENARIO 2: MAHASISWA NAKAL BIKIN IJAZAH PALSU
    // ==========================================
    function testHackerGagalCetak() public {
        address hacker = address(0x999);
        uint256 nimPalsu = 123456789;
        string memory linkIPFSPalsu = "ipfs://hacked-pdf";

        // Hacker nyoba manggil fungsi cetak sertifikat dari dompetnya sendiri
        vm.startPrank(hacker);
        
        // Kita beri tahu Foundry: "Transaksi di bawah ini HARUS GAGAL (Revert)!"
        vm.expectRevert("AKSES DITOLAK: Lo bukan Admin/Rektor!");
        
        // Transaksi dieksekusi, dan boom! Akan ditolak oleh Modifier onlyAdmin.
        cert.issueCertificate(hacker, nimPalsu, linkIPFSPalsu);
        
        vm.stopPrank();
    }
}