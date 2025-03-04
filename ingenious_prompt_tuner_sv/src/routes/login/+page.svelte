<script lang="ts">
    import { _username as importedUsername, _password as importedPassword, _error, _login } from './+page';
    let username = importedUsername;
    let password = importedPassword;
</script>

<style>
    .error {
        color: red;
    }
</style>

<div>
    <h1>Login</h1>
    <form on:submit|preventDefault={_login}>
        <label>
            Username:
            <input type="text" bind:value={username} />
        </label>
        <label>
            Password:
            <input type="password" bind:value={password} />
        </label>
        <button type="submit">Login</button>
    </form>
    {#if _error}
        <p class="error">{_error}</p>
    {/if}
</div>