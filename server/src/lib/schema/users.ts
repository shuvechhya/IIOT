import * as z from "zod";
import { ObjectId } from "mongodb";

export const usersSchema = z.object({
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

export const usersListSchema = usersSchema.array();

export const sessionSchema = z.object({
  _id: z.instanceof(ObjectId),
  userId: z.instanceof(ObjectId),
  expiresAt: z.string(),
  token: z.string(),
  createdAt: z.string(),
  updateAt: z.string(),
  ipAddress: z.string(),
  userAgent: z.string(),
});
