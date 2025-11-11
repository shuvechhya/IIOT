// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
import { usersSchema, sessionSchema } from "./lib/schema/users";

type UserType = z.infer<typeof usersSchema>;
type SessionType = z.infer<typeof sessionSchema>;

declare global {
  namespace App {
    // interface Error {}
    interface Locals {
      session?: SessionType;
      user?: UserType;
    }
    // interface PageData {}
    // interface PageState {}
    // interface Platform {}
  }
}

export {};
