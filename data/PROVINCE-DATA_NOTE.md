# Data note / Catatan data

- `ep_*`  : Energy Poverty = Simulasi EnergyPlus − konsumsi ternormalisasi RUPTL
           (kWh/pelanggan/tahun). Positif = kebutuhan pendinginan belum terpenuhi.
           Konvensi delta: dEP = ep_2025 − ep_2050 (positif = kesenjangan MENYEMPIT).
- `ur_*`  : Rasio urbanisasi (%), sumber statistik publik.
- `cdd_*` : Cooling Degree Days, metode hourly, basis 25 °C (2050: morphing SSP2-4.5).
- YANG TIDAK DIPUBLIKASIKAN: tabel RUPTL mentah per provinsi, keluaran mentah
  EnergyPlus per provinsi, dan proyeksi RUPTL 2050 (masih bagian dari dataset tesis
  yang belum selesai divalidasi). Seluruh hasil klaster pada repositori ini dapat
  direproduksi penuh dari berkas ini karena EP sudah memuat selisih Sim − RUPTL.
- Dikenal artefak: (1) Bali, Sumatera Selatan, DIY membawa anomali proyeksi CAGR
  RUPTL; (2) Jawa Barat & DIY membawa bias EPW dataran tinggi pada CDD.
  Keduanya diperlakukan sebagai klaster anomali, bukan regime populasi.