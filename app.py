import requests
from flask import Flask, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# Konfigurasi API WhatsApp
API_URL = 'https://api.fonnte.com/send'
TOKEN = 'XR5pM62abT79zu1QstSa'
TARGET_NUMBER = '085817824127'

# Konfigurasi Supabase
SUPABASE_URL = 'https://wpcyamuvtinjnhbnqlln.supabase.co'  # Ganti dengan URL project Supabase Anda
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndwY3lhbXV2dGluam5oYm5xbGxuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg1MDg0OTgsImV4cCI6MjA5NDA4NDQ5OH0.4JnPSMo9PPckUC8-LekUFaxKoo3OyoC5X0ysXFhdKA4'  # Ganti dengan anon key Anda
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Saldo awal
saldo_awal = 2650000

# Fungsi kirim pesan
def kirim_pesan(saldo, persen_pemasukan, persen_pengeluaran, pemasukan, pengeluaran):
    message = (
        f"Situasi Keuangan Saat Ini:\n"
        f"Saldo awal: Rp {saldo_awal:,}\n"
        f"Saldo saat ini: Rp {saldo:,}\n"
        f"Pemasukan: Rp {pemasukan:,} ({persen_pemasukan:.2f}%)\n"
        f"Pengeluaran: Rp {pengeluaran:,} ({persen_pengeluaran:.2f}%)"
    ).replace(',', '.')
    headers = {
        'Authorization': TOKEN
    }
    data = {
        'target': TARGET_NUMBER,
        'message': message,
        'countryCode': '62'
    }
    response = requests.post(API_URL, headers=headers, data=data)
    return response.text

def update_saldo(saldo, pemasukan=0, pengeluaran=0):
    saldo_baru = saldo + pemasukan - pengeluaran
    persen_pemasukan = (pemasukan / saldo_awal) * 100 if saldo_awal != 0 else 0
    persen_pengeluaran = (pengeluaran / saldo_awal) * 100 if saldo_awal != 0 else 0
    return saldo_baru, persen_pemasukan, persen_pengeluaran

# Fungsi untuk ambil data dari Supabase
def ambil_data_keuangan():
    data_keuangan = supabase.table('keuangan').select('*').order('created_at', desc=True).limit(1).execute()
    if data_keuangan.data:
        pemasukan = data_keuangan.data[0].get('pemasukan', 0)
        pengeluaran = data_keuangan.data[0].get('pengeluaran', 0)
    else:
        pemasukan = 0
        pengeluaran = 0
    return pemasukan, pengeluaran

# Contoh: Panggil fungsi ini saat startup atau sesuai kebutuhan
pemasukan, pengeluaran = ambil_data_keuangan()
saldo_terbaru, persen_pemasukan, persen_pengeluaran = update_saldo(saldo_awal, pemasukan, pengeluaran)

# Kirim pesan saat startup (opsional)
# hasil_kirim = kirim_pesan(saldo_terbaru, persen_pemasukan, persen_pengeluaran, pemasukan, pengeluaran)
# print(hasil_kirim)

@app.route('/some-endpoint', methods=['GET'])
def some_function():
    # Jika ingin mengambil data terbaru saat endpoint dipanggil
    pemasukan, pengeluaran = ambil_data_keuangan()
    saldo_terbaru, persen_pemasukan, persen_pengeluaran = update_saldo(saldo_awal, pemasukan, pengeluaran)
    hasil_kirim = kirim_pesan(saldo_terbaru, persen_pemasukan, persen_pengeluaran, pemasukan, pengeluaran)
    return jsonify({
        'status': 'success',
        'message': hasil_kirim,
        'saldo_terbaru': saldo_terbaru,
        'pemasukan': pemasukan,
        'pengeluaran': pengeluaran,
        'persen_pemasukan': persen_pemasukan,
        'persen_pengeluaran': persen_pengeluaran
    })

if __name__ == '__main__':
    app.run(debug=True)
