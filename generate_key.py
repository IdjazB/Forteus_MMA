import streamlit_authenticator as stauth
import yaml

passwords_to_hash = ['XXX', 'XXX']

hasher = stauth.Hasher(passwords_to_hash)
hashed_passwords = hasher.generate()

# Save hashed passwords to a YAML file
with open("hashed_passwords.yaml", "w") as yaml_file:
    yaml.dump(hashed_passwords, yaml_file)