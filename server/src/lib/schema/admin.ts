import { ObjectId } from "mongodb";
import * as z from "zod";

export const createUserSchema = z.object({
  name: z.string().check(z.minLength(8)),
  email: z.email(),
  password: z.string().check(z.minLength(8)),
  role: z.enum(["gateway", "admin", "manager"]).default("gateway"),
});

export const updateUserSchema = z.object({
  id: z.string(),
  name: z.string().check(z.minLength(8)),
  email: z.email(),
  password: z.string().check(z.minLength(8)),
  role: z.enum(["gateway", "admin", "manager"]).default("gateway"),
});

export const analyticsSchema = z.object({
  id: z.string(),
  name: z.string(),
  src: z.string(),
  user_id: z.string(),
});

export const createAnayticsSchema = z.object({
  name: z.string(),
  src: z.string(),
});

export const updateAnalyticsSchema = z.object({
  id: z.string(),
  name: z.string(),
  src: z.string(),
});
