from flask import Flask, render_template, request
from saes import encrypt, decrypt, SBOX, INV_SBOX

app = Flask(__name__)

def valid_bits(x):
    return len(x) == 16 and all(ch in '01' for ch in x)

@app.route('/', methods=['GET','POST'])
def index():
    result = None
    error = None
    data = {'text':'1101011100101000', 'key':'0100101011110101', 'mode':'encrypt'}
    if request.method == 'POST':
        data['text'] = request.form.get('text','').strip().replace(' ','')
        data['key'] = request.form.get('key','').strip().replace(' ','')
        data['mode'] = request.form.get('mode','encrypt')
        if not valid_bits(data['text']) or not valid_bits(data['key']):
            error = 'Input plaintext/ciphertext dan kunci wajib biner 16-bit, hanya boleh 0 dan 1.'
        else:
            result = encrypt(data['text'], data['key']) if data['mode'] == 'encrypt' else decrypt(data['text'], data['key'])
    return render_template('index.html', data=data, result=result, error=error,
                           sbox=[format(x,'X') for x in SBOX], inv_sbox=[format(x,'X') for x in INV_SBOX])

if __name__ == '__main__':
    app.run(debug=True)
