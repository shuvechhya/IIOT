import { createAuthClient } from "better-auth/client";
import { adminClient, jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
	fetchOptions: {
		credentials: "include",
	},
	plugins: [adminClient(), jwtClient()],
});
