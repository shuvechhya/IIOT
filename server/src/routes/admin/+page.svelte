<script lang="ts">
    import data from "./data.js";
    import * as Sidebar from "$lib/components/ui/sidebar/index.js";
    import AppSidebar from "$lib/components/app-sidebar.svelte";
    import SiteHeader from "$lib/components/site-header.svelte";
    import SectionCards from "$lib/components/section-cards.svelte";
    import ChartAreaInteractive from "$lib/components/chart-area-interactive.svelte";
    import DataTable from "$lib/components/data-table.svelte";
    import { listUsers } from "$lib/api/admin.remote.js";
</script>

<Sidebar.Provider
    style="--sidebar-width: calc(var(--spacing) * 72); --header-height: calc(var(--spacing) * 12);"
>
    <AppSidebar variant="inset" />
    <Sidebar.Inset>
        <SiteHeader />
        <div class="flex flex-1 flex-col">
            <div class="@container/main flex flex-1 flex-col gap-2">
                <div class="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
                    {#await listUsers()}
                        <p>Something</p>
                    {:then data}
                        <DataTable {data} />
                    {:catch err}
                        <p>There are problems in fetching Data</p>
                    {/await}
                </div>
            </div>
        </div>
    </Sidebar.Inset>
</Sidebar.Provider>
