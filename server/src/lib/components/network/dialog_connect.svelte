<script lang="ts">
    import { Button, buttonVariants } from "$lib/components/ui/button/index.js";
    import * as Dialog from "$lib/components/ui/dialog/index.js";
    import { Input } from "$lib/components/ui/input/index.js";
    import { Label } from "$lib/components/ui/label/index.js";
    import Eye from "@tabler/icons-svelte/icons/eye";
    import EyeOff from "@tabler/icons-svelte/icons/eye-off";
    import { toast } from "svelte-sonner";
    import * as z from "zod";
    import type { networkSchema } from "$lib/schema/network";
    import { connectNetwork } from "$lib/api/network.remote";

    let {
        ssid,
        signal,
        security,
    }: {
        ssid: string;
        signal: string;
        security: string;
    } = $props();
    let open = $state<boolean>(false);

    let password = $state<string>("");

    const refreshForm = async () => {
        password = "";
    };

    const handleSubmit = async () => {
        try {
            await connectNetwork({
                ssid: ssid,
                password: password,
            });
            await refreshForm();
            toast.success("Connect WIFI", {
                description: `Successfully Connected to ${ssid}`,
            });
        } catch (e) {
            toast.error("Connect WIFI", {
                description: `Error connecting to ${ssid}, with error: ${e}`,
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

<Dialog.Root
    {open}
    onOpenChange={async (value) => {
        open = value;
        password = "";
    }}
>
    <Dialog.Trigger class="w-full">Connect</Dialog.Trigger>
    <Dialog.Content class="sm:max-w-[425px]">
        <Dialog.Header>
            <Dialog.Title>Create User</Dialog.Title>
            <Dialog.Description
                >Create user here. New admin or gateway to let gateways start
                sending data through mqtt</Dialog.Description
            >
        </Dialog.Header>
        <form onsubmit={handleSubmit}>
            <div class="grid gap-4 py-4">
                <div class="grid grid-cols-4 items-center gap-4">
                    <Label class="text-right">SSID</Label>
                    <Input
                        class="col-span-3"
                        bind:value={ssid}
                        readonly
                        disabled
                    />
                </div>
                <div class="grid grid-cols-4 items-center gap-4">
                    <Label class="text-right">Signal</Label>
                    <Input
                        class="col-span-3"
                        bind:value={signal}
                        readonly
                        disabled
                    />
                </div>
                <div class="grid grid-cols-4 items-center gap-4">
                    <Label class="text-right">Security</Label>
                    <Input
                        class="col-span-3"
                        bind:value={security}
                        readonly
                        disabled
                    />
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
            </div>
            <Dialog.Footer>
                <Button type="submit">Connect</Button>
            </Dialog.Footer>
        </form>
    </Dialog.Content>
</Dialog.Root>
