#!/bin/bash
set -e

echo "[*] Starting Lab services..."

# ── Pre-flight dirs ─────────────────────────────────────────────────────────
mkdir -p /var/run/vsftpd/empty
mkdir -p /var/run/samba /var/log/samba
mkdir -p /run/sshd

# ── Samba ──────────────────────────────────────────────────────────────────
echo "[*] Starting Samba (SMB/CIFS)..."
rm -f /var/run/samba/*.pid
smbd --daemon --no-process-group
nmbd --daemon --no-process-group
echo "[+] Samba started"

# ── FTP ────────────────────────────────────────────────────────────────────
echo "[*] Starting vsftpd (FTP)..."
vsftpd /etc/vsftpd.conf &
echo "[+] vsftpd started"

# ── SSH ────────────────────────────────────────────────────────────────────
echo "[*] Starting OpenSSH..."
/usr/sbin/sshd -D &
echo "[+] sshd started"

echo ""
echo "================================================================"
echo "  Lab ready — services:"
echo "    SMB  :139,445  (anonymous read on 'Shared')"
echo "    FTP  :21       (user: andrew — key found in PDF)"
echo "    SSH  :22       (user: rogers — key-based only)"
echo "================================================================"

while true; do
    sleep 30
done
