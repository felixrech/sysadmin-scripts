import ssl
import sys
import time
from imaplib import IMAP4
from smtplib import SMTP, SMTPRecipientsRefused

sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import get_process_output, get_process_returncode  # noqa # pylint: disable=import-error
from test_helpers import set_log_length, print_log, print_check, print_crit_check  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary  # noqa # pylint: disable=import-error

default = "rech@psa-team10.in.tum.de"
server = "mail.psa-team10.in.tum.de"
user = "rech"
pw = "UrineHelenaBovineMacroHodgePushy"
context = ssl.SSLContext(ssl.PROTOCOL_TLS)

set_log_length(60)


def is_port_open(ip, port):
    cmd = f"nc -w5 -z {ip} {port}"
    return get_process_returncode(cmd) == 0


def send_mail(smtp, msg, from_addr=default, to_addr=default):
    try:
        smtp.sendmail(from_addr=from_addr, to_addrs=to_addr, msg=msg)
        return True
    except SMTPRecipientsRefused:
        return False


def email_received(imap, msg, limit_from_addr_to=None):
    imap.close()
    imap.select()
    if limit_from_addr_to is None:
        _, data = imap.search(None, 'ALL')
    else:
        _, data = imap.search(None, 'FROM', limit_from_addr_to)
    msgs = [imap.fetch(n, '(UID BODY[TEXT])') for n in data[0].split()[-10:]]
    msgs = [msg[1][0][1].decode('utf-8') for msg in msgs]
    return any(rmsg for rmsg in msgs if msg in rmsg)


print_log("[Firewall] Port  25 (SMTP) open")
print_crit_check(is_port_open(server, 25))

print_log("[Firewall] Port 143 (IMAP) open")
print_crit_check(is_port_open(server, 143))
print()


print_log("[IMAP] Connection possible")
try:
    imap = IMAP4(host=server)
    print_check('OK' in imap.noop())
except IMAP4.error:
    print_crit_check(False)

print_log("[IMAP] STARTTLS successful")
print_crit_check('OK' in imap.starttls(ssl_context=context))

print_log("[IMAP] Successful authentication")
print_crit_check('OK' in imap.login(user, pw))

print_log("[IMAP] Opening INBOX")
print_crit_check('OK' in imap.select())

print_log("[IMAP] Can read e-mails")
secret = b'This is a test mailing\r\n\r\n'
typ, data = imap.fetch(b'1', '(UID BODY[TEXT])')
print_crit_check(typ == 'OK' and data[0][1] == secret)
print()

print_log("[SMTP] Connection possible")
try:
    smtp = SMTP(server, port=25)
    print_check(250 in smtp.ehlo() and 250 in smtp.noop())
except:
    print_crit_check(False)

print_log("[SMTP] STARTTLS successful")
print_crit_check(220 in smtp.starttls(context=context) and 250 in smtp.ehlo())

print_log("[SMTP] Successful authentication")
print_crit_check(235 in smtp.login(user, pw))
print()


print_log("[CONFIG] rech@psa... -> rech@psa... sending")
ts = str(int(time.time()))
print_check(send_mail(smtp, f"rech-rech-{ts}"))

print_log("[CONFIG] e-mail also received")
time.sleep(5)
print_check(email_received(imap, f"rech-rech-{ts}"))

print_log("[CONFIG] rech@vm1.psa... -> rech@psa... sending")
print_check(send_mail(smtp, f"vm-rech-{ts}",
                      from_addr="rech@vm1.psa-team10.in.tum.de"))

print_log("[CONFIG] e-mail also received (as from rech@psa...)")
time.sleep(5)
print_check(email_received(imap, f"vm-rech-{ts}",
                           limit_from_addr_to=default))

print_log("[CONFIG] rech@psa... -> mail@remote... sending")
print_check(send_mail(smtp, f"rech-remote-{ts}",
                      to_addr="spam@google.com"))

print_log("[CONFIG] rech@psa... -> nonexistent@psa... rejected")
print_check(not send_mail(smtp, f"rech-remote-{ts}",
                          to_addr="nonexistent@psa-team10.in.tum.de"))

print_log("[CONFIG] Unauthorized rejected")
smtp_unauth = SMTP(server, port=25)
smtp_unauth.ehlo()
smtp_unauth.starttls(context=context)
smtp_unauth.ehlo()
rc = send_mail(smtp_unauth, f"unauth-{ts}", to_addr='spam@google.com')
print_check(not rc)

# Close connections
imap.close()
imap.logout()
smtp.quit()
smtp_unauth.quit()

print_test_summary()
