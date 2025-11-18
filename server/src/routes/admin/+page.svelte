<script lang="ts">
    import data from "./data.js";
    import * as Sidebar from "$lib/components/ui/sidebar/index.js";
    import AppSidebar from "$lib/components/app-sidebar.svelte";
    import SiteHeader from "$lib/components/site-header.svelte";
    import SectionCards from "$lib/components/section-cards.svelte";
    import ChartAreaInteractive from "$lib/components/chart-area-interactive.svelte";
    import DataTable from "$lib/components/data-table.svelte";
    import {
        deleteAnalytic,
        listAnalytics,
        listUsers,
    } from "$lib/api/admin.remote.js";
    import Button, {
        buttonVariants,
    } from "$lib/components/ui/button/button.svelte";
    import Spinner from "$lib/components/ui/spinner/spinner.svelte";
    import { DashboardNav } from "$lib/global/Global.svelte.js";
    import NetworkSettings from "$lib/components/network-settings.svelte";
    import {
        getConnectedNetwork,
        listIp,
        listNetworks,
    } from "$lib/api/network.remote.js";
    import Badge from "$lib/components/ui/badge/badge.svelte";
    import * as Card from "$lib/components/ui/card/index.js";
    import CreateAnalyticsDialog from "$lib/components/analytics/create-analytics-dialog.svelte";
    import EditCircle from "@tabler/icons-svelte/icons/edit-circle";
    import Variable from "@tabler/icons-svelte/icons/variable";
    import Trash from "@tabler/icons-svelte/icons/trash";
    import EditAnalyticsDialog from "$lib/components/analytics/edit-analytics-dialog.svelte";
    import { toast } from "svelte-sonner";
</script>

{#snippet Dashboard()}
    {#await listUsers()}
        <Button disabled size="sm">
            <Spinner />
            Loading...
        </Button>
    {:then data}
        <DataTable {data} />
    {:catch err}
        <p>There are problems in fetching Data</p>
    {/await}
{/snippet}

{#snippet Analytics()}
    {#await listAnalytics()}
        <Button disabled size="sm">
            <Spinner />
            Loading...
        </Button>
    {:then values}
        <div class="flex flex-col items-center py-3 gap-3 w-full">
            <div class="flex gap-6 justify-center w-full">
                <CreateAnalyticsDialog />
            </div>
            <div class="flex flex-col items-center gap-4 w-full h-screen">
                {#each values as value}
                    <Card.Root class="w-[60%] mx-5">
                        <Card.Header>
                            <div class="flex items-center w-full">
                                <p>
                                    Name: {value.name} | Id: {value.id}
                                </p>
                                <div class="flex ml-auto gap-3 items-center">
                                    <EditAnalyticsDialog id={value.id} />
                                    <Button
                                        class="bg-red-600 text-white hover:bg-red-500 cursor-pointer"
                                        onclick={async () => {
                                            await deleteAnalytic(value.id);
                                            toast.success("Delete Analytics", {
                                                description:
                                                    "Successfully deleted analytics graph!",
                                            });
                                        }}
                                    >
                                        <Trash />
                                        Delete
                                    </Button>
                                </div>
                            </div>
                        </Card.Header>
                        <Card.Content>
                            <iframe
                                src={value.src}
                                class="w-auto h-auto"
                                title={value.name}
                            ></iframe>
                        </Card.Content>
                        <Card.Footer
                            ><p>Created by: {value.user_id}</p></Card.Footer
                        >
                    </Card.Root>
                {/each}
            </div>
        </div>
    {/await}
{/snippet}
{#snippet Network()}
    {#await listNetworks()}
        <Button disabled size="sm">
            <Spinner />
            Loading...
        </Button>
    {:then data}
        <div class="flex flex-col items-center gap-3 h-screen">
            {#await listIp()}
                <Button disabled size="sm">
                    <Spinner />
                    Loading...
                </Button>
            {:then values}
                <div class="flex gap-3">
                    {#each values as value}
                        <Badge>{value.name} | {value.ip}</Badge>
                    {/each}
                </div>
            {/await}
            {#await getConnectedNetwork()}
                <Button disabled size="sm">
                    <Spinner />
                    Loading...
                </Button>
            {:then value}
                <Badge>{value}</Badge>
            {/await}
            <NetworkSettings {data} />
        </div>
    {:catch err}
        <p>There are problems in fetching Data</p>
    {/await}
{/snippet}

<Sidebar.Provider
    style="--sidebar-width: calc(var(--spacing) * 72); --header-height: calc(var(--spacing) * 12);"
>
    <AppSidebar variant="inset" />
    <Sidebar.Inset>
        <SiteHeader />
        <div class="flex flex-1 flex-col">
            <div class="@container/main flex flex-1 flex-col gap-2">
                <div class="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
                    {#if DashboardNav.id === "dashboard"}
                        {@render Dashboard()}
                    {:else if DashboardNav.id === "analytics"}
                        {@render Analytics()}
                    {:else if DashboardNav.id === "network_settings"}
                        {@render Network()}
                    {/if}
                </div>
            </div>
        </div>
    </Sidebar.Inset>
</Sidebar.Provider>
