<script lang="ts">
    import CirclePlusFilledIcon from "@tabler/icons-svelte/icons/circle-plus-filled";
    import * as Sidebar from "$lib/components/ui/sidebar/index.js";
    import type { Icon } from "@tabler/icons-svelte";
    import { authClient } from "$lib/auth-client";
    import Input from "./ui/input/input.svelte";
    import { toast } from "svelte-sonner";
    import Eye from "@tabler/icons-svelte/icons/eye";
    import Button from "./ui/button/button.svelte";
    import EyeOff from "@tabler/icons-svelte/icons/eye-off";
    import { DashboardNav } from "$lib/global/Global.svelte";

    let {
        items,
    }: { items: { id: string; title: string; url: string; icon?: Icon }[] } =
        $props();
    let showPassword = $state<boolean>(false);

    let token: string = $state("");
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

{#snippet SidebarMenuItem()}
    <Sidebar.Menu>
        <Sidebar.MenuItem class="flex items-center gap-2">
            <Input
                bind:value={token}
                type={showPassword ? "text" : "password"}
            />
            <Button
                onclick={() => {
                    showPassword = !showPassword;
                }}
            >
                {#if showPassword === true}
                    <Eye />
                {:else}
                    <EyeOff />
                {/if}
            </Button>
            <Sidebar.MenuButton
                class="bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground active:bg-primary/90 active:text-primary-foreground min-w-5 duration-200 ease-linear"
                tooltipContent="Token Generator"
                onclick={handleTokenGenerator}
            >
                <CirclePlusFilledIcon />
                <span>Token</span>
            </Sidebar.MenuButton>
            <!-- <Sidebar.MenuButton -->
            <!--   class="bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground active:bg-primary/90 active:text-primary-foreground min-w-8 duration-200 ease-linear" -->
            <!--   tooltipContent="Copy token" -->
            <!-- > -->
            <!--   <Copy /> -->
            <!-- </Sidebar.MenuButton> -->
        </Sidebar.MenuItem>
    </Sidebar.Menu>
{/snippet}

<Sidebar.Group>
    <Sidebar.GroupContent class="flex flex-col gap-2">
        {@render SidebarMenuItem()}
        <Sidebar.Menu>
            {#each items as item (item.title)}
                <Sidebar.MenuItem>
                    <Sidebar.MenuButton
                        tooltipContent={item.title}
                        onclick={() => DashboardNav.change(item.id, item.title)}
                    >
                        {#if item.icon}
                            <item.icon />
                        {/if}
                        <span>{item.title}</span>
                    </Sidebar.MenuButton>
                </Sidebar.MenuItem>
            {/each}
        </Sidebar.Menu>
    </Sidebar.GroupContent>
</Sidebar.Group>
