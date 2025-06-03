<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { apiClient } from '$lib/api/client';
	import RFPCreationWizard from '$lib/components/RFPCreationWizard.svelte';
	import { 
		Plus, 
		Search, 
		Filter, 
		Calendar,
		DollarSign,
		Eye,
		Edit,
		Trash2,
		ExternalLink,
		FileText,
		Clock,
		Users,
		TrendingUp
	} from 'lucide-svelte';
	
	let loading = true;
	let rfps: any[] = [];
	let enhancedRFPs: any[] = [];
	let templates: any[] = [];
	let filteredRFPs: any[] = [];
	let searchQuery = '';
	let statusFilter = 'all';
	let typeFilter = 'all';
	let showWizard = false;
	let statistics: any = null;
	
	const statusOptions = [
		{ value: 'all', label: 'All Status' },
		{ value: 'draft', label: 'Draft' },
		{ value: 'published', label: 'Published' },
		{ value: 'open', label: 'Open' },
		{ value: 'closed', label: 'Closed' },
		{ value: 'awarded', label: 'Awarded' }
	];
	
	const typeOptions = [
		{ value: 'all', label: 'All Types' },
		{ value: 'goods', label: 'Goods' },
		{ value: 'services', label: 'Services' },
		{ value: 'construction', label: 'Construction' },
		{ value: 'consulting', label: 'Consulting' },
		{ value: 'technology', label: 'Technology' },
		{ value: 'other', label: 'Other' }
	];
	
	onMount(async () => {
		await loadData();
	});
	
	async function loadData() {
		loading = true;
		
		try {
			// Load both original and enhanced RFPs
			const [rfpResponse, enhancedResponse, templatesResponse, statsResponse] = await Promise.allSettled([
				apiClient.getRFPs(),
				fetch('/api/v1/rfps-enhanced/', {
					headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
				}).then(r => r.json()),
				fetch('/api/v1/rfp-templates/', {
					headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
				}).then(r => r.json()),
				fetch('/api/v1/rfps-enhanced/statistics/overview', {
					headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
				}).then(r => r.json())
			]);
			
			// Handle original RFPs
			if (rfpResponse.status === 'fulfilled' && rfpResponse.value.success) {
				rfps = Array.isArray(rfpResponse.value.data) ? rfpResponse.value.data : [];
			}
			
			// Handle enhanced RFPs
			if (enhancedResponse.status === 'fulfilled' && Array.isArray(enhancedResponse.value)) {
				enhancedRFPs = enhancedResponse.value;
			}
			
			// Handle templates
			if (templatesResponse.status === 'fulfilled' && Array.isArray(templatesResponse.value)) {
				templates = templatesResponse.value;
			}
			
			// Handle statistics
			if (statsResponse.status === 'fulfilled') {
				statistics = statsResponse.value;
			}
			
			// Use enhanced RFPs if available, otherwise fall back to original
			const allRFPs = enhancedRFPs.length > 0 ? enhancedRFPs : rfps;
			rfps = allRFPs;
			filterRFPs();
			
		} catch (error) {
			console.error('Failed to load data:', error);
		} finally {
			loading = false;
		}
	}
	
	function filterRFPs() {
		filteredRFPs = rfps.filter(rfp => {
			const matchesSearch = !searchQuery || 
				rfp.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
				rfp.rfp_number.toLowerCase().includes(searchQuery.toLowerCase());
			
			const matchesStatus = statusFilter === 'all' || rfp.status === statusFilter;
			const matchesType = typeFilter === 'all' || rfp.rfp_type === typeFilter;
			
			return matchesSearch && matchesStatus && matchesType;
		});
	}
	
	// React to filter changes
	$: searchQuery, statusFilter, typeFilter, filterRFPs();
	
	function formatCurrency(amount: number): string {
		if (!amount) return 'N/A';
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'SAR',
			minimumFractionDigits: 0,
			maximumFractionDigits: 0
		}).format(amount);
	}
	
	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}
	
	function getStatusBadgeClass(status: string): string {
		const statusClasses = {
			draft: 'badge-draft',
			published: 'badge-published',
			open: 'badge-open',
			closed: 'badge-closed',
			awarded: 'badge-awarded'
		};
		return statusClasses[status.toLowerCase()] || 'badge-draft';
	}
	
	function getDaysUntilDeadline(rfp: any): number {
		if (rfp.days_until_deadline !== undefined) {
			return rfp.days_until_deadline;
		}
		
		if (rfp.submission_deadline) {
			const deadline = new Date(rfp.submission_deadline);
			const today = new Date();
			const diffTime = deadline.getTime() - today.getTime();
			return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
		}
		
		return 0;
	}
	
	function getDeadlineColor(days: number): string {
		if (days < 0) return 'text-red-600 dark:text-red-400';
		if (days <= 7) return 'text-orange-600 dark:text-orange-400';
		if (days <= 14) return 'text-yellow-600 dark:text-yellow-400';
		return 'text-green-600 dark:text-green-400';
	}
	
	function openWizard() {
		showWizard = true;
	}
	
	function handleRFPCreated(event: CustomEvent) {
		const newRFP = event.detail;
		rfps = [newRFP, ...rfps];
		filterRFPs();
		loadData(); // Refresh data to get updated statistics
	}
	
	function getDaysUntilDeadline(deadline: string): number {
		const deadlineDate = new Date(deadline);
		const today = new Date();
		const diffTime = deadlineDate.getTime() - today.getTime();
		return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
	}
	
	async function deleteRFP(rfpId: number) {
		if (!confirm('Are you sure you want to delete this RFP?')) return;
		
		try {
			const response = await apiClient.deleteRFP(rfpId);
			if (response.success) {
				await loadRFPs();
			} else {
				alert('Failed to delete RFP: ' + response.message);
			}
		} catch (error) {
			console.error('Failed to delete RFP:', error);
			alert('Failed to delete RFP');
		}
	}
