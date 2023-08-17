import hashlib

def sha256_hash_with_salt(password, salt):
    salted_password = password + salt
    hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
    return hashed_password

# Example usage:
password = input("Password: ")
salt = "DF2B0862F89FFA3E367A656EB422F1A32DA03F4AD2A6D04ADA08977D40CDE360"
hashed_password = sha256_hash_with_salt(password, salt)
print(hashed_password)