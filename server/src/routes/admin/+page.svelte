<script lang="ts">
    import * as Sidebar from "$lib/components/ui/sidebar/index.js";
    import AppSidebar from "$lib/components/app-sidebar.svelte";
    import SiteHeader from "$lib/components/site-header.svelte";
    import DataTable from "$lib/components/data-table.svelte";
    import { listUsers } from "$lib/api/admin.remote";
    import { usersSchema } from "$lib/schema/users";

    // const loadUser = async () => {
    //     let users = await listUsers();
    //     let parsedUsers: z.Infer<typeof usersSchema>[] = [];
    //     users.map((user) => {
    //         parsedUsers.push({
    //             id: user.id,
    //             name: user.name,
    //             email: user.email,
    //             emailVerified: user.emailVerified,
    //             image: user.image,
    //             createdAt: user.createdAt,
    //             updatedAt: user.updatedAt,
    //             role: user.role,
    //             banned: user.banned,
    //             banReason: user.banReason,
    //             banExpires: user.banExpires,
    //         });
    //     });
    //     return parsedUsers;
    // };
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
                    <!-- <SectionCards /> -->
                    <!-- <div class="px-4 lg:px-6">
                        <ChartAreaInteractive />
                    </div> -->
                    <!-- {#await loadUser()}
                        <p>Awaiting for lists</p>
                    {:then users}
                        <DataTable data={users} />
                    {:catch error}
                        <p>Something Went wrong</p>
                    {/await} -->
                </div>
            </div>
        </div>
    </Sidebar.Inset>
</Sidebar.Provider>
