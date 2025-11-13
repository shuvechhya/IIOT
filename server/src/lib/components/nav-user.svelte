<script lang="ts">
    import CreditCardIcon from "@tabler/icons-svelte/icons/credit-card";
    import DotsVerticalIcon from "@tabler/icons-svelte/icons/dots-vertical";
    import LogoutIcon from "@tabler/icons-svelte/icons/logout";
    import NotificationIcon from "@tabler/icons-svelte/icons/notification";
    import UserCircleIcon from "@tabler/icons-svelte/icons/user-circle";
    import * as Avatar from "$lib/components/ui/avatar/index.js";
    import * as DropdownMenu from "$lib/components/ui/dropdown-menu/index.js";
    import * as Sidebar from "$lib/components/ui/sidebar/index.js";
    import { authClient } from "$lib/auth-client";
    import { goto } from "$app/navigation";

    let { user }: { user: { name: string; email: string; role: string } } =
        $props();

    const sidebar = Sidebar.useSidebar();
    const handleSignOut = async () => {
        await authClient.signOut();
        goto("/");
    };
</script>

<Sidebar.Menu>
    <Sidebar.MenuItem>
        <DropdownMenu.Root>
            <DropdownMenu.Trigger>
                {#snippet child({ props })}
                    <Sidebar.MenuButton
                        {...props}
                        size="lg"
                        class="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                    >
                        <Avatar.Root class="size-8 rounded-lg grayscale">
                            <Avatar.Fallback class="rounded-lg"
                                >User</Avatar.Fallback
                            >
                        </Avatar.Root>
                        <div
                            class="grid flex-1 text-left text-sm leading-tight"
                        >
                            <span class="truncate font-medium">{user.name}</span
                            >
                            <span
                                class="text-muted-foreground truncate text-xs"
                            >
                                {user.email}
                            </span>
                        </div>
                        <DotsVerticalIcon class="ml-auto size-4" />
                    </Sidebar.MenuButton>
                {/snippet}
            </DropdownMenu.Trigger>
            <DropdownMenu.Content
                class="w-(--bits-dropdown-menu-anchor-width) min-w-56 rounded-lg"
                side={sidebar.isMobile ? "bottom" : "right"}
                align="end"
                sideOffset={4}
            >
                <DropdownMenu.Label class="p-0 font-normal">
                    <div
                        class="flex items-center gap-2 px-1 py-1.5 text-left text-sm"
                    >
                        <Avatar.Root class="size-8 rounded-lg">
                            <Avatar.Fallback class="rounded-lg"
                                >User</Avatar.Fallback
                            >
                        </Avatar.Root>
                        <div
                            class="grid flex-1 text-left text-sm leading-tight"
                        >
                            <span class="truncate font-medium">{user.name}</span
                            >
                            <span
                                class="text-muted-foreground truncate text-xs"
                            >
                                {user.email}
                            </span>
                        </div>
                    </div>
                </DropdownMenu.Label>
                <DropdownMenu.Separator />
                <DropdownMenu.Group>
                    <DropdownMenu.Item disabled>
                        <UserCircleIcon />
                        Account
                    </DropdownMenu.Item>
                    <!-- <DropdownMenu.Item>
                        <CreditCardIcon />
                        Billing
                    </DropdownMenu.Item>
                    <DropdownMenu.Item>
                        <NotificationIcon />
                        Notifications
                    </DropdownMenu.Item> -->
                </DropdownMenu.Group>
                <DropdownMenu.Separator />
                <DropdownMenu.Item onclick={handleSignOut}>
                    <LogoutIcon />
                    Log out
                </DropdownMenu.Item>
            </DropdownMenu.Content>
        </DropdownMenu.Root>
    </Sidebar.MenuItem>
</Sidebar.Menu>
