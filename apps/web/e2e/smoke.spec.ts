import { expect, test } from "@playwright/test";

/**
 * Smoke flow against a running API (pnpm api:dev) and web app (pnpm dev). SIMULATED_DATA only.
 */
test("staff logs in, sees scoped dashboard, and asks SAVI AI", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email pengguna simulasi").fill("sim.staff.pppsun@sunovate.local");
  await page.getByRole("button", { name: "Masuk dengan akses pengembangan" }).click();

  await expect(page.getByRole("heading", { name: "Ringkasan kerja", exact: true })).toBeVisible();
  await expect(page.getByText("SIMULATED_DATA").first()).toBeVisible();
  await expect(page.getByRole("link", { name: "Administrasi" })).toHaveCount(0);

  await page.getByRole("link", { name: "SAVI AI" }).click();
  await page.getByLabel("Pertanyaan untuk SAVI AI").fill(
    "Apa saja metadata wajib saat mendaftarkan dokumen knowledge?",
  );
  await page.getByRole("button", { name: "Kirim pertanyaan" }).click();
  await expect(page.getByText("Dijawab dengan sumber")).toBeVisible();
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
  await page.getByLabel("Email pengguna simulasi").fill("sim.staff.pppsun@sunovate.local");
  await page.getByRole("button", { name: "Masuk dengan akses pengembangan" }).click();
  await page.waitForURL(/\/dashboard$/);
  await page.goto("/admin");
  await expect(page.getByRole("heading", { name: "Anda tidak memiliki izin" })).toBeVisible();
});
