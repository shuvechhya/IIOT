<script lang="ts">
    // import CameraIcon from "@tabler/icons-svelte/icons/camera";
    import ChartBarIcon from "@tabler/icons-svelte/icons/chart-bar";
    import DashboardIcon from "@tabler/icons-svelte/icons/dashboard";
    // import DatabaseIcon from "@tabler/icons-svelte/icons/database";
    // import FileAiIcon from "@tabler/icons-svelte/icons/file-ai";
    // import FileDescriptionIcon from "@tabler/icons-svelte/icons/file-description";
    // import FileWordIcon from "@tabler/icons-svelte/icons/file-word";
    // import FolderIcon from "@tabler/icons-svelte/icons/folder";
    import HelpIcon from "@tabler/icons-svelte/icons/help";
    // import InnerShadowTopIcon from "@tabler/icons-svelte/icons/inner-shadow-top";
    // import ListDetailsIcon from "@tabler/icons-svelte/icons/list-details";
    // import ReportIcon from "@tabler/icons-svelte/icons/report";
    import SearchIcon from "@tabler/icons-svelte/icons/search";
    import SettingsIcon from "@tabler/icons-svelte/icons/settings";
    // import UsersIcon from "@tabler/icons-svelte/icons/users";
    import NavDocuments from "./nav-documents.svelte";
    import NavMain from "./nav-main.svelte";
    // import NavSecondary from "./nav-secondary.svelte";
    import NavUser from "./nav-user.svelte";
    import * as Sidebar from "$lib/components/ui/sidebar/index.js";
    import type { ComponentProps } from "svelte";
    import { getUser } from "$lib/api/auth.remote";
    import StackMiddle from "@tabler/icons-svelte/icons/stack-middle";
    import CloudNetwork from "@tabler/icons-svelte/icons/cloud-network";

    const data = {
        navMain: [
            {
                id: "dashboard",
                title: "Dashboard",
                url: "#",
                icon: DashboardIcon,
            },
            {
                id: "analytics",
                title: "Analytics",
                url: "#",
                icon: ChartBarIcon,
            },
        ],
        // navSecondary: [
        //     {
        //         title: "Settings",
        //         url: "#",
        //         icon: SettingsIcon,
        //     },
        //     {
        //         title: "Get Help",
        //         url: "#",
        //         icon: HelpIcon,
        //     },
        //     {
        //         title: "Search",
        //         url: "#",
        //         icon: SearchIcon,
        //     },
        // ],
        documents: [
            {
                id: "network_settings",
                name: "Network Settings",
                url: "#",
                icon: CloudNetwork,
            },
            {
                id: "middleware_settings",
                name: "Middleware Settings",
                url: "#",
                icon: StackMiddle,
            },
        ],
    };

    let { ...restProps }: ComponentProps<typeof Sidebar.Root> = $props();

    const { name, email, role } = await getUser();
</script>

<Sidebar.Root collapsible="offcanvas" {...restProps}>
    <Sidebar.Header>
        <NavUser user={{ name, email, role }} />
    </Sidebar.Header>
    <Sidebar.Content>
        {#if role === "admin"}
            <NavMain items={data.navMain} />
            <NavDocuments items={data.documents} />
        {/if}
        <!-- <NavSecondary items={data.navSecondary} class="mt-auto" /> -->
    </Sidebar.Content>
</Sidebar.Root>
