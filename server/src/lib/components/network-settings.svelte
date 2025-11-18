<script lang="ts">
    import ChevronDownIcon from "@lucide/svelte/icons/chevron-down";
    import {
        type ColumnDef,
        type ColumnFiltersState,
        type PaginationState,
        type RowSelectionState,
        type SortingState,
        type VisibilityState,
        type Row,
        getCoreRowModel,
        getFilteredRowModel,
        getPaginationRowModel,
        getSortedRowModel,
    } from "@tanstack/table-core";
    import { createRawSnippet } from "svelte";
    import * as Table from "$lib/components/ui/table/index.js";
    import { Button } from "$lib/components/ui/button/index.js";
    import * as DropdownMenu from "$lib/components/ui/dropdown-menu/index.js";
    import { Input } from "$lib/components/ui/input/index.js";
    import {
        FlexRender,
        createSvelteTable,
        renderComponent,
        renderSnippet,
    } from "$lib/components/ui/data-table/index.js";
    import { networkSchema } from "$lib/schema/network";
    import z from "zod";
    import DialogConnect from "./network/dialog_connect.svelte";
    import Badge from "./ui/badge/badge.svelte";
    import { listNetworks } from "$lib/api/network.remote";
    import DataTableCheckbox from "./data-table-checkbox.svelte";
    import DotsVerticalIcon from "@tabler/icons-svelte/icons/dots-vertical";

    type Network = z.infer<typeof networkSchema>;

    let { data }: { data: Network[] } = $props();

    const columns: ColumnDef<Network>[] = [
        // {
        //     id: "select",
        //     header: ({ table }) =>
        //         renderComponent(DataTableCheckbox, {
        //             checked: table.getIsAllPageRowsSelected(),
        //             indeterminate:
        //                 table.getIsSomePageRowsSelected() &&
        //                 !table.getIsAllPageRowsSelected(),
        //             onCheckedChange: (value) =>
        //                 table.toggleAllPageRowsSelected(!!value),
        //             "aria-label": "Select all",
        //         }),
        //     cell: ({ row }) =>
        //         renderComponent(DataTableCheckbox, {
        //             checked: row.getIsSelected(),
        //             onCheckedChange: (value) => row.toggleSelected(!!value),
        //             "aria-label": "Select row",
        //         }),
        //     enableSorting: false,
        //     enableHiding: false,
        // },
        {
            accessorKey: "ssid",
            header: "SSID",
            cell: ({ row }) => renderSnippet(DataTableSsid, { row }),
        },
        {
            accessorKey: "signal",
            header: "Signal",
            cell: ({ row }) => renderSnippet(DataTableSignal, { row }),
        },
        {
            accessorKey: "security",
            header: "Security",
            cell: ({ row }) => renderSnippet(DataTableSecurity, { row }),
        },
        {
            id: "actions",
            enableHiding: false,
            cell: ({ row }) => renderSnippet(DataTableActions, { row }),
        },
    ];

    let pagination = $state<PaginationState>({ pageIndex: 0, pageSize: 10 });
    let sorting = $state<SortingState>([]);
    let columnFilters = $state<ColumnFiltersState>([]);
    let rowSelection = $state<RowSelectionState>({});
    let columnVisibility = $state<VisibilityState>({});

    const table = createSvelteTable({
        get data() {
            return data;
        },
        columns,
        state: {
            get pagination() {
                return pagination;
            },
            get sorting() {
                return sorting;
            },
            get columnVisibility() {
                return columnVisibility;
            },
            get rowSelection() {
                return rowSelection;
            },
            get columnFilters() {
                return columnFilters;
            },
        },
        getCoreRowModel: getCoreRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        onPaginationChange: (updater) => {
            if (typeof updater === "function") {
                pagination = updater(pagination);
            } else {
                pagination = updater;
            }
        },
        onSortingChange: (updater) => {
            if (typeof updater === "function") {
                sorting = updater(sorting);
            } else {
                sorting = updater;
            }
        },
        onColumnFiltersChange: (updater) => {
            if (typeof updater === "function") {
                columnFilters = updater(columnFilters);
            } else {
                columnFilters = updater;
            }
        },
        onColumnVisibilityChange: (updater) => {
            if (typeof updater === "function") {
                columnVisibility = updater(columnVisibility);
            } else {
                columnVisibility = updater;
            }
        },
        onRowSelectionChange: (updater) => {
            if (typeof updater === "function") {
                rowSelection = updater(rowSelection);
            } else {
                rowSelection = updater;
            }
        },
    });
</script>

