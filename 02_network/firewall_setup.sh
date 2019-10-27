# No tracking on port 80 or 443 packets
iptables -t raw -i enp0s8 -A PREROUTING -p tcp --match multiport --dport 80,443 -j NOTRACK
iptables -t raw -o enp0s8 -A OUTPUT -p tcp --match multiport --dport 80,443 -j NOTRACK
# Allow DNS traffic
iptables -t filter -o enp0s8 -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -t filter -i enp0s8 -A INPUT -p udp --sport 53 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
# Allow incoming SSH
iptables -t filter -i enp0s8 -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -t filter -o enp0s8 -A OUTPUT -p tcp --sport 22 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
# Allow outgoing SSH
iptables -t filter -o enp0s8 -A OUTPUT -p tcp --dport 22 -j ACCEPT
iptables -t filter -i enp0s8 -A INPUT -p tcp --sport 22 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
# Allow incoming HTTP
iptables -t filter -i enp0s8 -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -t filter -o enp0s8 -A OUTPUT -p tcp --sport 80 -j ACCEPT
# Allow incoming HTTPS
iptables -t filter -i enp0s8 -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -t filter -o enp0s8 -A OUTPUT -p tcp --sport 443 -j ACCEPT
# Allow incoming from and outgoing to 192.168.0.0/16 (local praktikum network)
iptables -t filter -i enp0s8 -A INPUT -s 192.168.0.0/16 -j ACCEPT
iptables -t filter -o enp0s8 -A OUTPUT -d 192.168.0.0/16 -j ACCEPT
# Allow incoming from and outgoing to 131.159.0.0/16 (faculty network)
iptables -t filter -i enp0s8 -A INPUT -s 131.159.0.0/16 -j ACCEPT
iptables -t filter -o enp0s8 -A OUTPUT -d 131.159.0.0/16 -j ACCEPT
# Allow all ICMP traffic
iptables -t filter -i enp0s8 -A INPUT -p icmp -m limit --limit 2/s -j ACCEPT
iptables -t filter -o enp0s8 -A OUTPUT -p icmp -j ACCEPT
# Default to no incoming or outgoing packets
iptables -t filter -i enp0s8 -A INPUT -j DROP
iptables -t filter -o enp0s8 -A OUTPUT -j DROP
