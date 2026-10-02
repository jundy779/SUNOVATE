import type { FieldErrors, FieldValues, Resolver } from "react-hook-form";
import type { z } from "zod";

/**
 * Minimal React Hook Form resolver for Zod schemas.
 * Avoids an extra dependency (@hookform/resolvers) for the two forms in this scaffold.
 */
export function zodResolver<T extends FieldValues>(schema: z.ZodType<T>): Resolver<T> {
  return async (values) => {
    const result = schema.safeParse(values);
    if (result.success) return { values: result.data, errors: {} };
    const errors: Record<string, { type: string; message: string }> = {};
    for (const issue of result.error.issues) {
      const key = issue.path.join(".") || "root";
      errors[key] ??= { type: issue.code, message: issue.message };
    }
    return { values: {}, errors: errors as FieldErrors<T> };
  };
}
