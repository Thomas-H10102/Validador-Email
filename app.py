from flask import Flask, request, jsonify, render_template
import re
import smtplib
import dns.resolver

app = Flask(__name__)

def is_valid_email_format(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def has_mx_record(domain):
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return len(mx_records) > 0
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        return False

def verify_email_smtp(email):
    try:
        domain = email.split('@')[1]
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(mx_records[0].exchange)

        server = smtplib.SMTP()
        server.set_debuglevel(0)
        server.connect(mx_record)
        server.helo(server.local_hostname)
        server.mail('me@mydomain.com')
        code, message = server.rcpt(email)
        server.quit()

        if code == 250:
            return True
        else:
            return False
    except Exception as e:
        return False

def is_valid_email(email):
    if not is_valid_email_format(email):
        return False

    domain = email.split('@')[1]
    if not has_mx_record(domain):
        return False

    if verify_email_smtp(email):
        return True
    else:
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        if is_valid_email(email):
            result = 'valid'
        else:
            result = 'invalid'
        return jsonify(result=result)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
