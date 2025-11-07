import { auth } from "$lib/auth";
import { svelteKitHandler } from "better-auth/svelte-kit";
import { building } from "$app/environment";
import { connect, getDB } from "$db/mongo";

export async function handle({ event, resolve }) {
  const session = await auth.api.getSession({
    headers: event.request.headers,
  });

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
