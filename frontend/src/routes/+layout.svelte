<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	
	// Check authentication status on app start
	onMount(() => {
		if (browser) {
			authStore.initialize();
		}
	});
	
	// Redirect logic based on auth status and current route
	$: if (browser) {
		const isAuthRoute = $page.route.id?.startsWith('/(auth)');
		const isPublicRoute = $page.route.id === '/' || $page.route.id?.startsWith('/public');
		
		if (!$authStore.isAuthenticated && !isAuthRoute && !isPublicRoute) {
			goto('/auth/login');
		} else if ($authStore.isAuthenticated && isAuthRoute) {
			goto('/dashboard');
		}
	}
</script>

<div class="min-h-screen bg-gray-950 text-white">
	<slot />
</div>

<style>
	:global(body) {
		font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	}
</style>