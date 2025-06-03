<!-- RFP Document Management Page -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { fade } from 'svelte/transition';
	import DocumentManager from '$lib/components/document/DocumentManager.svelte';
	import { authStore } from '$lib/stores/auth';
	import type { RFPEnhanced } from '$lib/types/rfp';

	let rfpId: number;
	let rfp: RFPEnhanced | null = null;
	let loading = true;
	let error = '';

	$: rfpId = parseInt($page.params.id);

	onMount(() => {
		if (!$authStore.isAuthenticated) {
			goto('/auth/signin');
			return;
		}
		loadRFP();
	});

	async function loadRFP() {
		loading = true;
		error = '';
		
		try {
			const response = await fetch(`/api/v1/rfps-enhanced/${rfpId}`, {
				headers: {
					'Authorization': `Bearer ${$authStore.token}`
				}
			});

			if (!response.ok) {
				if (response.status === 404) {
					error = 'RFP not found';
				} else if (response.status === 403) {
					error = 'Access denied';
				} else {
					throw new Error(`HTTP ${response.status}: ${response.statusText}`);
				}
				return;
			}

			rfp = await response.json();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load RFP';
			console.error('Error loading RFP:', err);
		} finally {
			loading = false;
		}
	}

	function getStatusColor(status: string): string {
		const colors = {
			'DRAFT': 'bg-gray-500/20 text-gray-300',
			'PUBLISHED': 'bg-blue-500/20 text-blue-300',
			'OPEN': 'bg-green-500/20 text-green-300',
			'CLOSED': 'bg-yellow-500/20 text-yellow-300',
			'AWARDED': 'bg-purple-500/20 text-purple-300'
		};
		return colors[status] || colors['DRAFT'];
	}
</script>

<svelte:head>
	<title>Document Management - {rfp?.title || 'RFP'} | TenderWise AI</title>
</svelte:head>

<div class="min-h-screen bg-gray-950 text-white">
	<!-- Header -->
	<div class="border-b border-gray-800 bg-gray-900">
		<div class="max-w-7xl mx-auto px-4 py-6">
			{#if loading}
				<div class="animate-pulse">
					<div class="h-8 bg-gray-700 rounded w-1/3 mb-4"></div>
					<div class="h-4 bg-gray-700 rounded w-1/2"></div>
				</div>
			{:else if error}
				<div class="text-center py-8">
					<div class="text-red-400 mb-4">⚠️ {error}</div>
					<button
						class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
						on:click={() => goto('/app/rfps')}
					>
						Back to RFPs
					</button>
				</div>
			{:else if rfp}
				<div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
					<div class="flex-1">
						<!-- Breadcrumb -->
						<nav class="flex items-center gap-2 text-sm text-gray-400 mb-3">
							<a href="/app" class="hover:text-white transition-colors">Dashboard</a>
							<span>›</span>
							<a href="/app/rfps" class="hover:text-white transition-colors">RFPs</a>
							<span>›</span>
							<a href="/app/rfps/{rfpId}" class="hover:text-white transition-colors">{rfp.title}</a>
							<span>›</span>
							<span class="text-white">Documents</span>
						</nav>

						<div class="flex items-start gap-4">
							<div class="flex-1">
								<h1 class="text-2xl font-bold text-white mb-2">
									Document Management
								</h1>
								<p class="text-gray-400 mb-3">
									Manage documents for: <span class="text-white font-medium">{rfp.title}</span>
								</p>
								<div class="flex flex-wrap items-center gap-3 text-sm">
									<span class={`px-2 py-1 rounded ${getStatusColor(rfp.status)}`}>
										{rfp.status}
									</span>
									<span class="text-gray-400">
										RFP #{rfp.id}
									</span>
									<span class="text-gray-400">
										Created {new Date(rfp.created_at).toLocaleDateString()}
									</span>
								</div>
							</div>
						</div>
					</div>

					<!-- Actions -->
					<div class="flex items-center gap-3">
						<a
							href="/app/rfps/{rfpId}"
							class="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
						>
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
							</svg>
							Back to RFP
						</a>
						
						<a
							href="/app/rfps/{rfpId}/edit"
							class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
						>
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
							</svg>
							Edit RFP
						</a>
					</div>
				</div>
			{/if}
		</div>
	</div>

	<!-- Main Content -->
	<div class="max-w-7xl mx-auto px-4 py-8">
		{#if rfp && !loading && !error}
			<div transition:fade={{ duration: 300 }}>
				<DocumentManager 
					{rfpId} 
					readonly={rfp.status === 'AWARDED'}
				/>
			</div>
		{/if}
	</div>
</div>

<style>
	/* Custom scrollbar for document lists */
	:global(.document-manager .overflow-y-auto::-webkit-scrollbar) {
		width: 6px;
	}

	:global(.document-manager .overflow-y-auto::-webkit-scrollbar-track) {
		background: #374151;
		border-radius: 3px;
	}

	:global(.document-manager .overflow-y-auto::-webkit-scrollbar-thumb) {
		background: #6b7280;
		border-radius: 3px;
	}

	:global(.document-manager .overflow-y-auto::-webkit-scrollbar-thumb:hover) {
		background: #9ca3af;
	}
</style>