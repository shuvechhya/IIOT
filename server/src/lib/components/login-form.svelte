<script lang="ts">
    import { Button } from "$lib/components/ui/button/index.js";
    import * as Card from "$lib/components/ui/card/index.js";
    import { Input } from "$lib/components/ui/input/index.js";
    import {
        FieldGroup,
        Field,
        FieldLabel,
        FieldDescription,
    } from "$lib/components/ui/field/index.js";

    const id = $props.id();

    let email: string = $state("");
    let password: string = $state("");

    const handleSubmit = () => {
        return;
    };
</script>

<Card.Root class="mx-auto w-full max-w-sm">
    <Card.Header>
        <Card.Title class="text-2xl">Login</Card.Title>
        <Card.Description>Enter your credentials below</Card.Description>
    </Card.Header>
    <Card.Content>
        <form onsubmit={handleSubmit}>
            <FieldGroup>
                <Field>
                    <FieldLabel for="email-{id}">Email</FieldLabel>
                    <Input
                        id="email-{id}"
                        type="email"
                        placeholder="m@example.com"
                        required
                    />
                </Field>
                <Field>
                    <FieldLabel for="password-{id}">Password</FieldLabel>
                    <Input id="password-{id}" type="password" required />
                </Field>
                <Field>
                    <Button type="submit" class="w-full">Login</Button>
                    <FieldDescription class="text-center">
                        Don't have an account? Please contact your admin.
                    </FieldDescription>
                </Field>
            </FieldGroup>
        </form>
    </Card.Content>
</Card.Root>
