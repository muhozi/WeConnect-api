from Crypto.PublicKey import RSA  # provided by pycryptodome

key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

print('private key:')
print(private_key.decode())
print('public key:')
print(public_key.decode())
