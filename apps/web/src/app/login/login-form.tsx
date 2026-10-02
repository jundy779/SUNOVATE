"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { devLoginSchema, SIMULATED_USERS, type DevLoginInput } from "@sunovate/contracts";
import { zodResolver } from "@/lib/zod-resolver";
import { loginAction } from "./actions";

export function LoginForm() {
  const router = useRouter();
  const [serverError, setServerError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<DevLoginInput>({
    resolver: zodResolver(devLoginSchema),
    defaultValues: { email: SIMULATED_USERS[5].email },
  });

  const onSubmit = handleSubmit(async (values) => {
    setServerError(null);
    const result = await loginAction(values);
    if (!result.ok) {
      setServerError(result.message ?? "Login gagal");
      return;
    }
    router.replace("/dashboard");
    router.refresh();
  });

  return (
    <form className="auth-form" onSubmit={onSubmit} noValidate>
      <label htmlFor="email">Email pengguna simulasi</label>
      <input
        id="email"
        type="email"
        list="simulated-users"
        autoComplete="off"
        aria-invalid={errors.email ? "true" : "false"}
        aria-describedby={errors.email ? "email-error" : "email-hint"}
        {...register("email")}
      />
      <datalist id="simulated-users">
        {SIMULATED_USERS.map((user) => (
          <option key={user.email} value={user.email}>
            {user.role}
          </option>
        ))}
      </datalist>
      <small id="email-hint">Pilih salah satu akun SIMULATED_DATA. Tidak ada kata sandi.</small>
      {errors.email ? (
        <p className="field-error" id="email-error" role="alert">
          {errors.email.message}
        </p>
      ) : null}
      {serverError ? (
        <p className="field-error" role="alert">
          {serverError}
        </p>
      ) : null}
      <button className="button" type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Memproses..." : "Masuk dengan akses pengembangan"}
      </button>
    </form>
  );
}
