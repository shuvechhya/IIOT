import { createAccessControl } from "better-auth/plugins/access";

const statement = {
  user: ["create", "read", "update", "delete", "list", "set-role"],
  project: ["create", "access", "update", "delete", "push"],
} as const;

export const ac = createAccessControl(statement);

export const gateway = ac.newRole({
  project: ["push"],
});

export const manager = ac.newRole({
  user: ["read", "list"],
  project: ["create", "access", "update", "delete", "push"],
});

export const adminAc = ac.newRole({
  user: ["create", "read", "update", "delete", "list", "set-role"],
  project: ["create", "update", "access", "delete", "push"],
});
