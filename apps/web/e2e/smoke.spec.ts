import { expect, test } from "@playwright/test";

/**
 * Smoke flow against a running API (pnpm api:dev) and web app (pnpm dev). SIMULATED_DATA only.
 */
test("staff logs in, sees scoped dashboard, and asks SAVI AI", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("button", { name: "Masuk dengan akses pengembangan" })).toBeEnabled();
  await page.getByLabel("Email pengguna simulasi").fill("sim.staff.pppsun@sunovate.local");
  await page.getByRole("button", { name: "Masuk dengan akses pengembangan" }).click();

  await expect(page.getByRole("heading", { name: "Ringkasan kerja", exact: true })).toBeVisible();
  await expect(page.getByText("Data contoh", { exact: false }).first()).toBeVisible();
  await expect(page.getByText("Yield SUN", { exact: true })).toBeVisible();
  await expect(page.getByText("Kepemilikan SBN", { exact: true })).toBeVisible();
  await expect(page.getByText("Sumber data belum tersedia")).toHaveCount(2);
  await expect(page.getByRole("link", { name: "Administrasi" })).toHaveCount(0);

  await page.getByRole("navigation", { name: "Navigasi utama" }).getByRole("link", { name: "SAVI AI" }).click();
  await page
    .getByRole("button", { name: "Apa metadata wajib saat mendaftarkan dokumen?" })
    .click();
  await page.getByRole("button", { name: "Kirim pertanyaan" }).click();
  await expect(page.getByText("Dijawab dengan sumber")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Sumber yang digunakan" })).toBeVisible();
  await expect(page.getByText("1 rujukan digunakan")).toBeVisible();

  await page.getByRole("button", { name: "Mulai percakapan baru" }).click();
  await expect(page.getByRole("heading", { name: "Mulai dari pertanyaan tentang SUN" })).toBeVisible();
  await expect(page.getByText("Dijawab dengan sumber")).toHaveCount(0);
});

test("public landing page explains scope without loading authenticated data", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle("SUNOVATE");
  await expect(page.getByRole("heading", { name: /Pengetahuan organisasi/ })).toBeVisible();
  await expect(page.getByRole("link", { name: "Akses SUNOVATE" })).toHaveAttribute("href", "/login");
  await expect(page.getByText("Bukan sistem transaksi atau pengambilan keputusan keuangan")).toBeVisible();
});

test("unauthenticated visitors are redirected to login", async ({ page }) => {
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/login$/);
});

test("staff cannot open administration", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("button", { name: "Masuk dengan akses pengembangan" })).toBeEnabled();
  await page.getByLabel("Email pengguna simulasi").fill("sim.staff.pppsun@sunovate.local");
  await page.getByRole("button", { name: "Masuk dengan akses pengembangan" }).click();
  await page.waitForURL(/\/dashboard$/);
  await page.goto("/admin");
  await expect(page.getByRole("heading", { name: "Anda tidak memiliki izin" })).toBeVisible();
});

test("staff creates and updates scoped work data", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("button", { name: "Masuk dengan akses pengembangan" })).toBeEnabled();
  await page.getByLabel("Email pengguna simulasi").fill("sim.staff.pppsun@sunovate.local");
  await page.getByRole("button", { name: "Masuk dengan akses pengembangan" }).click();
  await page.getByRole("link", { name: "Monitoring Kerja" }).click();

  // A unique title keeps the scenario repeatable against an API that still holds earlier runs.
  const title = `Output simulasi dari UI ${Date.now()}`;
  await page.getByRole("button", { name: "Tambah output" }).click();
  const form = page.locator("form.work-form");
  await form.getByLabel("Judul").fill(title);
  await form.getByLabel("Deskripsi").fill("Data simulasi untuk memverifikasi alur monitoring kerja.");
  await form.getByLabel("Tim").selectOption({ index: 1 });
  await page.getByRole("button", { name: "Simpan" }).click();

  await expect(page.getByText(title)).toBeVisible();
  await expect(page.getByText("Output kerja berhasil ditambahkan.")).toBeVisible();
});

