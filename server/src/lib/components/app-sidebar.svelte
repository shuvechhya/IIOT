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

  const data = {
    user: {
      name: "shadcn",
      email: "m@example.com",
      avatar: "/avatars/shadcn.jpg",
    },
    navMain: [
      {
        title: "Dashboard",
        url: "#",
        icon: DashboardIcon,
      },
      {
        title: "Analytics",
        url: "#",
        icon: ChartBarIcon,
      },
    ],
    // navClouds: [
    //     {
    //         title: "Capture",
    //         icon: CameraIcon,
    //         isActive: true,
    //         url: "#",
    //         items: [
    //             {
    //                 title: "Active Proposals",
    //                 url: "#",
    //             },
    //             {
    //                 title: "Archived",
    //                 url: "#",
    //             },
    //         ],
    //     },
    //     {
    //         title: "Proposal",
    //         icon: FileDescriptionIcon,
    //         url: "#",
    //         items: [
    //             {
    //                 title: "Active Proposals",
    //                 url: "#",
    //             },
    //             {
    //                 title: "Archived",
    //                 url: "#",
    //             },
    //         ],
    //     },
    //     {
    //         title: "Prompts",
    //         icon: FileAiIcon,
    //         url: "#",
    //         items: [
    //             {
    //                 title: "Active Proposals",
    //                 url: "#",
    //             },
    //             {
    //                 title: "Archived",
    //                 url: "#",
    //             },
    //         ],
    //     },
    // ],
    navSecondary: [
      {
        title: "Settings",
        url: "#",
        icon: SettingsIcon,
      },
      {
        title: "Get Help",
        url: "#",
        icon: HelpIcon,
      },
      {
        title: "Search",
        url: "#",
        icon: SearchIcon,
      },
    ],
    documents: [
      {
        name: "Settings",
        url: "#",
        icon: SettingsIcon,
      },
      // {
      //     name: "Data Library",
      //     url: "#",
      //     icon: DatabaseIcon,
      // },
      // {
      //     name: "Reports",
      //     url: "#",
      //     icon: ReportIcon,
      // },
      // {
      //     name: "Word Assistant",
      //     url: "#",
      //     icon: FileWordIcon,
      // },
    ],
  };

  let { ...restProps }: ComponentProps<typeof Sidebar.Root> = $props();
</script>

<Sidebar.Root collapsible="offcanvas" {...restProps}>
  <Sidebar.Header>
    <NavUser user={data.user} />
  </Sidebar.Header>
  <Sidebar.Content>
    <NavMain items={data.navMain} />
    <NavDocuments items={data.documents} />
    <!-- <NavSecondary items={data.navSecondary} class="mt-auto" /> -->
  </Sidebar.Content>
</Sidebar.Root>
