import * as z from "zod";
import { ObjectId } from "mongodb";

export const usersSchema = z.object({
  _id: z.instanceof(ObjectId),
  name: z.string().check(z.minLength(8)),
  email: z.email(),
  createdAt: z.string(),
  updatedAt: z.string(),
  role: z.enum(["gateway", "manager", "admin"]),
  banned: z.boolean(),
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