test("granted reader opens a confidential document only after accepting the notice", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("button", { name: "Masuk dengan akses pengembangan" })).toBeEnabled();
  await page.getByLabel("Email pengguna simulasi").fill("sim.coordinator@sunovate.local");
  await page.getByRole("button", { name: "Masuk dengan akses pengembangan" }).click();
  await page.waitForURL(/\/dashboard$/);

  // First visits compile these routes in development mode, which can exceed the default 5 s.
  await page.goto("/dokumen-rahasia");
  await page.getByRole("link", { name: /Pedoman Penilaian Internal/ }).click();
  await expect(page.getByRole("heading", { name: "Pernyataan kerahasiaan" })).toBeVisible({ timeout: 30_000 });
  await expect(page.getByRole("button", { name: "Buka dokumen" })).toBeDisabled();
  await expect(page.locator(".sv-page img")).toHaveCount(0);

  await page.getByLabel("Saya memahami dan menyetujui pernyataan di atas.").check();
  await page.getByRole("button", { name: "Buka dokumen" }).click();
  await expect(page.getByRole("img", { name: /Halaman 1 dari 2/ })).toBeVisible({ timeout: 30_000 });
  await expect(page.getByRole("link", { name: /unduh/i })).toHaveCount(0);
});

test("readers without a grant see no confidential documents", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("button", { name: "Masuk dengan akses pengembangan" })).toBeEnabled();
  await page.getByLabel("Email pengguna simulasi").fill("sim.staff.pppsun@sunovate.local");
  await page.getByRole("button", { name: "Masuk dengan akses pengembangan" }).click();
  await page.waitForURL(/\/dashboard$/);
  await page.goto("/dokumen-rahasia");
  await expect(page.getByText("Belum ada dokumen rahasia untuk Anda")).toBeVisible();
});

test("team lead grants and revokes read access without seeing document content", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("button", { name: "Masuk dengan akses pengembangan" })).toBeEnabled();
  await page.getByLabel("Email pengguna simulasi").fill("sim.lead.psun@sunovate.local");
  await page.getByRole("button", { name: "Masuk dengan akses pengembangan" }).click();
  await page.waitForURL(/\/dashboard$/);

  await page.goto("/dokumen-rahasia");
  await page.getByRole("link", { name: "Kelola akses baca" }).click();
  await expect(page.getByRole("heading", { name: "Kelola akses baca" })).toBeVisible({ timeout: 30_000 });
  await expect(page.locator("section.sv-manage")).toHaveCount(1);
  const section = page.locator("section.sv-manage").filter({ hasText: "Catatan Penyusunan Regulasi" });
  await section.getByLabel("Email pegawai").fill("sim.auditor@sunovate.local");
  await section.getByRole("button", { name: "Beri akses baca" }).click();
  await expect(section.getByText("Akses baca diberikan kepada sim.auditor@sunovate.local.")).toBeVisible();
  await section.locator("li").filter({ hasText: "sim.auditor@sunovate.local" }).getByRole("button", { name: "Cabut akses" }).click();
  await expect(section.getByText(/Akses baca sim.auditor@sunovate.local dicabut/)).toBeVisible();
  await expect(page.getByText("KODE-UJI-RAHASIA-7781")).toHaveCount(0);
});

test("coordinator filters, sorts, and downloads work data as Excel", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("button", { name: "Masuk dengan akses pengembangan" })).toBeEnabled();
  await page.getByLabel("Email pengguna simulasi").fill("sim.coordinator@sunovate.local");
  await page.getByRole("button", { name: "Masuk dengan akses pengembangan" }).click();
  await page.waitForURL(/\/dashboard$/);

  await page.goto("/work-monitoring");
  await page.getByRole("button", { name: /^Tugas/ }).click();
  const rows = page.locator(".work-table tbody tr");
  const total = await rows.count();
  expect(total).toBeGreaterThan(1);

  await page.getByRole("button", { name: "Judul" }).click();
  await expect(page.locator("th[aria-sort='ascending']")).toHaveText("Judul");
  const firstTitle = (await rows.first().locator("strong").innerText()).trim();
  await page.getByLabel("Cari judul").fill(firstTitle);
  await expect(page.getByText(/Menampilkan \d+ dari \d+ baris/)).toBeVisible();
  expect(await rows.count()).toBeLessThanOrEqual(total);

  const [download] = await Promise.all([page.waitForEvent("download"), page.getByRole("link", { name: "Unduh Excel" }).click()]);
  expect(download.suggestedFilename()).toMatch(/^SUNOVATE-tugas-\d{8}\.xlsx$/);
});
