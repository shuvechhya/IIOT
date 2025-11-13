import { command, form, getRequestEvent, query } from "$app/server";
import { auth } from "$lib/auth";
import { createUserSchema } from "$lib/schema/admin";
import { redirect } from "@sveltejs/kit";
import { usersListSchema } from "$lib/schema/users";
import type z from "zod";

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
  let parsedUsers: z.Infer<typeof usersListSchema> = [];
  users.users.map((user) => {
    parsedUsers.push({
      id: user.id,
      name: user.name,
      email: user.email,
      emailVerified: user.emailVerified,
      image: user.image,
      role: user.role,
      createdAt: user.createdAt,
      updatedAt: user.updatedAt,
      banned: user.banned,
      banReason: user.banReason,
      banExpires: user.banExpires,
    });
  });

  return parsedUsers;
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
