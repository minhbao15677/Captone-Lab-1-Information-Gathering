FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    samba \
    samba-common-bin \
    smbclient \
    vsftpd \
    openssh-server \
    sudo \
    python3 \
    python3-pip \
    python3-reportlab \
    net-tools \
    iputils-ping \
    vim \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Users ────────────────────────────────────────────────────────────────────
# andrew : FTP only (no SSH), no write, .bash_history reveals id_rsa path
# rogers : SSH only via private key (no password auth), holds proof.txt
RUN useradd -m -s /bin/bash andrew && echo "andrew:Welc0me@2024!" | chpasswd
RUN useradd -m -s /bin/bash rogers && echo "rogers:$(openssl rand -hex 32)" | chpasswd

# rogers cannot login with password — key only
# andrew cannot login via SSH (AllowUsers in sshd_config only lists rogers)

# ── rogers SSH key pair ───────────────────────────────────────────────────────
RUN mkdir -p /home/rogers/.ssh
RUN ssh-keygen -t rsa -b 2048 -f /tmp/rogers_rsa -N "" -C "rogers@labsrv"
RUN cp /tmp/rogers_rsa.pub /home/rogers/.ssh/authorized_keys
RUN chmod 700 /home/rogers/.ssh && chmod 600 /home/rogers/.ssh/authorized_keys
RUN chown -R rogers:rogers /home/rogers/.ssh

# Store private key in a path andrew sees in his FTP session (world-readable subdir)
RUN mkdir -p /opt/backups/keys
RUN cp /tmp/rogers_rsa /opt/backups/keys/rogers_rsa
RUN chmod 644 /opt/backups/keys/rogers_rsa
RUN chown root:root /opt/backups/keys/rogers_rsa
RUN rm /tmp/rogers_rsa /tmp/rogers_rsa.pub

# ── proof.txt ─────────────────────────────────────────────────────────────────
COPY flags/proof.txt /home/rogers/proof.txt
RUN chown rogers:rogers /home/rogers/proof.txt && chmod 600 /home/rogers/proof.txt

# ── SMB shared folder ─────────────────────────────────────────────────────────
RUN mkdir -p /srv/smb/Shared
RUN chmod 755 /srv/smb/Shared

# ── andrew's FTP home & .bash_history ────────────────────────────────────────
# .bash_history leaks the path to rogers_rsa
RUN printf \
    "ls\npwd\nftp localhost\ncd /opt/backups/keys\nls -la\nget rogers_rsa /tmp/rogers_rsa\nexit\n" \
    > /home/andrew/.bash_history
RUN chown andrew:andrew /home/andrew/.bash_history && chmod 600 /home/andrew/.bash_history

# andrew cannot write to his own home via FTP (enforced by vsftpd write_enable=NO)

# ── Generate PDFs at build time ───────────────────────────────────────────────
COPY scripts/gen_pdfs.py /tmp/gen_pdfs.py
RUN python3 /tmp/gen_pdfs.py /srv/smb/Shared
RUN chmod 644 /srv/smb/Shared/*.pdf

# ── Config files ─────────────────────────────────────────────────────────────
COPY config/smb/smb.conf        /etc/samba/smb.conf
COPY config/ftp/vsftpd.conf     /etc/vsftpd.conf
COPY config/ftp/vsftpd.userlist /etc/vsftpd.userlist
COPY config/ssh/sshd_config     /etc/ssh/sshd_config
COPY config/ssh/banner.txt      /etc/ssh/banner.txt

# SSH host keys
RUN ssh-keygen -A

# Samba runtime dirs
RUN mkdir -p /var/run/samba /var/log/samba

# ── Entrypoint ───────────────────────────────────────────────────────────────
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 21 22 139 445

ENTRYPOINT ["/entrypoint.sh"]
