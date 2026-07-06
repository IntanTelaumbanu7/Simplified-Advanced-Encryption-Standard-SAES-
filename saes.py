SBOX = [0x9,0x4,0xA,0xB,0xD,0x1,0x8,0x5,0x6,0x2,0x0,0x3,0xC,0xE,0xF,0x7]
INV_SBOX = [0xA,0x5,0x9,0xB,0x1,0x7,0x8,0xF,0x6,0x0,0x2,0x3,0xC,0x4,0xD,0xE]
RCON1 = 0x80
RCON2 = 0x30


def b(n, width=4):
    return format(n, f'0{width}b')

def h(n, width=1):
    return format(n, f'0{width}X')

def bits_to_int(bits):
    return int(bits, 2)

def int_to_bits(value, width=16):
    return format(value & ((1 << width) - 1), f'0{width}b')

def split_nibbles16(x):
    return [(x >> 12) & 0xF, (x >> 8) & 0xF, (x >> 4) & 0xF, x & 0xF]

def nibbles_to_int(ns):
    return ((ns[0] & 0xF) << 12) | ((ns[1] & 0xF) << 8) | ((ns[2] & 0xF) << 4) | (ns[3] & 0xF)

def int_to_state(x):
    n = split_nibbles16(x)
    return [[n[0], n[2]], [n[1], n[3]]]  # kolom: [n0,n1] dan [n2,n3]

def state_to_int(s):
    return ((s[0][0]&0xF)<<12) | ((s[1][0]&0xF)<<8) | ((s[0][1]&0xF)<<4) | (s[1][1]&0xF)

def state_to_hex(s):
    return [[h(c) for c in row] for row in s]

def state_to_bin(s):
    return [[b(c) for c in row] for row in s]

def xor_state_key(s, key16):
    k = int_to_state(key16)
    return [[s[r][c] ^ k[r][c] for c in range(2)] for r in range(2)]

def sub_word(byte):
    hi, lo = (byte >> 4) & 0xF, byte & 0xF
    return (SBOX[hi] << 4) | SBOX[lo]

def rot_word(byte):
    return ((byte & 0xF) << 4) | ((byte >> 4) & 0xF)

def key_expansion(key16):
    w0 = (key16 >> 8) & 0xFF
    w1 = key16 & 0xFF
    rw1 = rot_word(w1); sw1 = sub_word(rw1)
    w2 = w0 ^ sw1 ^ RCON1
    w3 = w2 ^ w1
    rw3 = rot_word(w3); sw3 = sub_word(rw3)
    w4 = w2 ^ sw3 ^ RCON2
    w5 = w4 ^ w3
    keys = [(w0 << 8) | w1, (w2 << 8) | w3, (w4 << 8) | w5]
    steps = {
        'w0': b(w0,8), 'w1': b(w1,8), 'rot_w1': b(rw1,8), 'sub_rot_w1': b(sw1,8),
        'w2_calc': f'{b(w0,8)} XOR {b(sw1,8)} XOR {b(RCON1,8)} = {b(w2,8)}',
        'w2': b(w2,8), 'w3_calc': f'{b(w2,8)} XOR {b(w1,8)} = {b(w3,8)}', 'w3': b(w3,8),
        'rot_w3': b(rw3,8), 'sub_rot_w3': b(sw3,8),
        'w4_calc': f'{b(w2,8)} XOR {b(sw3,8)} XOR {b(RCON2,8)} = {b(w4,8)}',
        'w4': b(w4,8), 'w5_calc': f'{b(w4,8)} XOR {b(w3,8)} = {b(w5,8)}', 'w5': b(w5,8),
        'K0': b(keys[0],16), 'K1': b(keys[1],16), 'K2': b(keys[2],16),
        'K0_hex': h(keys[0],4), 'K1_hex': h(keys[1],4), 'K2_hex': h(keys[2],4)
    }
    return keys, steps

def gf_mul(a, c):
    res = 0
    aa = a
    cc = c
    for _ in range(4):
        if cc & 1:
            res ^= aa
        carry = aa & 0x8
        aa = (aa << 1) & 0xF
        if carry:
            aa ^= 0x3  # reduksi dari x^4 = x+1 (0x13 -> 0x3 setelah buang bit x^4)
        cc >>= 1
    return res & 0xF

def gf_expr(a, c):
    return f'{h(c)}×{h(a)} = {h(gf_mul(a,c))} ({b(c)}×{b(a)} → {b(gf_mul(a,c))})'

def sub_nibbles(s, inv=False):
    box = INV_SBOX if inv else SBOX
    return [[box[s[r][c]] for c in range(2)] for r in range(2)]

def sub_details(before, after):
    out=[]
    for r in range(2):
        for c in range(2):
            out.append(f'{h(before[r][c])}({b(before[r][c])}) → {h(after[r][c])}({b(after[r][c])})')
    return out

def shift_rows(s):
    return [[s[0][0], s[0][1]], [s[1][1], s[1][0]]]

def inv_shift_rows(s):
    return shift_rows(s)  # untuk 2 kolom, geser kiri/kanan 1 hasilnya sama

