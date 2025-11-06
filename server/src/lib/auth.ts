import { getRequestEvent } from "$app/server";
import { betterAuth } from "better-auth";
import { mongodbAdapter } from "better-auth/adapters/mongodb";
import { admin, jwt, openAPI } from "better-auth/plugins";
import { sveltekitCookies } from "better-auth/svelte-kit";
import { getDB, client } from "../db/mongo";
import { BETTER_AUTH_SECRET } from "$env/static/private";
import { ac, gateway, manager, adminAc } from "$lib/permissions";

export const auth = betterAuth({
  secret: BETTER_AUTH_SECRET,
  database: mongodbAdapter(getDB(), {
    client,
  }),
  emailAndPassword: {
    enabled: true,
  },
  plugins: [
    sveltekitCookies(getRequestEvent),
    admin({
      ac,
      roles: {
        admin: adminAc,
        gateway,
        manager,
      },
    }),
    jwt(),
    openAPI(),
  ],
});
