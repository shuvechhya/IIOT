import * as z from "zod";

export const loginSchema = z.object({
	email: z.email(),
	password: z.string().check(z.minLength(8)),
});
