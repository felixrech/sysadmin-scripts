# No tracking on port 80 or 443 packets
iptables -t raw -A PREROUTING -p tcp --dport 80 -j NOTRACK
iptables -t raw -A PREROUTING -p tcp --dport 443 -j NOTRACK
iptables -t raw -A OUTPUT -p tcp --sport 80 -j NOTRACK
iptables -t raw -A OUTPUT -p tcp --sport 443 -j NOTRACK
# Allow DNS traffic
iptables -t filter -A OUTPUT -p udp --dport domain -j ACCEPT
iptables -t filter -A INPUT -p udp --sport domain -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
# Allow incoming SSH
iptables -t filter -A INPUT -p tcp --dport ssh -j ACCEPT
iptables -t filter -A OUTPUT -p tcp --sport ssh -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
# Allow incoming HTTP
iptables -t filter -A INPUT -p tcp --dport http -j ACCEPT
iptables -t filter -A OUTPUT -p tcp --sport http -j ACCEPT
# Allow incoming HTTPS
iptables -t filter -A INPUT -p tcp --dport https -j ACCEPT
iptables -t filter -A OUTPUT -p tcp --sport https -j ACCEPT
# Allow outgoing HTTP(S) (connections to proxy.in.tum.de)
iptables -t filter -A INPUT -d proxy.in.tum.de -p tcp --sport 8080 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
iptables -t filter -A OUTPUT -s proxy.in.tum.de -p tcp --dport 8080 -j ACCEPT
# Allow incoming outgoing to 192.168.0.0/16 (local praktikum network)
iptables -t filter -A INPUT -s 192.168.0.0/16 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
iptables -t filter -A OUTPUT -d 192.168.0.0/16 -j ACCEPT
# Allow incoming outgoing to 131.159.0.0/16 (faculty network)
iptables -t filter -A INPUT -s 131.159.0.0/16 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
iptables -t filter -A OUTPUT -d 131.159.0.0/16 -j ACCEPT
# Allow OS upgrades
iptables -t filter -A INPUT -s de.archive.ubuntu.com -p tcp --sport http -j ACCEPT
iptables -t filter -A OUTPUT -d de.archive.ubuntu.com -p tcp --dport http -j ACCEPT
# Allow all ICMP traffic
iptables -t filter -A INPUT -p icmp -m limit --limit 2/s -j ACCEPT
iptables -t filter -A OUTPUT -p icmp -j ACCEPT
# Allow NTP traffic (ntp.ubuntu.com)
iptables -t filter -A OUTPUT -d ntp.ubuntu.com -p udp --dport ntp -j ACCEPT
iptables -t filter -A INPUT -s ntp.ubuntu.com -p udp --sport ntp -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
# Default to no incoming or outgoing packets
iptables -t filter -P INPUT DROP
iptables -t filter -P OUTPUT DROP
