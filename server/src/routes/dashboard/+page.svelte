<script lang="ts">
    import * as Sidebar from "$lib/components/ui/sidebar/index.js";
    import AppSidebar from "$lib/components/app-sidebar.svelte";
    import SiteHeader from "$lib/components/site-header.svelte";
    import SectionCards from "$lib/components/section-cards.svelte";
    import ChartAreaInteractive from "$lib/components/chart-area-interactive.svelte";
    import DataTable from "$lib/components/data-table.svelte";
    import { listUsers } from "$lib/api/admin.remote.js";
    import TokenForm from "$lib/components/token-form.svelte";
</script>

<Sidebar.Provider
    style="--sidebar-width: calc(var(--spacing) * 72); --header-height: calc(var(--spacing) * 12);"
>
    <AppSidebar variant="inset" />
    <Sidebar.Inset>
        <SiteHeader />
        <div class="flex flex-1 flex-col">
            <div class="@container/main flex flex-1 flex-col gap-2">
                <div class="flex justify-center items-center w-full h-full">
                    <TokenForm />
                </div>
            </div>
        </div>
    </Sidebar.Inset>
</Sidebar.Provider>
