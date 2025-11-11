import { command, form, getRequestEvent, query } from "$app/server";
import { auth } from "$lib/auth";
import { createUserSchema } from "$lib/schema/admin";
import { redirect } from "@sveltejs/kit";

function requireAdmin() {
	const { locals, request } = getRequestEvent();
	if (!locals.user) {
		redirect(307, "/");
	} else {
		if (locals.user?.role !== "admin") {
			redirect(307, "/dashboard");
		}
	}
	return {
		user: locals.user,
		session: locals.session,
		headers: request.headers,
	};
}

export const listUsers = query(async () => {
	const { headers } = requireAdmin();
	const users = await auth.api.listUsers({
		query: {
			limit: 100,
			sortBy: "_id",
		},
		headers: headers,
	});

	return users.users;
});

export const createUser = command(createUserSchema, async (user) => {
	const _ = requireAdmin();
	console.log(user);
	await auth.api.createUser({
		body: {
			email: user.email,
			password: user.password,
			name: user.name,
			role: user.role,
		},
	});
	await listUsers().refresh();
});
