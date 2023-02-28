import dotenv
from Crypto.PublicKey import RSA  # provided by pycryptodome
try:
    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)
    key = RSA.generate(4096)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    # Write changes to .env file.
    dotenv.set_key(dotenv_file, "PRIVATE_KEY", private_key.decode())
    dotenv.set_key(dotenv_file, "PUBLIC_KEY", public_key.decode())

    print('PRIVATE AND PUBLIC KEYS were successfully generated and added in environment variables')
except FileNotFoundError:
    print("No .env file found")
