<script lang="ts">
    import { Button } from "$lib/components/ui/button/index.js";
    import * as Card from "$lib/components/ui/card/index.js";
    import { Input } from "$lib/components/ui/input/index.js";
    import {
        FieldGroup,
        Field,
        FieldLabel,
        FieldDescription,
    } from "$lib/components/ui/field/index.js";
    import { authClient } from "$lib/auth-client";
    import { toast } from "svelte-sonner";
    import Eye from "@tabler/icons-svelte/icons/eye";
    import EyeOff from "@tabler/icons-svelte/icons/eye-off";
    const id = $props.id();

    let wlan = $state<string>("");
    let lan = $state<string>("192.168.200.30");
    let token = $state<string>("");

    let showToken = $state<boolean>(false);

    const handleTokenGenerator = async (e: MouseEvent) => {
        e.preventDefault();
        const { data, error } = await authClient.token();
        if (error) {
            toast.error("Token Generation", {
                description: `Error in creating token with error of: ${error}`,
            });
        }
        if (data) {
            token = data.token;
            if (token) {
                toast.success("Token Generation", {
                    description:
                        "Successfully created token, Please copy the provided token",
                });
            } else {
                toast.error("Token Generation", {
                    description: "Token is empty, internal error 500",
                });
            }
        }
    };
</script>

<Card.Root class="mx-auto w-full max-w-sm">
    <Card.Header>
        <Card.Title class="text-2xl">Token Generator</Card.Title>
        <Card.Description
            >Generate your token to connect to the server's MQTT</Card.Description
        >
    </Card.Header>
    <Card.Content>
        <form>
            <FieldGroup>
                <Field>
                    <div class="flex justify-between">
                        <FieldLabel>Token</FieldLabel>
                        <div class="flex gap-4">
                            <Button
                                onclick={() => {
                                    showToken = !showToken;
                                }}
                            >
                                {#if showToken === true}
                                    <Eye />
                                {:else}
                                    <EyeOff />
                                {/if}
                            </Button>
                            <Button onclick={handleTokenGenerator}>Token</Button
                            >
                        </div>
                    </div>
                    <Input
                        type={showToken ? "text" : "password"}
                        bind:value={token}
                        readonly
                    />
                </Field>
                <Field>
                    <FieldLabel>Server's WLAN IP Address</FieldLabel>
                    <Input type="text" bind:value={wlan} readonly />
                </Field>
                <Field>
                    <FieldLabel>Server's LAN IP Address</FieldLabel>
                    <Input type="text" bind:value={lan} readonly />
                </Field>
            </FieldGroup>
        </form>
    </Card.Content>
</Card.Root>
