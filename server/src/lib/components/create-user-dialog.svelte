<script lang="ts">
  import { Button, buttonVariants } from "$lib/components/ui/button/index.js";
  import * as Dialog from "$lib/components/ui/dialog/index.js";
  import { Input } from "$lib/components/ui/input/index.js";
  import { Label } from "$lib/components/ui/label/index.js";
  import Combobox from "$lib/components/dropdown-combobox.svelte";
  import Eye from "@tabler/icons-svelte/icons/eye";
  import EyeOff from "@tabler/icons-svelte/icons/eye-off";
  import { createUser } from "$lib/api/admin.remote";
  import { toast } from "svelte-sonner";

  let roles: {
    value: "gateway" | "admin" | "manager";
    label: string;
  }[] = [
    {
      value: "admin",
      label: "Admin",
    },
    {
      value: "gateway",
      label: "Gateway",
    },
  ];

  let email = $state<string>("");
  let password = $state<string>("");
  let name = $state<string>("");
  let role = $state<"gateway" | "admin" | "manager">("gateway");

  const refreshForm = async () => {
    email = "";
    password = "";
    name = "";
    role = "gateway";
  };

  const handleSubmit = async () => {
    try {
      await createUser({
        name: name,
        email: email,
        password: password,
        role: role,
      });
      await refreshForm();
      toast.success("Create User", {
        description: "Successfully created user!",
      });
    } catch (e) {
      toast.error("Create User", {
        description: `Error creating user with error: ${e}`,
      });
    }
  };

  let showPassword: boolean = $state(false);
</script>

{#snippet ShowPassword(showPassword: boolean)}
  {#if showPassword === false}
    <EyeOff />
  {:else}
    <Eye />
  {/if}
{/snippet}

<Dialog.Root>
  <Dialog.Trigger class={buttonVariants({ variant: "outline" })}
    >Create User</Dialog.Trigger
  >
  <Dialog.Content class="sm:max-w-[425px]">
    <Dialog.Header>
      <Dialog.Title>Create User</Dialog.Title>
      <Dialog.Description
        >Create user here. New admin or gateway to let gateways start sending
        data through mqtt</Dialog.Description
      >
    </Dialog.Header>
    <form onsubmit={handleSubmit}>
      <div class="grid gap-4 py-4">
        <div class="grid grid-cols-4 items-center gap-4">
          <Label for="name" class="text-right">Name</Label>
          <Input class="col-span-3" bind:value={name} required />
        </div>
        <div class="grid grid-cols-4 items-center gap-4">
          <Label for="email" class="text-right">Email</Label>
          <Input class="col-span-3" bind:value={email} required />
        </div>
        <div class="grid grid-cols-4 items-center gap-4">
          <Label for="password" class="text-right">Password</Label>
          <div class="grid grid-cols-4 col-span-3 gap-3">
            <Input
              type={showPassword ? "text" : "password"}
              bind:value={password}
              class="col-span-3"
            />
            <Button
              type="button"
              variant="outline"
              onclick={() => {
                showPassword = !showPassword;
              }}
            >
              {@render ShowPassword(showPassword)}
            </Button>
          </div>
        </div>
        <div class="grid grid-cols-4 items-center gap-4">
          <Label for="username" class="text-right">Password</Label>
          <Combobox {roles} bind:value={role} />
        </div>
      </div>
      <Dialog.Footer>
        <Button type="submit">Create User</Button>
      </Dialog.Footer>
    </form>
  </Dialog.Content>
</Dialog.Root>
