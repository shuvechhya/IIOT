import { command, form, getRequestEvent, query } from "$app/server";
import { auth } from "$lib/auth";
import {
  analyticsSchema,
  createAnayticsSchema,
  createUserSchema,
  updateAnalyticsSchema,
  updateUserSchema,
} from "$lib/schema/admin";
import { redirect } from "@sveltejs/kit";
import { UsersListSchema } from "$lib/schema/users";
import z from "zod";
import { get_influx } from "$db/influx";
import { getDB } from "$db/mongo";
import { ObjectId } from "mongodb";

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
  const influx = await get_influx();
  if (influx !== null) {
    await auth.api.removeUser({
      body: {
        userId: id,
      },
      headers: headers,
    });
    await influx.dropDatabase(id);
    await listUsers().refresh();
  }
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

export const createUser = command(createUserSchema, async (u) => {
  const _ = requireAdmin();
  const influx = await get_influx();
  if (u.role !== "admin") {
    if (influx !== null) {
      let { user } = await auth.api.createUser({
        body: {
          email: u.email,
          password: u.password,
          name: u.name,
          role: u.role,
        },
      });
      await influx.createDatabase(user.id);
      await listUsers().refresh();
    }
  }
});

export const createAnalytics = command(createAnayticsSchema, async (a) => {
  const { user } = requireAdmin();
  const db = getDB();
  try {
    await db
      .collection("analytics")
      .insertOne({ name: a.name, src: a.src, user_id: user.id });
    await listAnalytics().refresh();
  } catch (error) {
    console.log("Create Analytics Error: ", error);
  }
});

export const listAnalytics = query(async () => {
  const { user } = requireAdmin();
  const db = getDB();
  type AnalyticSchema = z.infer<typeof analyticsSchema>;
  let response: AnalyticSchema[] = [];
  try {
    let document = await db
      .collection<AnalyticSchema>("analytics")
      .find({ user_id: user.id })
      .toArray();
    document.map((doc) => {
      response.push({
        id: doc._id.toString(),
        name: doc.name,
        src: doc.src,
        user_id: doc.user_id,
      });
    });
  } catch (error) {
    console.log("List Analytics Error: ", error);
  }
  return response;
});

export const updateAnalytic = command(
  updateAnalyticsSchema,
  async ({ id, name, src }) => {
    const _ = requireAdmin();
    const db = getDB();
    try {
      await db
        .collection("analytics")
        .updateOne(
          { _id: new ObjectId(id) },
          { $set: { name: name, src: src } },
        );
      await listAnalytics().refresh();
    } catch (error) {
      console.log("Create Analytics Error: ", error);
    }
  },
);

export const getAnalytic = query(z.string(), async (id) => {
  const _ = requireAdmin();
  const db = getDB();
  type AnalyticSchema = z.infer<typeof analyticsSchema>;
  let response: AnalyticSchema;
  try {
    let doc = await db
      .collection<AnalyticSchema>("analytics")
      .findOne({ _id: new ObjectId(id) });
    if (doc !== undefined || doc !== null) {
      response = analyticsSchema.parse({
        id: doc?._id.toString(),
        name: doc?.name,
        src: doc?.src,
        user_id: doc?.user_id,
      });
      return response;
    }
  } catch (error) {
    console.log(`Get Analytic with ID: ${id} error: ${error}`);
  }
});

export const deleteAnalytic = command(z.string(), async (id) => {
  const _ = requireAdmin();
  const db = getDB();
  try {
    await db.collection("analytics").deleteOne({ _id: new ObjectId(id) });
    await listAnalytics().refresh();
  } catch (error) {
    console.log(`Delete Analytic Error wiht ID: ${id} error: ${error}`);
  }
});
