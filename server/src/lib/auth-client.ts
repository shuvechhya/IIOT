import { createAuthClient } from "better-auth/client";
import { adminClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
	fetchOptions: {
		credentials: "include",
	},
	plugins: [adminClient()],
});
