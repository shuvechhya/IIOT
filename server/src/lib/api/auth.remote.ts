import { goto } from "$app/navigation";
import { form, query, getRequestEvent } from "$app/server";
import { getDB } from "$db/mongo";
import { auth } from "$lib/auth";
import { loginSchema } from "$lib/schema/auth";
import { redirect } from "@sveltejs/kit";
import { ObjectId } from "mongodb";

export const login = form(loginSchema, async (body) => {
  let { user } = await auth.api.signInEmail({ body: body });
  let db = getDB();
  let doc = await db.collection("user").findOne({ _id: new ObjectId(user.id) });
  let role = doc?.role;
  if (role) {
    if (role === "admin") {
      redirect(307, "/admin");
    } else if (role === "gateway") {
      redirect(307, "/dashboard");
    }
  }
});

export const getUser = query(async () => {
  const { locals } = getRequestEvent();
  if (!locals.user) {
    redirect(307, "/");
  }
  return locals.user;
});
