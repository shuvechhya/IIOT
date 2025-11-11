<script lang="ts">
  import "../app.css";
  let { children } = $props();
  import { Toaster } from "$lib/components/ui/sonner/index";
</script>

<Toaster richColors position="top-center" />

{@render children()}
