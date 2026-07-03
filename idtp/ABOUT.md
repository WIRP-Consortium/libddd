<p align="center">
  <img src="daemon.png" alt="WIRP idtpd" width="900">
</p>

# WIRP idtpd

---

## 📡 WIRP IDTP Daemon Specification

**WIRP idtpd** is a secure server-side daemon implementing the **Internet Data Transmission Protocol (IDTP)**.  
It is designed for encrypted, authenticated, and replay-protected communication over TCP with optional **TLS 1.3** transport security.

---

## 🧠 Core Purpose

The daemon acts as a **secure resource delivery engine**, handling encrypted requests and returning protected responses using hybrid cryptography.

---

## 🔐 Security Model

### ✔ Encryption
- RSA-OAEP → Secure AES session key exchange  
- AES-256-GCM → Payload encryption (confidentiality + integrity)

### ✔ Authentication
- RSA public/private key identity verification  
- Registrant-based identity mapping

### ✔ Integrity Protection
- HMAC-SHA256 for request validation  
- Checksum verification for tamper detection  

### ✔ Replay Protection
- Nonce-based request tracking  
- Timestamp validation (300s expiry window)  
- In-memory nonce cache (`nonce_store`)

### ✔ Transport Security
- TLS 1.3 enforced socket communication  
- Encrypted TCP channel

---

## 📦 Packet Structure

### Request Format
VER | TYPE | TO | IP | REGISTRANT | METHOD
NONCE | CHK | PUBLIC_KEY | CLIENT_KEY
MAC | TIMESTAMP | IV

DATA:
<encrypted payload>
RSA_OAEP(AES_KEY) | IV | AES_GCM(CIPHERTEXT)


---

## ⚙️ Processing Flow

1. Client connects via TLS 1.3  
2. Server receives IDTP packet  
3. Packet parsed and validated  
4. Checks performed:
   - Signature / key validation  
   - Nonce verification  
   - Timestamp expiry check  
   - HMAC + checksum validation  
5. AES key decrypted using RSA private key  
6. Payload decrypted using AES-256-GCM  
7. Resource is resolved from filesystem  
8. Response encrypted with new AES key  
9. AES key encrypted with client RSA public key  
10. Response sent back securely  

---

## 📁 Resource Handling

Supported formats:
- `.png`
- `.jpg`
- `.txt`
- `.smrl`

Files are mapped using:

---

## 🚨 Error System

Standard error response format:
IDTP: <version> / ERROR
CODE: <error_code>
MESSAGE: <description>
TIMESTAMP: <unix_time>


Common errors:
- 101 → Missing checksum  
- 103 → Missing MAC  
- 104 → Expired packet  
- 111 → Replay attack detected  
- 121 → Invalid checksum  
- 122 → Invalid MAC  
- 129 → Decryption failure  

---

## 🧾 Key Features

- Hybrid cryptography (RSA + AES)
- TLS 1.3 secure transport
- Replay attack protection
- Multi-threaded request handling
- File-based secure resource system
- Per-session encryption keys

---

## ⚠️ Limitations

- No database backend (file-based only)
- Nonce storage is in-memory only
- No forward secrecy yet
- No distributed scaling support

---

## 🚀 Future Improvements

- ECC-based cryptography
- Persistent replay store (Redis/DB)
- Certificate Authority integration
- Forward secrecy (ECDHE)
- Load-balanced cluster support

---

## 📌 Summary

**WIRP idtpd** is a secure daemon implementation of IDTP that provides encrypted, authenticated, and replay-protected communication with strong cryptographic guarantees and a modular architecture for future expansion.
