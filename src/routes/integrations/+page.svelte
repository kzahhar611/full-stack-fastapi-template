<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import IntegrationsManager from '$lib/components/integrations/IntegrationsManager.svelte';
    
    // Check authentication
    onMount(() => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            goto('/login');
            return;
        }
    });
</script>

<svelte:head>
    <title>Third-Party Integrations - TenderWise AI</title>
    <meta name="description" content="Connect with ERP, CRM, and procurement platforms to enhance your RFP workflow" />
</svelte:head>

<IntegrationsManager />