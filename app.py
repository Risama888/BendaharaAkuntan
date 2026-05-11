
import requests
from flask import Flask, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# Konfigurasi API WhatsApp
API_URL = 'https://api.fonnte.com/send'
TOKEN = 'XR5pM62abT79zu1QstSa'
TARGET_NUMBER = '085817824127'

# Konfigurasi Supabase
SUPABASE_URL = 'https://eqkenuzuhgmewirhgseg.supabase.co/rest/v1/signals'  # Ganti dengan URL project Supabase Anda
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVxa2VudXp1aGdtZXdpcmhnc2VnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4OTgzNzgsImV4cCI6MjA3NDQ3NDM3OH0.YKLdjMnNatSQMmZ3zgVumiMpNH2GS4KOb66Th0__mcU'  # Ganti dengan anon key Anda
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Saldo awal
saldo_awal = 2650000

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

def proses_keuangan():
    global saldo_awal
    # Ambil data terbaru dari Supabase
    data_keuangan = supabase.table('keuangan').select('*').order('created_at', desc=True).limit(1).execute()

    if data_keuangan.data:
        pemasukan = data_keuangan.data[0].get('pemasukan', 0)
        pengeluaran = data_keuangan.data[0].get('pengeluaran', 0)
    else:
        pemasukan = 0
        pengeluaran = 0

    saldo_terbaru, persen_pemasukan, persen_pengeluaran = update_saldo(saldo_awal, pemasukan, pengeluaran)
    saldo_awal = saldo_terbaru  # update saldo global

    hasil_kirim = kirim_pesan(saldo_terbaru, persen_pemasukan, persen_pengeluaran, pemasukan, pengeluaran)
    print(hasil_kirim)

# Jika ingin menjalankan proses secara otomatis saat script dieksekusi
if __name__ == '__main__':
    proses_keuangan()
    # Jika ingin menjalankan secara otomatis setiap interval tertentu, bisa pakai scheduler
