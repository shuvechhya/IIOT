<script lang="ts">
    // import DotsIcon from "@tabler/icons-svelte/icons/dots";
    // import FolderIcon from "@tabler/icons-svelte/icons/folder";
    // import Share3Icon from "@tabler/icons-svelte/icons/share-3";
    // import TrashIcon from "@tabler/icons-svelte/icons/trash";
    import type { Icon } from "@tabler/icons-svelte";

    // import * as DropdownMenu from "$lib/components/ui/dropdown-menu/index.js";
    import * as Sidebar from "$lib/components/ui/sidebar/index.js";
    import { DashboardNav } from "$lib/global/Global.svelte";

    let {
        items,
    }: { items: { id: string; name: string; url: string; icon: Icon }[] } =
        $props();

    // const sidebar = Sidebar.useSidebar();
</script>

<Sidebar.Group class="group-data-[collapsible=icon]:hidden">
    <Sidebar.GroupLabel>More Functionalities</Sidebar.GroupLabel>
    <Sidebar.Menu>
        {#each items as item (item.name)}
            <Sidebar.MenuItem>
                <Sidebar.MenuButton>
                    {#snippet child({ props })}
                        <a
                            {...props}
                            href={item.url}
                            onclick={() => {
                                DashboardNav.change(item.id, item.name);
                            }}
                        >
                            <item.icon />
                            <span>{item.name}</span>
                        </a>
                    {/snippet}
                </Sidebar.MenuButton>
            </Sidebar.MenuItem>
        {/each}
    </Sidebar.Menu>
</Sidebar.Group>
