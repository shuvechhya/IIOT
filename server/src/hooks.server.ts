import { auth } from "$lib/auth";
import { svelteKitHandler } from "better-auth/svelte-kit";
import { building } from "$app/environment";
import { connect } from "$db/mongo";

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
  .then(() => {
    console.log("MongoDB has started");
  })
  .catch((e: Error) => {
    console.log("MongoDB failed to start");
    console.log(e);
  });
