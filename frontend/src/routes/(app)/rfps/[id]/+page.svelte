<!-- RFP Detail Page with Document Management Integration -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { fade } from 'svelte/transition';
	import { authStore } from '$lib/stores/auth';
	import type { RFPEnhanced } from '$lib/types/rfp';
	import AIChatInterface from '$lib/components/ai/AIChatInterface.svelte';
	import AIInsights from '$lib/components/ai/AIInsights.svelte';

	let rfpId: number;
	let rfp: RFPEnhanced | null = null;
	let loading = true;
	let error = '';
	let activeTab = 'overview';

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

	function getPriorityColor(priority: string): string {
		const colors = {
			'LOW': 'bg-green-500/20 text-green-300',
			'MEDIUM': 'bg-yellow-500/20 text-yellow-300',
			'HIGH': 'bg-red-500/20 text-red-300',
			'URGENT': 'bg-red-600/20 text-red-300'
		};
		return colors[priority] || colors['MEDIUM'];
	}

	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD'
		}).format(amount);
	}

	$: canEdit = $authStore.user?.role && !['viewer'].includes($authStore.user.role) && rfp?.status !== 'AWARDED';
</script>

<svelte:head>
	<title>{rfp?.title || 'RFP'} | TenderWise AI</title>
</svelte:head>

