# Permasalahan

Ketika otomax / server hit ke api provider , kita mendapat response yang tidak terstruktur dengan baik, sehingga sulit untuk diolah. Proyek ini bertujuan untuk mengatasi masalah tersebut dengan menyediakan parser yang dapat mengubah response API menjadi format yang lebih mudah dipahami dan digunakan.
apalagi dengan batasa SQL Server yang hanya 8000 karakter, sehingga kita perlu mengolah data tersebut menjadi lebih ringkas.

## Solusi

- Membuat parser yang dapat mengubah response API yang tidak terstruktur menjadi format yang lebih terstruktur dan mudah digunakan.
- Mengimplementasikan mekanisme untuk memecah data yang lebih besar dari 8000 karakter menjadi beberapa bagian yang lebih kecil dan dapat dikelola.
- tweaking response API agar lebih ringkas dan mudah dipahami.

## Cara Kerja

client:
    - request ke services ini
    - service akan melakukan request ke API provider
    - service akan mengolah response API yang diterima
    - service akan mengembalikan response yang telah diolah ke client

## Tech Stack

- Python >= 3.12 : Language yang digunakan untuk mengembangkan parser ini.
- pydantic >= 2.0 : validasi dan serialisasi data yang digunakan untuk memastikan bahwa data yang diterima dari API provider sesuai dengan format yang diharapkan.
- pydantic-settings >= 2.0 : untuk mengelola konfigurasi aplikasi.
- fastapi : framework web yang digunakan untuk membangun API.
- loguru : library untuk logging yang lebih baik dan mudah digunakan.
- uvicorn : server ASGI yang digunakan untuk menjalankan aplikasi FastAPI.
- pytest : framework pengujian yang digunakan untuk menguji aplikasi.
- uv : untuk mengelola dependensi dan lingkungan virtual.
- ruff : untuk linting kode Python.
- pylint : untuk linting kode Python.
- stack lain selengkap nya ada di [pyproject.toml](pyproject.toml)

## Instalasi

- Clone repository ini
- klik start.bat untuk menjalankan aplikasi
- pastikan UV sudah terinstall, karena akan ada uv sync yg akan menginstall dependensi yang diperlukan dan mengaktifkan virtual environment.

## konfigurasi

- untuk setup ada di .env, sistem settings sudah otomatis deteksi multi .env, jadi kita bisa membuat .env.local, .env.development, .env.production, dll sesuai dengan kebutuhan kita.

## TOS

- segala kerugian , kesalahan, bug, dan lain-lain yang terjadi akibat penggunaan project ini adalah tanggung jawab pengguna.
- jangan install / deploy ke production tanpa melakukan testing terlebih dahulu.
- project ini di tujukan hanya untuk komunikasi antara localhost dalam network lokal, jadi jangan gunakan untuk komunikasi antar server yang berbeda.
- jika anda install di public server , pastikan anda sudah melakukan konfigurasi yang benar dan aman.
