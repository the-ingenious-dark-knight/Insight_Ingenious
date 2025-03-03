<script lang="ts">
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>


<div>
    <h1>Diagnostic Data</h1>
    <ul>
        {#each Object.entries(data.props.data) as [key, value]}
            <li><strong>{key}:</strong> {value}</li>
        {/each}
    </ul>
</div>
