import { z } from "zod/v4";

export const schema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.email(),
  emailVerified: z.boolean(),
  image: z.union([z.string(), z.null(), z.undefined()]),
  role: z.union([z.string(), z.undefined()]),
  createdAt: z.date(),
  updatedAt: z.date(),
  banned: z.union([z.boolean(), z.null(), z.undefined()]),
  banReason: z.union([z.string(), z.null(), z.undefined()]),
  banExpires: z.union([z.date(), z.null(), z.undefined()]),
});

export type Schema = z.infer<typeof schema>;
