const STAGES = [
  { name: "Tangkap", detail: "Pengalaman, bahan rapat, dan catatan SME dikumpulkan." },
  { name: "Validasi", detail: "Sumber, pemilik, versi, dan klasifikasi diperiksa." },
  { name: "Organisasikan", detail: "Kategori, metadata, dan relasi antardokumen disusun." },
  { name: "Temukan", detail: "Pencarian mengikuti hak akses setiap pegawai." },
  { name: "Gunakan", detail: "SAVI AI menjawab dengan menyebut sumbernya." },
  { name: "Pelajari", detail: "Masukan dan pembaruan memperbaiki pengetahuan berikutnya." },
] as const;

/** Six points rising left to right: knowledge gains value as it moves through the cycle. */
const POINTS = STAGES.map((_, index) => ({ x: index * 100 + 50, y: 118 - index * 18 }));
const LINE = POINTS.map((point, index) => `${index ? "L" : "M"}${point.x} ${point.y}`).join(" ");

export function KnowledgeCycle() {
  return (
    <figure className="cycle" aria-labelledby="cycle-title">
      <header className="ed-head">
        <h2 id="cycle-title">Dari pengalaman menjadi rujukan</h2>
        <p>Tahapan yang dilalui setiap pengetahuan sebelum dipakai SAVI AI</p>
      </header>
      <svg className="cycle-chart" viewBox="0 0 600 150" role="presentation" aria-hidden="true">
        {[40, 80, 120].map((y) => <line className="cycle-grid" key={y} x1="0" x2="600" y1={y} y2={y} />)}
        <line className="cycle-axis" x1="0" x2="600" y1="140" y2="140" />
        <path className="cycle-line" d={LINE} pathLength={1} />
        {POINTS.map((point, index) => (
          <g className="cycle-point" key={point.x} style={{ animationDelay: `${0.35 + index * 0.22}s` }}>
            <circle
              className={index === POINTS.length - 1 ? "cycle-node cycle-node-final" : "cycle-node"}
              cx={point.x}
              cy={point.y}
              r="6"
            />
            <text className="cycle-number" x={point.x} y={point.y - 16}>{index + 1}</text>
          </g>
        ))}
      </svg>
      <ol className="cycle-stages">
        {STAGES.map((stage) => (
          <li key={stage.name}>
            <strong>{stage.name}</strong>
            <span>{stage.detail}</span>
          </li>
        ))}
      </ol>
      <figcaption>Sumber: rancangan SUNOVATE v2.5. Dokumen yang belum disetujui tidak dipakai sebagai sumber jawaban.</figcaption>
    </figure>
  );
}
