import { form } from "$app/server";
import { auth } from "$lib/auth";
import { loginSchema } from "$lib/schema/auth";
import { redirect } from "@sveltejs/kit";

export const login = form(loginSchema, async (user) => {
	await auth.api.signInEmail({ body: user });
	redirect(307, "/admin");
});
