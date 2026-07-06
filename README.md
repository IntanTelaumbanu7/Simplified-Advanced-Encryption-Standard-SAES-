# Web Simulasi S-AES 16-bit

Project Flask untuk simulasi Simplified AES sesuai spesifikasi tugas:
- Input plaintext/ciphertext 16-bit biner dan key 16-bit biner.
- Mode enkripsi/dekripsi.
- Output biner 16-bit dan heksadesimal.
- Step-by-step: Key Expansion, Initial AddRoundKey, Round 1, Round 2, dan InvCipher.
- Tabel S-Box, Inverse S-Box, MixColumns, InvMixColumns, RCON.
- Visualisasi state matrix 2x2 nibble.

## Jalankan lokal
```bash
pip install -r requirements.txt
python app.py
```
Buka: http://127.0.0.1:5000

## Deploy Vercel
Upload semua file ke GitHub, lalu import repository ke Vercel. File `vercel.json` sudah disediakan.
