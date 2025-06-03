<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Header from '$lib/components/Header.svelte';
	import { writable } from 'svelte/store';
	
	// Sidebar state
	export const sidebarCollapsed = writable(false);
	
	// Redirect if not authenticated
	onMount(() => {
		const unsubscribe = authStore.subscribe((auth) => {
			if (!auth.isAuthenticated) {
				goto('/login');
			}
		});
		
		return unsubscribe;
	});
	
	// Toggle sidebar
	function toggleSidebar() {
		sidebarCollapsed.update(collapsed => !collapsed);
	}
</script>

<svelte:head>
	<title>TenderWise AI - Enterprise RFP Platform</title>
</svelte:head>

{#if $authStore.isAuthenticated}
	<div class="flex h-screen bg-gray-950 text-white">
		<!-- Sidebar -->
		<Sidebar collapsed={$sidebarCollapsed} />
		
		<!-- Main Content Area -->
		<div class="flex-1 flex flex-col {$sidebarCollapsed ? 'lg:ml-16' : 'lg:ml-64'} transition-all duration-300">
			<!-- Header -->
			<Header on:toggleSidebar={toggleSidebar} />
			
			<!-- Page Content -->
			<main class="flex-1 overflow-y-auto p-6">
				<slot />
			</main>
		</div>
	</div>
	
	<!-- Mobile Sidebar Overlay -->
	{#if !$sidebarCollapsed}
		<div 
			class="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
			on:click={toggleSidebar}
			on:keydown={(e) => e.key === 'Escape' && toggleSidebar()}
		></div>
	{/if}
{:else}
	<!-- Loading state while checking authentication -->
	<div class="min-h-screen bg-gray-950 flex items-center justify-center">
		<div class="text-center">
			<div class="spinner w-8 h-8 mx-auto mb-4"></div>
			<p class="text-gray-400">Loading...</p>
		</div>
	</div>
{/if}