<div class="min-h-screen bg-gray-950 text-white">
	{#if loading}
		<div class="flex items-center justify-center min-h-screen">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
			<span class="ml-3 text-gray-400">Loading RFP...</span>
		</div>
	{:else if error}
		<div class="flex items-center justify-center min-h-screen">
			<div class="text-center">
				<div class="text-red-400 mb-4">⚠️ {error}</div>
				<button
					class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
					on:click={() => goto('/app/rfps')}
				>
					Back to RFPs
				</button>
			</div>
		</div>
	{:else if rfp}
		<!-- Header -->
		<div class="border-b border-gray-800 bg-gray-900">
			<div class="max-w-7xl mx-auto px-4 py-6">
				<div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
					<div class="flex-1">
						<!-- Breadcrumb -->
						<nav class="flex items-center gap-2 text-sm text-gray-400 mb-3">
							<a href="/app" class="hover:text-white transition-colors">Dashboard</a>
							<span>›</span>
							<a href="/app/rfps" class="hover:text-white transition-colors">RFPs</a>
							<span>›</span>
							<span class="text-white">{rfp.title}</span>
						</nav>

						<div class="flex items-start gap-4">
							<div class="flex-1">
								<h1 class="text-2xl font-bold text-white mb-2">{rfp.title}</h1>
								<p class="text-gray-400 mb-3">{rfp.description}</p>
								<div class="flex flex-wrap items-center gap-3 text-sm">
									<span class={`px-2 py-1 rounded ${getStatusColor(rfp.status)}`}>
										{rfp.status}
									</span>
									<span class={`px-2 py-1 rounded ${getPriorityColor(rfp.priority)}`}>
										{rfp.priority} Priority
									</span>
									<span class="text-gray-400">
										RFP #{rfp.id}
									</span>
									<span class="text-gray-400">
										Created {formatDate(rfp.created_at)}
									</span>
								</div>
							</div>
						</div>
					</div>

					<!-- Actions -->
					<div class="flex items-center gap-3">
						{#if canEdit}
							<a
								href="/app/rfps/{rfpId}/edit"
								class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
								</svg>
								Edit RFP
							</a>
						{/if}
						
						<button
							class="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
							on:click={() => window.print()}
						>
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/>
							</svg>
							Print
						</button>
					</div>
				</div>

				<!-- Tabs -->
				<div class="mt-6">
					<nav class="flex space-x-8">
						<button
							class={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
								activeTab === 'overview'
									? 'border-blue-500 text-blue-400'
									: 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
							}`}
							on:click={() => activeTab = 'overview'}
						>
							Overview
						</button>
						<button
							class={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
								activeTab === 'content'
									? 'border-blue-500 text-blue-400'
									: 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
							}`}
							on:click={() => activeTab = 'content'}
						>
							Content
						</button>
						<a
							href="/app/rfps/{rfpId}/documents"
							class={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
								activeTab === 'documents'
									? 'border-blue-500 text-blue-400'
									: 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
							} flex items-center gap-2`}
						>
							📁 Documents
							<span class="bg-blue-500/20 text-blue-300 text-xs px-2 py-0.5 rounded-full">
								{rfp.document_count || 0}
							</span>
						</a>
						<button
							class={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
								activeTab === 'ai'
									? 'border-blue-500 text-blue-400'
									: 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
							} flex items-center gap-2`}
							on:click={() => activeTab = 'ai'}
						>
							🤖 AI Assistant
						</button>
						<button
							class={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
								activeTab === 'timeline'
									? 'border-blue-500 text-blue-400'
									: 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
							}`}
							on:click={() => activeTab = 'timeline'}
						>
							Timeline
						</button>
					</nav>
				</div>
			</div>
		</div>

		<!-- Main Content -->
		<div class="max-w-7xl mx-auto px-4 py-8">
			{#if activeTab === 'overview'}
				<div class="grid grid-cols-1 lg:grid-cols-3 gap-8" transition:fade={{ duration: 300 }}>
					<!-- Main Info -->
					<div class="lg:col-span-2 space-y-6">
						<!-- Summary Stats -->
						<div class="bg-gray-900 rounded-lg border border-gray-700 p-6">
							<h3 class="text-lg font-semibold text-white mb-4">Summary</h3>
							<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
								<div class="text-center">
									<div class="text-2xl font-bold text-blue-400">{rfp.budget ? formatCurrency(rfp.budget) : 'N/A'}</div>
									<div class="text-sm text-gray-400">Budget</div>
								</div>
								<div class="text-center">
									<div class="text-2xl font-bold text-green-400">{rfp.document_count || 0}</div>
									<div class="text-sm text-gray-400">Documents</div>
								</div>
								<div class="text-center">
									<div class="text-2xl font-bold text-purple-400">{rfp.download_count || 0}</div>
									<div class="text-sm text-gray-400">Downloads</div>
								</div>
								<div class="text-center">
									<div class="text-2xl font-bold text-yellow-400">{rfp.view_count || 0}</div>
									<div class="text-sm text-gray-400">Views</div>
								</div>
							</div>
						</div>

						<!-- Key Information -->
						<div class="bg-gray-900 rounded-lg border border-gray-700 p-6">
							<h3 class="text-lg font-semibold text-white mb-4">Key Information</h3>
							<div class="space-y-4">
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<div>
										<label class="block text-sm font-medium text-gray-400 mb-1">RFP Number</label>
										<div class="text-white">#{rfp.rfp_number || rfp.id}</div>
									</div>
									<div>
										<label class="block text-sm font-medium text-gray-400 mb-1">Category</label>
										<div class="text-white">{rfp.category || 'General'}</div>
									</div>
									<div>
										<label class="block text-sm font-medium text-gray-400 mb-1">Submission Deadline</label>
										<div class="text-white">
											{rfp.submission_deadline ? formatDate(rfp.submission_deadline) : 'Not set'}
										</div>
									</div>
									<div>
										<label class="block text-sm font-medium text-gray-400 mb-1">Contact Person</label>
										<div class="text-white">{rfp.contact_person || 'Not specified'}</div>
									</div>
								</div>
								
								{#if rfp.contact_email}
									<div>
										<label class="block text-sm font-medium text-gray-400 mb-1">Contact Email</label>
										<div class="text-white">
											<a href="mailto:{rfp.contact_email}" class="text-blue-400 hover:text-blue-300">
												{rfp.contact_email}
											</a>
										</div>
									</div>
								{/if}
							</div>
						</div>

						<!-- Requirements -->
						{#if rfp.requirements}
							<div class="bg-gray-900 rounded-lg border border-gray-700 p-6">
								<h3 class="text-lg font-semibold text-white mb-4">Requirements</h3>
								<div class="prose prose-invert max-w-none">
									{@html rfp.requirements}
								</div>
							</div>
						{/if}
					</div>

					<!-- Sidebar -->
					<div class="space-y-6">
						<!-- Quick Actions -->
						<div class="bg-gray-900 rounded-lg border border-gray-700 p-6">
							<h3 class="text-lg font-semibold text-white mb-4">Quick Actions</h3>
							<div class="space-y-3">
								<a
									href="/app/rfps/{rfpId}/documents"
									class="flex items-center gap-3 w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
								>
									<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
									</svg>
									Manage Documents
								</a>
								
								{#if canEdit}
									<a
										href="/app/rfps/{rfpId}/edit"
										class="flex items-center gap-3 w-full px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
									>
										<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
										</svg>
										Edit RFP Details
									</a>
								{/if}

								<button
									class="flex items-center gap-3 w-full px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
									on:click={() => {
										navigator.clipboard.writeText(window.location.href);
										alert('Link copied to clipboard!');
									}}
								>
									<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
									</svg>
									Copy Link
								</button>
							</div>
						</div>

						<!-- Timeline -->
						<div class="bg-gray-900 rounded-lg border border-gray-700 p-6">
							<h3 class="text-lg font-semibold text-white mb-4">Timeline</h3>
							<div class="space-y-4">
								<div class="flex items-center gap-3">
									<div class="w-3 h-3 bg-green-500 rounded-full"></div>
									<div>
										<div class="text-sm text-white">Created</div>
										<div class="text-xs text-gray-400">{formatDate(rfp.created_at)}</div>
									</div>
								</div>
								
								{#if rfp.published_at}
									<div class="flex items-center gap-3">
										<div class="w-3 h-3 bg-blue-500 rounded-full"></div>
										<div>
											<div class="text-sm text-white">Published</div>
											<div class="text-xs text-gray-400">{formatDate(rfp.published_at)}</div>
										</div>
									</div>
								{/if}

								{#if rfp.submission_deadline}
									<div class="flex items-center gap-3">
										<div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
										<div>
											<div class="text-sm text-white">Deadline</div>
											<div class="text-xs text-gray-400">{formatDate(rfp.submission_deadline)}</div>
										</div>
									</div>
								{/if}

								{#if rfp.updated_at && rfp.updated_at !== rfp.created_at}
									<div class="flex items-center gap-3">
										<div class="w-3 h-3 bg-purple-500 rounded-full"></div>
										<div>
											<div class="text-sm text-white">Last Updated</div>
											<div class="text-xs text-gray-400">{formatDate(rfp.updated_at)}</div>
										</div>
									</div>
								{/if}
							</div>
						</div>
					</div>
				</div>

			{:else if activeTab === 'content'}
				<div class="bg-gray-900 rounded-lg border border-gray-700 p-6" transition:fade={{ duration: 300 }}>
					<h3 class="text-lg font-semibold text-white mb-4">RFP Content</h3>
					{#if rfp.content}
						<div class="prose prose-invert max-w-none">
							{@html rfp.content}
						</div>
					{:else}
						<div class="text-gray-400 text-center py-8">
							No content available
						</div>
					{/if}
				</div>

			{:else if activeTab === 'ai'}
				<div class="grid grid-cols-1 lg:grid-cols-2 gap-8" transition:fade={{ duration: 300 }}>
					<!-- AI Insights -->
					<div>
						<AIInsights 
							rfpId={rfpId} 
							showUsageStats={$authStore.user?.role && ['super_admin', 'admin'].includes($authStore.user.role)}
						/>
					</div>

					<!-- AI Chat -->
					<div class="bg-gray-900 rounded-lg border border-gray-700 h-[600px]">
						<AIChatInterface 
							rfpId={rfpId}
							context={{
								rfp_title: rfp.title,
								rfp_status: rfp.status,
								rfp_category: rfp.category
							}}
							placeholder="Ask me about this RFP..."
						/>
					</div>
				</div>

			{:else if activeTab === 'timeline'}
				<div class="bg-gray-900 rounded-lg border border-gray-700 p-6" transition:fade={{ duration: 300 }}>
					<h3 class="text-lg font-semibold text-white mb-4">Activity Timeline</h3>
					<div class="space-y-6">
						<div class="flex items-start gap-4">
							<div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
								<svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
								</svg>
							</div>
							<div class="flex-1">
								<div class="text-white font-medium">RFP Created</div>
								<div class="text-sm text-gray-400">{formatDate(rfp.created_at)}</div>
								<div class="text-sm text-gray-400 mt-1">Initial RFP was created and saved as draft</div>
							</div>
						</div>

						{#if rfp.published_at}
							<div class="flex items-start gap-4">
								<div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
									<svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122"/>
									</svg>
								</div>
								<div class="flex-1">
									<div class="text-white font-medium">RFP Published</div>
									<div class="text-sm text-gray-400">{formatDate(rfp.published_at)}</div>
									<div class="text-sm text-gray-400 mt-1">RFP was made available to potential bidders</div>
								</div>
							</div>
						{/if}

						{#if rfp.updated_at && rfp.updated_at !== rfp.created_at}
							<div class="flex items-start gap-4">
								<div class="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
									<svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
									</svg>
								</div>
								<div class="flex-1">
									<div class="text-white font-medium">RFP Updated</div>
									<div class="text-sm text-gray-400">{formatDate(rfp.updated_at)}</div>
									<div class="text-sm text-gray-400 mt-1">RFP details were modified</div>
								</div>
							</div>
						{/if}
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	/* Print styles */
	@media print {
		.bg-gray-950,
		.bg-gray-900,
		.bg-gray-800 {
			background: white !important;
			color: black !important;
		}
		
		.text-white,
		.text-gray-300,
		.text-gray-400 {
			color: black !important;
		}
		
		.border-gray-700,
		.border-gray-800 {
			border-color: #ccc !important;
		}
	}

	/* Content prose styling */
	:global(.prose h1) { @apply text-2xl font-bold text-white mb-4; }
	:global(.prose h2) { @apply text-xl font-semibold text-white mb-3; }
	:global(.prose h3) { @apply text-lg font-medium text-white mb-2; }
	:global(.prose p) { @apply text-gray-300 mb-3 leading-relaxed; }
	:global(.prose ul) { @apply list-disc list-inside text-gray-300 mb-3; }
	:global(.prose ol) { @apply list-decimal list-inside text-gray-300 mb-3; }
	:global(.prose li) { @apply mb-1; }
	:global(.prose a) { @apply text-blue-400 hover:text-blue-300; }
	:global(.prose strong) { @apply font-semibold text-white; }
	:global(.prose em) { @apply italic; }
	:global(.prose blockquote) { @apply border-l-4 border-gray-600 pl-4 italic text-gray-400; }
	:global(.prose code) { @apply bg-gray-800 text-blue-300 px-1 py-0.5 rounded text-sm; }
	:global(.prose pre) { @apply bg-gray-800 text-gray-300 p-4 rounded-lg overflow-x-auto; }
</style>