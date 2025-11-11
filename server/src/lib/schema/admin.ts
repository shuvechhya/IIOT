import * as z from "zod";

export const createUserSchema = z.object({
	name: z.string().check(z.minLength(8)),
	email: z.email(),
	password: z.string().check(z.minLength(8)),
	role: z.enum(["gateway", "admin", "manager"]).default("gateway"),
});
