import { command, form, getRequestEvent, query } from "$app/server";
import { auth } from "$lib/auth";
import { createUserSchema, updateUserSchema } from "$lib/schema/admin";
import { redirect } from "@sveltejs/kit";
import { UsersListSchema } from "$lib/schema/users";
import z from "zod";

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
  const { headers, user } = requireAdmin();
  let admin = user.id;
  const users = await auth.api.listUsers({
    query: {
      limit: 100,
      sortBy: "_id",
    },
    headers: headers,
  });
  let parsedUsers: z.Infer<typeof UsersListSchema> = [];
  users.users.map((user) => {
    if (user.id !== admin) {
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
    }
  });

  return parsedUsers;
});

export const deleteUser = command(z.string(), async (id) => {
  const { headers } = requireAdmin();
  await auth.api.removeUser({
    body: {
      userId: id,
    },
    headers: headers,
  });
  await listUsers().refresh();
});

export const updateUser = command(
  updateUserSchema,
  async ({ id, email, name, password, role }) => {
    const { headers } = requireAdmin();
    await auth.api.adminUpdateUser({
      body: {
        userId: id,
        data: {
          email: email,
          name: name,
          role: role,
        },
      },
      headers: headers,
    });
  },
);

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
