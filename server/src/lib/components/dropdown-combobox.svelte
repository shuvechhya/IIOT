<script lang="ts">
  import CheckIcon from "@lucide/svelte/icons/check";
  import ChevronsUpDownIcon from "@lucide/svelte/icons/chevrons-up-down";
  import { tick } from "svelte";
  import * as Command from "$lib/components/ui/command/index.js";
  import * as Popover from "$lib/components/ui/popover/index.js";
  import { Button } from "$lib/components/ui/button/index.js";
  import { cn } from "$lib/utils.js";

  let {
    roles,
    value = $bindable(),
  }: {
    roles: {
      value: "gateway" | "admin" | "manager";
      label: string;
    }[];
    value: "gateway" | "admin" | "manager";
  } = $props();
  let open = $state(false);
  let triggerRef = $state<HTMLButtonElement>(null!);

  const selectedValue = $derived(roles.find((f) => f.value === value)?.label);

  // We want to refocus the trigger button when the user selects
  // an item from the list so users can continue navigating the
  // rest of the form with the keyboard.
  function closeAndFocusTrigger() {
    open = false;
    tick().then(() => {
      triggerRef.focus();
    });
  }
</script>

<Popover.Root bind:open>
  <Popover.Trigger bind:ref={triggerRef}>
    {#snippet child({ props })}
      <Button
        {...props}
        variant="outline"
        class="w-[200px] justify-between"
        role="combobox"
        aria-expanded={open}
      >
        {selectedValue || "Select a role..."}
        <ChevronsUpDownIcon class="opacity-50" />
      </Button>
    {/snippet}
  </Popover.Trigger>
  <Popover.Content class="w-[200px] p-0">
    <Command.Root>
      <Command.Input placeholder="Search role..." />
      <Command.List>
        <Command.Empty>No role found.</Command.Empty>
        <Command.Group value="roles">
          {#each roles as role (role.value)}
            <Command.Item
              value={role.value}
              onSelect={() => {
                value = role.value;
                closeAndFocusTrigger();
              }}
            >
              <CheckIcon
                class={cn(value !== role.value && "text-transparent")}
              />
              {role.label}
            </Command.Item>
          {/each}
        </Command.Group>
      </Command.List>
    </Command.Root>
  </Popover.Content>
</Popover.Root>
