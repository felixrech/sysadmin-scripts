# No tracking on port 80 or 443 packets
iptables -t raw -A PREROUTING -p tcp --match multiport --dport 80,443 -j NOTRACK
iptables -t raw -A OUTPUT -p tcp --match multiport --dport 80,443 -j NOTRACK
# Allow DNS traffic
iptables -t filter -A OUTPUT -p udp --dport domain -j ACCEPT
iptables -t filter -A INPUT -p udp --sport domain -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
# Allow incoming SSH
iptables -t filter -A INPUT -p tcp --dport ssh -j ACCEPT
iptables -t filter -A OUTPUT -p tcp --sport ssh -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
# Allow outgoing SSH
iptables -t filter -A OUTPUT -p tcp --dport ssh -j ACCEPT
iptables -t filter -A INPUT -p tcp --sport ssh -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
# Allow incoming HTTP
iptables -t filter -A INPUT -p tcp --dport http -j ACCEPT
iptables -t filter -A OUTPUT -p tcp --sport http -j ACCEPT
# Allow incoming HTTPS
iptables -t filter -A INPUT -p tcp --dport https -j ACCEPT
iptables -t filter -A OUTPUT -p tcp --sport https -j ACCEPT
# Allow incoming from and outgoing to 192.168.0.0/16 (local praktikum network)
iptables -t filter -A INPUT -s 192.168.0.0/16 -j ACCEPT
iptables -t filter -A OUTPUT -d 192.168.0.0/16 -j ACCEPT
# Allow incoming from and outgoing to 131.159.0.0/16 (faculty network)
iptables -t filter -A INPUT -s 131.159.0.0/16 -j ACCEPT
iptables -t filter -A OUTPUT -d 131.159.0.0/16 -j ACCEPT
# Allow all ICMP traffic
iptables -t filter -A INPUT -p icmp -m limit --limit 2/s -j ACCEPT
iptables -t filter -A OUTPUT -p icmp -j ACCEPT
# Allow NTP traffic (ntp.ubuntu.com)
iptables -t filter -A OUTPUT -d ntp.ubuntu.com -p udp --dport ntp -j ACCEPT
iptables -t filter -A INPUT -s ntp.ubuntu.com -p udp --sport ntp -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
# Default to no incoming or outgoing packets
iptables -t filter -A INPUT -P DROP
iptables -t filter -A OUTPUT -P DROP