</script>

<svelte:head>
	<title>RFPs - TenderWise AI</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
		<div>
			<h1 class="text-2xl font-bold text-white">RFPs</h1>
			<p class="text-gray-400 mt-1">Manage and track all your RFPs</p>
		</div>
		
		{#if $authStore.canManageRFPs()}
			<div class="mt-4 sm:mt-0 flex gap-3">
				<a href="/rfps/create" class="btn-secondary flex items-center gap-2">
					<Edit size={16} />
					Quick Create
				</a>
				<button 
					class="btn-primary flex items-center gap-2"
					on:click={openWizard}>
					<Plus size={16} />
					Create with Wizard
				</button>
			</div>
		{/if}
	</div>

	<!-- Statistics Cards -->
	{#if statistics}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
			<div class="card p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-400">Total RFPs</p>
						<p class="text-2xl font-bold text-white">{statistics.total_rfps}</p>
					</div>
					<FileText class="w-8 h-8 text-blue-400" />
				</div>
			</div>
			
			<div class="card p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-400">Open RFPs</p>
						<p class="text-2xl font-bold text-white">{statistics.rfps_by_status?.open || 0}</p>
					</div>
					<Clock class="w-8 h-8 text-green-400" />
				</div>
			</div>
			
			<div class="card p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-400">Upcoming Deadlines</p>
						<p class="text-2xl font-bold text-white">{statistics.upcoming_deadlines || 0}</p>
					</div>
					<Calendar class="w-8 h-8 text-orange-400" />
				</div>
			</div>
			
			<div class="card p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-400">Total Budget</p>
						<p class="text-lg font-bold text-white">{formatCurrency(statistics.total_budget || 0)}</p>
					</div>
					<TrendingUp class="w-8 h-8 text-purple-400" />
				</div>
			</div>
		</div>
	{/if}
	
	<!-- Filters -->
	<div class="card">
		<div class="flex flex-col lg:flex-row gap-4">
			<!-- Search -->
			<div class="flex-1">
				<div class="relative">
					<Search size={16} class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
					<input
						type="text"
						bind:value={searchQuery}
						placeholder="Search RFPs by title or number..."
						class="input pl-10"
					/>
				</div>
			</div>
			
			<!-- Status Filter -->
			<div class="w-full lg:w-48">
				<select bind:value={statusFilter} class="input">
					{#each statusOptions as option}
						<option value={option.value}>{option.label}</option>
					{/each}
				</select>
			</div>
			
			<!-- Type Filter -->
			<div class="w-full lg:w-48">
				<select bind:value={typeFilter} class="input">
					{#each typeOptions as option}
						<option value={option.value}>{option.label}</option>
					{/each}
				</select>
			</div>
		</div>
	</div>
	
	{#if loading}
		<div class="flex items-center justify-center py-12">
			<div class="spinner w-8 h-8"></div>
		</div>
	{:else if filteredRFPs.length === 0}
		<div class="card text-center py-12">
			<div class="text-gray-400">
				{#if rfps.length === 0}
					<Plus size={48} class="mx-auto mb-4 opacity-50" />
					<h3 class="text-lg font-medium mb-2">No RFPs yet</h3>
					<p class="mb-4">Get started by creating your first RFP</p>
					{#if $authStore.canManageRFPs()}
						<a href="/rfps/create" class="btn-primary">Create RFP</a>
					{/if}
				{:else}
					<Search size={48} class="mx-auto mb-4 opacity-50" />
					<h3 class="text-lg font-medium mb-2">No matching RFPs</h3>
					<p>Try adjusting your search or filters</p>
				{/if}
			</div>
		</div>
	{:else}
		<!-- Enhanced RFP Cards -->
		<div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
			{#each filteredRFPs as rfp}
				<div class="card-hover">
					<!-- RFP Header -->
					<div class="flex items-start justify-between mb-4">
						<div class="flex-1 min-w-0">
							<h3 class="font-semibold text-white truncate mb-1">
								<a href="/rfps/{rfp.id}" class="hover:text-blue-300 transition-colors">
									{rfp.title}
								</a>
							</h3>
							<div class="flex items-center gap-2 text-sm text-gray-400">
								<span>{rfp.rfp_number}</span>
								{#if rfp.category}
									<span class="text-blue-400">• {rfp.category}</span>
								{/if}
							</div>
						</div>
						<span class="badge {getStatusBadgeClass(rfp.status)} ml-3">
							{rfp.status}
						</span>
					</div>
					
					<!-- RFP Details -->
					<div class="space-y-3 mb-4">
						<div class="flex items-center gap-2 text-sm text-gray-400">
							<Calendar size={14} />
							<span>Deadline:</span>
							<span class="{getDeadlineColor(getDaysUntilDeadline(rfp))} font-medium">
								{formatDate(rfp.submission_deadline)}
								({getDaysUntilDeadline(rfp)} days)
							</span>
						</div>
						
						{#if rfp.estimated_budget}
							<div class="flex items-center gap-2 text-sm text-gray-400">
								<DollarSign size={14} />
								<span>Budget: {formatCurrency(rfp.estimated_budget)}</span>
								{#if rfp.budget_range_min && rfp.budget_range_max}
									<span class="text-xs">({formatCurrency(rfp.budget_range_min)} - {formatCurrency(rfp.budget_range_max)})</span>
								{/if}
							</div>
						{/if}
						
						<div class="flex items-center justify-between text-sm text-gray-400">
							<div class="flex items-center gap-2">
								<Filter size={14} />
								<span>Type: {rfp.rfp_type}</span>
							</div>
							{#if rfp.document_count !== undefined}
								<div class="flex items-center gap-1">
									<FileText size={12} />
									<span class="text-xs">{rfp.document_count}</span>
								</div>
							{/if}
						</div>
						
						{#if rfp.view_count !== undefined}
							<div class="flex items-center gap-2 text-xs text-gray-500">
								<Eye size={12} />
								<span>{rfp.view_count} views</span>
								{#if rfp.is_template_based}
									<span class="text-blue-400">• Template-based</span>
								{/if}
							</div>
						{/if}
					</div>
					
					<!-- Actions -->
					<div class="flex items-center gap-2 pt-4 border-t border-gray-700">
						<a
							href="/rfps/{rfp.id}"
							class="btn-ghost flex items-center gap-1 text-xs px-2 py-1"
						>
							<Eye size={12} />
							View
						</a>
						
						{#if $authStore.canManageRFPs()}
							<a
								href="/rfps/{rfp.id}/edit"
								class="btn-ghost flex items-center gap-1 text-xs px-2 py-1"
							>
								<Edit size={12} />
								Edit
							</a>
							
							<button
								on:click={() => deleteRFP(rfp.id)}
								class="btn-ghost text-red-400 hover:text-red-300 hover:bg-red-900/20 flex items-center gap-1 text-xs px-2 py-1"
							>
								<Trash2 size={12} />
								Delete
							</button>
						{/if}
						
						{#if rfp.is_public}
							<div class="ml-auto">
								<ExternalLink size={12} class="text-blue-400" title="Public RFP" />
							</div>
						{/if}
					</div>
				</div>
			{/each}
		</div>
		
		<!-- Results Summary -->
		<div class="text-center text-sm text-gray-400">
			Showing {filteredRFPs.length} of {rfps.length} RFPs
		</div>
	{/if}
</div>

<!-- RFP Creation Wizard -->
<RFPCreationWizard 
	bind:isOpen={showWizard} 
	{templates}
	on:created={handleRFPCreated} />