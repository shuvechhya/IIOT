import { auth } from "$lib/auth";
import { toSvelteKitHandler } from "better-auth/svelte-kit";
import type { RequestEvent } from "./$types";

const baseHandler = toSvelteKitHandler(auth);

const handler = async (event: RequestEvent) => {
	console.log(`[Atuh] ${event.request.method} ${event.url.pathname}`);
	return baseHandler(event);
};

export { handler as GET, handler as POST };