def mix_columns(s, inv=False):
    if inv:
        m = [[9,2],[2,9]]
    else:
        m = [[1,4],[4,1]]
    out = [[0,0],[0,0]]
    details=[]
    for c in range(2):
        a0, a1 = s[0][c], s[1][c]
        out[0][c] = gf_mul(a0,m[0][0]) ^ gf_mul(a1,m[0][1])
        out[1][c] = gf_mul(a0,m[1][0]) ^ gf_mul(a1,m[1][1])
        details.append(f'Kolom {c+1} atas: ({gf_expr(a0,m[0][0])}) XOR ({gf_expr(a1,m[0][1])}) = {h(out[0][c])} ({b(out[0][c])})')
        details.append(f'Kolom {c+1} bawah: ({gf_expr(a0,m[1][0])}) XOR ({gf_expr(a1,m[1][1])}) = {h(out[1][c])} ({b(out[1][c])})')
    return out, details

def add_step(steps, title, before, after, notes=None, key=None):
    steps.append({'title': title, 'before': state_to_bin(before), 'after': state_to_bin(after),
                  'before_hex': state_to_hex(before), 'after_hex': state_to_hex(after),
                  'notes': notes or [], 'key': b(key,16) if key is not None else None})

def encrypt(plain_bits, key_bits):
    p = bits_to_int(plain_bits); k = bits_to_int(key_bits)
    keys, ksteps = key_expansion(k)
    steps=[]
    s0 = int_to_state(p)
    s1 = xor_state_key(s0, keys[0]); add_step(steps, 'Initial AddRoundKey dengan K0', s0, s1, [f'{b(p,16)} XOR {b(keys[0],16)} = {b(state_to_int(s1),16)}'], keys[0])
    b1=s1; a1=sub_nibbles(b1); add_step(steps,'Round 1 - SubNibbles',b1,a1,sub_details(b1,a1))
    b2=a1; a2=shift_rows(b2); add_step(steps,'Round 1 - ShiftRows',b2,a2,['Baris kedua digeser 1 nibble ke kiri.'])
    b3=a2; a3, det=mix_columns(b3); add_step(steps,'Round 1 - MixColumns',b3,a3,det)
    b4=a3; a4=xor_state_key(b4,keys[1]); add_step(steps,'Round 1 - AddRoundKey K1',b4,a4,[f'{b(state_to_int(b4),16)} XOR {b(keys[1],16)} = {b(state_to_int(a4),16)}'],keys[1])
    b5=a4; a5=sub_nibbles(b5); add_step(steps,'Round 2 - SubNibbles',b5,a5,sub_details(b5,a5))
    b6=a5; a6=shift_rows(b6); add_step(steps,'Round 2 - ShiftRows',b6,a6,['Round final tidak memakai MixColumns.'])
    b7=a6; a7=xor_state_key(b7,keys[2]); add_step(steps,'Round 2 - AddRoundKey K2',b7,a7,[f'{b(state_to_int(b7),16)} XOR {b(keys[2],16)} = {b(state_to_int(a7),16)}'],keys[2])
    out = state_to_int(a7)
    return {'mode':'encrypt','input':plain_bits,'key':key_bits,'result_bin':b(out,16),'result_hex':h(out,4),'key_expansion':ksteps,'steps':steps}

def decrypt(cipher_bits, key_bits):
    c = bits_to_int(cipher_bits); k = bits_to_int(key_bits)
    keys, ksteps = key_expansion(k)
    steps=[]
    s0=int_to_state(c)
    s1=xor_state_key(s0,keys[2]); add_step(steps,'Dekripsi - Initial AddRoundKey K2',s0,s1,[f'{b(c,16)} XOR {b(keys[2],16)} = {b(state_to_int(s1),16)}'],keys[2])
    b1=s1; a1=inv_shift_rows(b1); add_step(steps,'Inverse Round 1 - InvShiftRows',b1,a1,['Pada matrix 2 kolom, geser kanan/kiri 1 nibble menghasilkan posisi tertukar.'])
    b2=a1; a2=sub_nibbles(b2,inv=True); add_step(steps,'Inverse Round 1 - InvSubNibbles',b2,a2,sub_details(b2,a2))
    b3=a2; a3=xor_state_key(b3,keys[1]); add_step(steps,'Inverse Round 1 - AddRoundKey K1',b3,a3,[f'{b(state_to_int(b3),16)} XOR {b(keys[1],16)} = {b(state_to_int(a3),16)}'],keys[1])
    b4=a3; a4,det=mix_columns(b4,inv=True); add_step(steps,'Inverse Round 1 - InvMixColumns',b4,a4,det)
    b5=a4; a5=inv_shift_rows(b5); add_step(steps,'Inverse Round 2 - InvShiftRows',b5,a5,['Final inverse round tidak memakai InvMixColumns setelah AddRoundKey K0.'])
    b6=a5; a6=sub_nibbles(b6,inv=True); add_step(steps,'Inverse Round 2 - InvSubNibbles',b6,a6,sub_details(b6,a6))
    b7=a6; a7=xor_state_key(b7,keys[0]); add_step(steps,'Inverse Round 2 - AddRoundKey K0',b7,a7,[f'{b(state_to_int(b7),16)} XOR {b(keys[0],16)} = {b(state_to_int(a7),16)}'],keys[0])
    out=state_to_int(a7)
    return {'mode':'decrypt','input':cipher_bits,'key':key_bits,'result_bin':b(out,16),'result_hex':h(out,4),'key_expansion':ksteps,'steps':steps}
