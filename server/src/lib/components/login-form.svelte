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
    import { login } from "$lib/api/auth.remote";

    const id = $props.id();
    // let email = $state<string>("");
    // let password = $state<string>("");
</script>

<Card.Root class="mx-auto w-full max-w-sm">
    <Card.Header>
        <Card.Title class="text-2xl">Login</Card.Title>
        <Card.Description>Enter your credentials below</Card.Description>
    </Card.Header>
    <Card.Content>
        <form {...login}>
            <FieldGroup>
                <Field>
                    <FieldLabel for="email-{id}">Email</FieldLabel>
                    <Input
                        {...login.fields.email.as("email")}
                        placeholder="m@example.com"
                        required
                    />
                </Field>
                <Field>
                    <FieldLabel for="password-{id}">Password</FieldLabel>
                    <Input {...login.fields.password.as("password")} required />
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
