<script lang="ts">
    import { Button, buttonVariants } from "$lib/components/ui/button/index.js";
    import * as Dialog from "$lib/components/ui/dialog/index.js";
    import { Input } from "$lib/components/ui/input/index.js";
    import { Label } from "$lib/components/ui/label/index.js";
    import {
        createAnalytics,
        getAnalytic,
        updateAnalytic,
    } from "$lib/api/admin.remote";
    import { toast } from "svelte-sonner";
    import EditCircle from "@tabler/icons-svelte/icons/edit-circle";

    let { id }: { id: string } = $props();

    let analytic = await getAnalytic(id);
    let name = $state<string>(analytic?.name ?? "");
    let src = $state<string>(analytic?.src ?? "");

    const refreshForm = async () => {
        name = "";
        src = "";
    };

    const handleSubmit = async () => {
        try {
            await updateAnalytic({
                id: id,
                name: name,
                src: src,
            });
            await refreshForm();
            toast.success("Edit Analytics", {
                description: "Successfully updated analytics graph!",
            });
        } catch (e) {
            toast.error("Edit Analytics", {
                description: `Error updating analtyics graph: ${e}`,
            });
        }
    };
</script>

<Dialog.Root>
    <Dialog.Trigger
        class={buttonVariants({
            variant: "default",
            class: "bg-amber-600 text-white hover:bg-amber-500 cursor-pointer",
        })}><EditCircle />Edit</Dialog.Trigger
    >
    <Dialog.Content class="sm:max-w-[425px]">
        <Dialog.Header>
            <Dialog.Title>Edit Analytics Graph</Dialog.Title>
            <Dialog.Description>Update Analytics Graph</Dialog.Description>
        </Dialog.Header>
        <form onsubmit={handleSubmit}>
            <div class="grid gap-4 py-4">
                <div class="grid grid-cols-4 items-center gap-4">
                    <Label for="name" class="text-right">Name</Label>
                    <Input class="col-span-3" bind:value={name} required />
                </div>
                <div class="grid grid-cols-4 items-center gap-4">
                    <Label for="email" class="text-right">Src</Label>
                    <Input class="col-span-3" bind:value={src} required />
                </div>
            </div>
            <Dialog.Footer>
                <Button type="submit">Update Analytic</Button>
            </Dialog.Footer>
        </form>
    </Dialog.Content>
</Dialog.Root>
