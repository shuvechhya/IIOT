<script lang="ts">
    import { Button, buttonVariants } from "$lib/components/ui/button/index.js";
    import * as Dialog from "$lib/components/ui/dialog/index.js";
    import { Input } from "$lib/components/ui/input/index.js";
    import { Label } from "$lib/components/ui/label/index.js";
    import { createAnalytics } from "$lib/api/admin.remote";
    import { toast } from "svelte-sonner";
    import Plus from "@tabler/icons-svelte/icons/plus";

    let name = $state<string>("");
    let src = $state<string>("");

    const refreshForm = async () => {
        name = "";
        src = "";
    };

    const handleSubmit = async () => {
        try {
            await createAnalytics({
                name: name,
                src: src,
            });
            await refreshForm();
            toast.success("Create Analytics", {
                description: "Successfully created analytics graph!",
            });
        } catch (e) {
            toast.error("Create Analytics", {
                description: `Error creating analtyics graph: ${e}`,
            });
        }
    };
</script>

<Dialog.Root>
    <Dialog.Trigger
        class={buttonVariants({ variant: "outline", class: "cursor-pointer" })}
        ><Plus />Create Analytics Graph</Dialog.Trigger
    >
    <Dialog.Content class="sm:max-w-[425px]">
        <Dialog.Header>
            <Dialog.Title>Create User</Dialog.Title>
            <Dialog.Description
                >Create Analytics Graph by adding shared url from Grafana</Dialog.Description
            >
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
                <Button type="submit">Create Analytics</Button>
            </Dialog.Footer>
        </form>
    </Dialog.Content>
</Dialog.Root>
