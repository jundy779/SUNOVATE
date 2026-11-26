"""Uji beban SUNOVATE: banyak pegawai simulasi memakai aplikasi bersamaan.

Setiap pengguna virtual masuk dengan akun simulasi, lalu berulang kali membuka Ringkasan,
Basis Pengetahuan, Pencarian, dan Monitoring Kerja dengan jeda acak seperti orang bekerja.
Sebagian pengguna juga bertanya satu kali ke SAVI AI. Di akhir, skrip mencetak kecepatan
(median, persentil 95, maksimum), jumlah gagal, dan jumlah permintaan yang ditolak pembatas
laju (429), lalu menyimpan laporan JSON.

Permintaan dikirim langsung ke API dari satu komputer. Itu sengaja: di server kantor semua
pegawai menghubungi API lewat server web yang sama, sehingga API juga melihat satu alamat.

Pelengkap `pnpm demo:load` (yang hanya memeriksa /health tanpa masuk). Target dibatasi ke
loopback secara bawaan, dengan aturan yang sama: IP privat hanya dengan --izinkan-ip-privat,
alamat publik dan nama host selain localhost selalu ditolak.

Jalankan dari folder repository (API harus sudah menyala):
    pnpm demo:workload --pengguna 25 --durasi 120
Hanya data contoh; tidak ada data yang diubah.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import statistics
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import httpx
from demo_load_test import validate_target

AKUN = [
    "sim.staff.pppsun@sunovate.local",
    "sim.lead.psun@sunovate.local",
    "sim.coordinator@sunovate.local",
    "sim.owner.ppsun@sunovate.local",
    "sim.reviewer.akpsun@sunovate.local",
]
KATA_CARI = ["metadata", "lelang", "regulasi", "setelmen", "dealer utama", "SUN ritel", "template"]
PERTANYAAN_SAVI = [
    "Apa metadata wajib saat mendaftarkan dokumen?",
    "Apa materi edukasi SUN ritel?",
]
AKSI = {
    "Ringkasan": ("GET", "/api/v1/dashboard/summary"),
    "Basis Pengetahuan": ("GET", "/api/v1/knowledge?pageSize=20"),
    "Pencarian": ("GET", "/api/v1/search"),
    "Monitoring Kerja": ("GET", "/api/v1/tasks?pageSize=50"),
}
BATAS_P95_MS = 1500
BATAS_GAGAL_PERSEN = 1.0


@dataclass
class Catatan:
    durasi_ms: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
    gagal: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    dibatasi: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    ditolak_akses: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def simpan(self, aksi: str, mulai: float, status: int | None) -> None:
        self.durasi_ms[aksi].append((time.perf_counter() - mulai) * 1000)
        if status == 429:
            self.dibatasi[aksi] += 1
        elif status in (401, 403):
            self.ditolak_akses[aksi] += 1
        elif status is None or status >= 400:
            self.gagal[aksi] += 1


def persentil(nilai: list[float], p: float) -> float:
    if not nilai:
        return 0.0
    urut = sorted(nilai)
    indeks = min(len(urut) - 1, max(0, round(p / 100 * (len(urut) - 1))))
    return urut[indeks]


async def kirim(
    client: httpx.AsyncClient, catatan: Catatan, aksi: str, metode: str, jalur: str, **kw: object
) -> None:
    mulai = time.perf_counter()
    try:
        respons = await client.request(metode, jalur, **kw)  # type: ignore[arg-type]
        catatan.simpan(aksi, mulai, respons.status_code)
    except httpx.HTTPError:
        catatan.simpan(aksi, mulai, None)


async def pengguna(
    nomor: int,
    client: httpx.AsyncClient,
    token: str,
    batas_waktu: float,
    jeda: tuple[float, float],
    tanya_savi: bool,
    catatan: Catatan,
) -> None:
    header = {"Authorization": f"Bearer {token}"}
    sisa = batas_waktu - time.perf_counter()
    waktu_savi = time.perf_counter() + random.uniform(5, max(6, sisa / 2))  # noqa: S311
    rng = random.Random(nomor)  # noqa: S311 - jeda acak, bukan keamanan
    await asyncio.sleep(rng.uniform(0, jeda[1]))  # pegawai tidak mulai pada detik yang sama
    while time.perf_counter() < batas_waktu:
        if tanya_savi and time.perf_counter() >= waktu_savi:
            tanya_savi = False
            await kirim(
                client,
                catatan,
                "SAVI AI",
                "POST",
                "/api/v1/hermes/query",
                headers=header,
                json={"question": rng.choice(PERTANYAAN_SAVI)},
                timeout=300,
            )
            continue
        aksi = rng.choice(list(AKSI))
        metode, jalur = AKSI[aksi]
        params = {"q": rng.choice(KATA_CARI)} if aksi == "Pencarian" else None
        await kirim(client, catatan, aksi, metode, jalur, headers=header, params=params, timeout=60)
        await asyncio.sleep(rng.uniform(*jeda))


async def jalankan(args: argparse.Namespace) -> int:
    async with httpx.AsyncClient(
        base_url=args.alamat, limits=httpx.Limits(max_connections=args.pengguna + 10)
    ) as client:
        try:
            sehat = (await client.get("/api/v1/health", timeout=10)).json()["data"]["status"]
        except (httpx.HTTPError, KeyError, ValueError):
            sehat = None
        if sehat != "ok":
            print(f"API di {args.alamat} belum menyala. Nyalakan SUNOVATE dulu.")
            return 2
        token: dict[str, str] = {}
        for email in AKUN:
            respons = await client.post("/api/v1/auth/dev/login", json={"email": email}, timeout=30)
            if respons.status_code != 200:
                print(f"Gagal masuk sebagai {email}: status {respons.status_code}")
                return 2
            token[email] = respons.json()["data"]["accessToken"]

        catatan = Catatan()
        mulai = time.perf_counter()
        batas = mulai + args.durasi
        print(
            f"Menjalankan {args.pengguna} pengguna selama {args.durasi} detik "
            f"({args.savi} di antaranya bertanya ke SAVI AI sekali)..."
        )
        await asyncio.gather(
            *(
                pengguna(
                    i,
                    client,
                    token[AKUN[i % len(AKUN)]],
                    batas,
                    (args.jeda_min, args.jeda_maks),
                    i < args.savi,
                    catatan,
                )
                for i in range(args.pengguna)
            )
        )
        lama = time.perf_counter() - mulai

    ringkasan: dict[str, dict[str, float | int]] = {}
    total = sum(len(v) for v in catatan.durasi_ms.values())
    print()
    print(
        f"{'Aksi':<18}{'Jumlah':>8}{'Gagal':>7}{'429':>6}{'Akses':>7}{'Median':>9}{'P95':>9}{'Maks':>9}"
    )
    for aksi in [*AKSI, "SAVI AI"]:
        d = catatan.durasi_ms.get(aksi, [])
        if not d:
            continue
        baris = {
            "jumlah": len(d),
            "gagal": catatan.gagal[aksi],
            "dibatasi_429": catatan.dibatasi[aksi],
            "ditolak_akses": catatan.ditolak_akses[aksi],
            "median_ms": round(statistics.median(d)),
            "p95_ms": round(persentil(d, 95)),
            "maks_ms": round(max(d)),
        }
        ringkasan[aksi] = baris
        print(
            f"{aksi:<18}{baris['jumlah']:>8}{baris['gagal']:>7}{baris['dibatasi_429']:>6}"
            f"{baris['ditolak_akses']:>7}{baris['median_ms']:>7}ms{baris['p95_ms']:>7}ms{baris['maks_ms']:>7}ms"
        )

    biasa = [v for k, v in catatan.durasi_ms.items() if k != "SAVI AI" for v in v]
    gagal = sum(catatan.gagal.values())
    dibatasi = sum(catatan.dibatasi.values())
    p95_biasa = persentil(biasa, 95)
    persen_gagal = 100 * gagal / total if total else 0.0
    layak = p95_biasa <= BATAS_P95_MS and persen_gagal < BATAS_GAGAL_PERSEN and dibatasi == 0
    print()
    print(f"Total {total} permintaan dalam {lama:.0f} detik ({total / lama * 60:.0f} per menit).")
    print(
        f"Halaman biasa: P95 {p95_biasa:.0f} ms (batas {BATAS_P95_MS} ms); "
        f"gagal {persen_gagal:.1f}% (batas {BATAS_GAGAL_PERSEN}%); "
        f"ditolak pembatas laju {dibatasi}."
    )
    if dibatasi:
        print(
            "Ada permintaan yang ditolak pembatas laju (429). Semua pegawai di server kantor "
            "terbaca sebagai satu alamat, jadi batas gabungan API_GLOBAL_RATE_LIMIT "
            "(bawaan 600/menit) "
            "perlu dinaikkan di .env server."
        )
    print(
        "KESIMPULAN: "
        + ("LAYAK untuk beban ini." if layak else "BELUM LAYAK; lihat angka di atas.")
    )

    laporan = {
        "waktu": datetime.now().isoformat(timespec="seconds"),
        "alamat": args.alamat,
        "pengguna": args.pengguna,
        "durasi_detik": args.durasi,
        "pengguna_savi": args.savi,
        "jeda_detik": [args.jeda_min, args.jeda_maks],
        "total_permintaan": total,
        "permintaan_per_menit": round(total / lama * 60),
        "p95_halaman_biasa_ms": round(p95_biasa),
        "persen_gagal": round(persen_gagal, 2),
        "dibatasi_429": dibatasi,
        "layak": layak,
        "per_aksi": ringkasan,
    }
    folder = (
        Path(args.keluaran)
        if args.keluaran
        else (Path.home() / "Desktop" if (Path.home() / "Desktop").is_dir() else Path.cwd())
    )
    berkas = folder / f"SUNOVATE-uji-beban-{datetime.now():%Y%m%d-%H%M%S}.json"
    berkas.write_text(json.dumps(laporan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Laporan disimpan di: {berkas}")
    return 0 if layak else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Uji beban SUNOVATE dengan pegawai simulasi.")
    parser.add_argument("--alamat", default="http://127.0.0.1:8000")
    parser.add_argument("--pengguna", type=int, default=25)
    parser.add_argument("--durasi", type=int, default=120, help="detik")
    parser.add_argument(
        "--savi", type=int, default=3, help="jumlah pengguna yang bertanya ke SAVI sekali"
    )
    parser.add_argument("--jeda-min", type=float, default=2.0)
    parser.add_argument("--jeda-maks", type=float, default=5.0)
    parser.add_argument("--keluaran", default="", help="folder laporan; bawaan Desktop")
    parser.add_argument("--izinkan-ip-privat", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.pengguna <= 200 or args.durasi < 10 or args.savi > args.pengguna:
        parser.error(
            "pengguna 1-200, durasi minimal 10 detik, dan savi tidak boleh melebihi pengguna"
        )
    try:
        validate_target(args.alamat, allow_private_target=args.izinkan_ip_privat)
    except ValueError as exc:
        parser.error(str(exc))
    return asyncio.run(jalankan(args))


if __name__ == "__main__":
    raise SystemExit(main())