<div class="w-full flex-col justify-start gap-6 px-4">
    <div class="flex items-center justify-between px-4 py-6 lg:px-6">
        <Input
            placeholder="Filter SSID..."
            value={(table.getColumn("ssid")?.getFilterValue() as string) ?? ""}
            oninput={(e) =>
                table.getColumn("ssid")?.setFilterValue(e.currentTarget.value)}
            onchange={(e) => {
                table.getColumn("ssid")?.setFilterValue(e.currentTarget.value);
            }}
            class="max-w-sm"
        />
        <DropdownMenu.Root>
            <DropdownMenu.Trigger>
                {#snippet child({ props })}
                    <Button {...props} variant="outline" class="ml-auto">
                        Columns <ChevronDownIcon class="ml-2 size-4" />
                    </Button>
                {/snippet}
            </DropdownMenu.Trigger>
            <DropdownMenu.Content align="end">
                {#each table
                    .getAllColumns()
                    .filter((col) => col.getCanHide()) as column (column)}
                    <DropdownMenu.CheckboxItem
                        class="capitalize"
                        bind:checked={
                            () => column.getIsVisible(),
                            (v) => column.toggleVisibility(!!v)
                        }
                    >
                        {column.id}
                    </DropdownMenu.CheckboxItem>
                {/each}
            </DropdownMenu.Content>
        </DropdownMenu.Root>
    </div>
    <div class="rounded-md border">
        <Table.Root>
            <Table.Header>
                {#each table.getHeaderGroups() as headerGroup (headerGroup.id)}
                    <Table.Row>
                        {#each headerGroup.headers as header (header.id)}
                            <Table.Head class="[&:has([role=checkbox])]:pl-3">
                                {#if !header.isPlaceholder}
                                    <FlexRender
                                        content={header.column.columnDef.header}
                                        context={header.getContext()}
                                    />
                                {/if}
                            </Table.Head>
                        {/each}
                    </Table.Row>
                {/each}
            </Table.Header>
            <Table.Body>
                {#each table.getRowModel().rows as row (row.id)}
                    <Table.Row data-state={row.getIsSelected() && "selected"}>
                        {#each row.getVisibleCells() as cell (cell.id)}
                            <Table.Cell class="[&:has([role=checkbox])]:pl-3">
                                <FlexRender
                                    content={cell.column.columnDef.cell}
                                    context={cell.getContext()}
                                />
                            </Table.Cell>
                        {/each}
                    </Table.Row>
                {:else}
                    <Table.Row>
                        <Table.Cell
                            colspan={columns.length}
                            class="h-24 text-center"
                        >
                            No results.
                        </Table.Cell>
                    </Table.Row>
                {/each}
            </Table.Body>
        </Table.Root>
    </div>
    <div class="flex items-center justify-end space-x-2 pt-4">
        <div class="text-muted-foreground flex-1 text-sm">
            {table.getFilteredSelectedRowModel().rows.length} of
            {table.getFilteredRowModel().rows.length} row(s) selected.
        </div>
        <div class="space-x-2">
            <Button
                variant="outline"
                size="sm"
                onclick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
            >
                Previous
            </Button>
            <Button
                variant="outline"
                size="sm"
                onclick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
            >
                Next
            </Button>
        </div>
    </div>
</div>

{#snippet DataTableSsid({ row }: { row: Row<z.Infer<typeof networkSchema>> })}
    <div class="w-32">
        <Badge variant="outline" class="text-muted-foreground px-1.5">
            {row.original.ssid}
        </Badge>
    </div>
{/snippet}

{#snippet DataTableSignal({ row }: { row: Row<z.Infer<typeof networkSchema>> })}
    <div class="w-32">
        <Badge variant="outline" class="text-muted-foreground px-1.5">
            {row.original.signal}
        </Badge>
    </div>
{/snippet}

{#snippet DataTableSecurity({
    row,
}: {
    row: Row<z.Infer<typeof networkSchema>>;
})}
    <div class="w-32">
        <Badge variant="outline" class="text-muted-foreground px-1.5">
            {row.original.security}
        </Badge>
    </div>
{/snippet}

{#snippet DataTableActions({
    row,
}: {
    row: Row<z.infer<typeof networkSchema>>;
})}
    <DropdownMenu.Root>
        <DropdownMenu.Trigger
            class="data-[state=open]:bg-muted text-muted-foreground flex size-8"
        >
            {#snippet child({ props })}
                <Button variant="ghost" size="icon" {...props}>
                    <DotsVerticalIcon />
                    <span class="sr-only">Open menu</span>
                </Button>
            {/snippet}
        </DropdownMenu.Trigger>
        <DropdownMenu.Content align="end" class="w-32">
            <DropdownMenu.Item onclick={(e) => e.preventDefault()}>
                <DialogConnect
                    ssid={row.original.ssid}
                    security={row.original.security}
                    signal={row.original.signal}
                />
            </DropdownMenu.Item>
        </DropdownMenu.Content>
    </DropdownMenu.Root>
{/snippet}
