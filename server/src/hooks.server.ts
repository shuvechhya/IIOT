import { auth } from "$lib/auth";
import { svelteKitHandler } from "better-auth/svelte-kit";
import { building } from "$app/environment";
import { connect, getDB } from "$db/mongo";
import { redirect } from "@sveltejs/kit";

export async function handle({ event, resolve }) {
  const session = await auth.api.getSession({
    headers: event.request.headers,
  });

  const protectedRoutes = ["/admin", "/dashboard"];

  if (protectedRoutes.some((route) => event.url.pathname.startsWith(route))) {
    if (!session?.user) {
      redirect(307, "/");
    }

    if (
      event.url.pathname.startsWith("/admin") &&
      session?.user?.role !== "admin"
    ) {
      redirect(307, "/dashboard");
    }
  }

  if (event.url.pathname === "/" && session?.user) {
    if (session?.user?.role === "admin") {
      redirect(307, "/admin");
    } else {
      redirect(307, "/dashboard");
    }
  }

  if (session) {
    event.locals.session = session.session;
    event.locals.user = session.user;
  }
  return svelteKitHandler({ event, resolve, auth, building });
}

connect()
  .then(async () => {
    console.log("MongoDB has started");
    const db = getDB();
    const collections = await db.listCollections({ name: "user" }).toArray();
    if (collections.length > 0) {
      console.log("Users collection exists");
    } else {
      console.log("Users collection does not exist");
      console.log("Creating admin user");
      await auth.api.signUpEmail({
        body: {
          email: "admin@gmail.com",
          password: "admin123",
          name: "Admin",
        },
      });
      await db
        .collection("users")
        .updateOne({ email: "admin@gmail.com" }, { $set: { role: "admin" } });
    }
  })
  .catch((e: Error) => {
    console.log("MongoDB failed to start");
    console.log(e);
  });
