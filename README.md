# Internet Data Transmission Protocol (IDTP)

<p align="center">
  <b>A Secure Application-Layer Protocol for Confidential, Authenticated, and Reliable Data Transmission</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Protocol-IDTP-blue" alt="Protocol">
  <img src="https://img.shields.io/badge/Security-AES--256--GCM-green" alt="AES">
  <img src="https://img.shields.io/badge/Encryption-RSA--OAEP-orange" alt="RSA">
  <img src="https://img.shields.io/badge/Authentication-RSA%20Signature-red" alt="Signature">
  <img src="https://img.shields.io/badge/Integrity-HMAC--SHA256-yellow" alt="HMAC">
  <img src="https://img.shields.io/badge/License-MIT-blueviolet" alt="License">
</p>

---

## Overview

**Internet Data Transmission Protocol (IDTP)** is a custom **application-layer protocol** designed for secure communication over IP-based networks.

It combines **hybrid encryption**, **digital signatures**, **authenticated encryption**, **message authentication**, and **replay protection** into a unified packet format that ensures:

* 🔒 Confidentiality
* ✅ Integrity
* 👤 Authentication
* 🛡️ Replay attack protection
* 🔑 Secure session key exchange

IDTP is suitable for applications requiring secure exchange of sensitive resources across the Internet or private networks.

---

# Table of Contents

* [Features](#-features)
* [Protocol Architecture](#-protocol-architecture)
* [Security Mechanisms](#-security-mechanisms)
* [Packet Structure](#-packet-structure)
* [Communication Workflow](#-communication-workflow)
* [Advantages](#-advantages)
* [Applications](#-applications)
* [Future Enhancements](#-future-enhancements)
* [Conclusion](#-conclusion)

---

# Features

* Hybrid Encryption (RSA + AES)
* AES-256-GCM authenticated encryption
* RSA-OAEP secure session key exchange
* RSA Digital Signatures
* HMAC-SHA256 integrity verification
* Replay attack prevention
* Nonce & Timestamp validation
* Session-based encryption keys
* Secure request and response communication
* Modular and extensible packet format

---

# 🏗 Protocol Architecture

IDTP follows a **client-server architecture**.

```
          Client
             │
             │
      Generate AES Key
             │
             ▼
 Encrypt Request (AES-256-GCM)
             │
 Encrypt AES Key (RSA-OAEP)
             │
 Sign Packet (RSA Signature)
             │
 Attach:
   • Nonce
   • Timestamp
   • HMAC
             │
             ▼
 ───────── Internet ─────────►
             │
             ▼
           Server
             │
 Verify Signature
 Verify HMAC
 Verify Timestamp
 Verify Nonce
             │
Decrypt AES Key (RSA)
             │
Decrypt Payload (AES)
             │
Retrieve Resource
             │
Generate New AES Key
             │
Encrypt Response
             │
Encrypt Response Key
             │
◄──────── Secure Response ────────
```

---

# Security Mechanisms

## Hybrid Encryption

IDTP combines symmetric and asymmetric cryptography.

### RSA-OAEP

Used for securely exchanging AES session keys.

### AES-256-GCM

Used for authenticated encryption of application data.

Provides:

* Confidentiality
* Authentication
* Integrity

---

## Digital Signatures

Every request is digitally signed using the sender's **RSA private key**.

The receiver verifies the signature using the sender's **public key**, ensuring:

* Sender authenticity
* Data integrity
* Non-repudiation

---

## Message Authentication

Every packet includes an **HMAC-SHA256** value.

This detects:

* Packet tampering
* Unauthorized modifications
* Transmission corruption

---

## Replay Attack Protection

Each packet contains:

* Random cryptographic nonce
* Unix timestamp

The receiver maintains a temporary nonce cache.

Duplicate packets are rejected automatically.

---

## Session Key Security

A new AES-256 session key is generated for **every communication session**, minimizing key reuse and limiting the impact of key compromise.

---

# Packet Structure

```
+----------------------------------------------------+
|                    HEADER                          |
+----------------------------------------------------+
| Protocol Version                                  |
| Message Type                                      |
| Source ID                                         |
| Destination ID                                    |
| Registrant ID                                     |
| Requested Resource                                |
| Encryption Algorithm                              |
| Nonce                                             |
| Timestamp                                         |
| Sender Public Key                                 |
| Digital Signature                                 |
| Encrypted AES Session Key                         |
| HMAC                                              |
| Initialization Vector (IV)                        |
+----------------------------------------------------+
|                    DATA                            |
+----------------------------------------------------+
| AES-256-GCM Encrypted Payload                     |
+----------------------------------------------------+
```

---

# Communication Workflow

## Client Side

1. Create resource request.
2. Generate a random AES-256 session key.
3. Encrypt request using AES-256-GCM.
4. Encrypt AES key with the server's RSA public key.
5. Generate RSA digital signature.
6. Compute HMAC-SHA256.
7. Attach nonce and timestamp.
8. Send the packet to the server.

---

## Server Side

1. Receive packet.
2. Verify timestamp.
3. Verify nonce.
4. Verify HMAC.
5. Verify digital signature.
6. Decrypt AES session key.
7. Decrypt request payload.
8. Retrieve requested resource.
9. Generate a new AES session key.
10. Encrypt response.
11. Encrypt response AES key with the client's RSA public key.
12. Send secure response.

---

# Advantages

* End-to-end encryption
* Strong authentication
* Secure key exchange
* Authenticated encryption
* Replay attack protection
* Packet integrity verification
* Modular protocol design
* Efficient hybrid cryptography
* Extensible architecture
* Secure client-server communication

---

# Applications

IDTP can be used in:

* Secure File Transfer Systems
* Client-Server Applications
* Distributed Storage Systems
* Secure Document Exchange
* Private Communication Platforms
* Remote Resource Access
* Research Projects
* Enterprise Data Transmission
* Secure Cloud Communication
* Custom Network Applications

---

#  Future Enhancements

Potential improvements include:

* Elliptic Curve Cryptography (ECC)
* Forward Secrecy
* Certificate-based Authentication
* TLS Integration
* Protocol Compression
* Multi-client Session Management
* Secure Key Rotation
* Post-Quantum Cryptography Support

---

# Cryptographic Algorithms

| Purpose               | Algorithm                                 |
| --------------------- | ----------------------------------------- |
| Symmetric Encryption  | AES-256-GCM                               |
| Asymmetric Encryption | RSA-OAEP                                  |
| Digital Signature     | RSA                                       |
| Integrity             | HMAC-SHA256                               |
| Randomness            | Cryptographically Secure Random Generator |

---

# 🛡 Security Goals

✔ Confidentiality

✔ Integrity

✔ Authentication

✔ Non-Repudiation

✔ Replay Protection

✔ Secure Key Exchange

✔ Authenticated Encryption

---

# Conclusion

The **Internet Data Transmission Protocol (IDTP)** is a secure, extensible application-layer protocol that provides confidential, authenticated, and reliable communication over IP networks.

By integrating **hybrid encryption**, **AES-256-GCM**, **RSA-OAEP**, **digital signatures**, **HMAC-SHA256**, and **replay protection**, IDTP establishes a comprehensive security framework capable of protecting data against interception, tampering, impersonation, and replay attacks.

Its modular architecture makes it suitable for secure client-server systems while allowing future enhancements such as certificate-based authentication, forward secrecy, and post-quantum cryptographic support.

---

## License

This project is licensed under the **MIT License**.

---

<p align="center">
Developed for secure and reliable Internet communication using modern cryptographic principles.
</p>
