# Classic RPG 2D Game - Python Pygame Version

Game RPG pixel 2D klasik yang dibuat dengan Python dan Pygame.

## Fitur

- **Map System**: Load map dari file PNG atau generate default map
- **Character Animation**: 
  - Animasi idle (idle1.png, idle2.png)
  - Animasi berjalan (walk1.png, walk2.png)
- **Smooth Movement**: Pergerakan karakter smooth dengan 4 arah
- **Camera System**: Kamera mengikuti player
- **Pixel Art Style**: Grafis pixel art klasik

## Requirements

- Python 3.7 atau lebih baru
- Pygame 2.5.0 atau lebih baru

## Cara Install dan Jalankan

### 1. Install Python
Download dan install Python dari: https://www.python.org/
(Pastikan centang "Add Python to PATH" saat install)

### 2. Install Pygame
```bash
pip install pygame
```

Atau install dari requirements.txt:
```bash
pip install -r requirements.txt
```

### 3. Siapkan Assets (Opsional)

#### Sprite Karakter (16x16 pixels):
- `idle1.png` - Posisi idle frame 1
- `idle2.png` - Posisi idle frame 2
- `walk1.png` - Posisi jalan frame 1
- `walk2.png` - Posisi jalan frame 2

Jika file tidak ada, game akan generate sprite sederhana otomatis.

#### Map (Opsional):
- `map.png` - File map dalam format PNG

Jika file tidak ada, game akan generate map default 30x20 tiles.

### 4. Jalankan Game

**Windows:**
```bash
run_game.bat
```

Atau:
```bash
python main.py
```

**Linux/Mac:**
```bash
python3 main.py
```

## Kontrol

- **Arrow Keys** atau **WASD** - Gerakkan karakter
- **ESC** - Keluar dari game

## Struktur File

```
jam/
├── main.py              # File utama game (Python)
├── requirements.txt     # Dependencies Python
├── run_game.bat        # Script untuk jalankan game (Windows)
├── map.png             # Map file (opsional)
├── idle1.png           # Sprite idle frame 1 (opsional)
├── idle2.png           # Sprite idle frame 2 (opsional)
├── walk1.png           # Sprite jalan frame 1 (opsional)
└── walk2.png           # Sprite jalan frame 2 (opsional)
```

## Membuat Map PNG

Anda bisa membuat map menggunakan:

1. **Tiled Map Editor** (https://www.mapeditor.org/)
   - Buat map dengan ukuran 30x20 tiles (16x16 pixels per tile)
   - Export sebagai PNG

2. **Photoshop/GIMP/Paint.NET**
   - Buat image dengan ukuran 480x320 pixels (30x20 tiles @ 16px)
   - Gambar map sesuai keinginan
   - Save sebagai `map.png`

3. **Aseprite** (untuk pixel art)
   - Buat canvas 480x320
   - Gambar dengan pixel art style
   - Export sebagai PNG

## Customization

### Ubah Kecepatan Player
Di `main.py`, line ~33:
```python
'speed': 100,  # Ubah nilai ini (pixels per second)
```

### Ubah Kecepatan Animasi
Di `main.py`, line ~48:
```python
self.animation_speed = 0.3  # Ubah nilai ini (seconds per frame)
```

### Ubah Resolusi Window
Di `main.py`, line ~16-17:
```python
SCREEN_WIDTH = 800  # Lebar window
SCREEN_HEIGHT = 600  # Tinggi window
```

### Ubah Scale
Di `main.py`, line ~19:
```python
SCALE = 2  # 1=normal, 2=2x zoom, 3=3x zoom
```

## Konversi Map dari Lua ke PNG

Untuk mengkonversi map dari format Tiled (Lua) ke PNG:

1. Buka file map di Tiled Map Editor
2. File → Export As Image
3. Pilih format PNG
4. Save sebagai `map.png` di folder game

## Tips

1. Map dan sprite otomatis di-scale sesuai SCALE setting
2. Game berjalan di 60 FPS
3. Camera otomatis mengikuti player
4. Debug info ditampilkan di pojok kiri atas

## Troubleshooting

**Error: pygame not found**
```bash
pip install pygame
```

**Error: No module named 'pygame'**
- Pastikan Python dan pip terinstall dengan benar
- Coba: `python -m pip install pygame`

**Game terlalu lambat**
- Kurangi nilai SCALE di main.py
- Pastikan driver grafis sudah update

**Sprite tidak muncul**
- Cek apakah file PNG ada di folder yang sama dengan main.py
- Cek ukuran sprite (harus 16x16 pixels)

**Map tidak muncul**
- Pastikan map.png ada di folder yang sama
- Atau biarkan kosong untuk menggunakan default map

## Pengembangan Lebih Lanjut

Fitur yang bisa ditambahkan:
- Collision detection dengan tiles
- NPCs dan dialog
- Inventory system
- Combat system
- Multiple maps
- Sound effects dan music
- Save/Load game

## License

Free to use and modify.
