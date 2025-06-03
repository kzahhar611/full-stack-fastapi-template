<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { apiClient } from '$lib/api/client';
	import { 
		FileText, 
		Building2, 
		Users, 
		TrendingUp,
		Clock,
		CheckCircle,
		AlertCircle,
		Plus,
		Activity
	} from 'lucide-svelte';
	
	let loading = true;
	let error = null;
	let stats = {
		total_rfps: 0,
		draft_rfps: 0,
		published_rfps: 0,
		closed_rfps: 0,
		average_budget: 0,
		upcoming_deadlines: 0
	};
	let recentRFPs = [];
	let organizations = [];
	
	onMount(async () => {
		await loadDashboardData();
	});
	
	async function loadDashboardData() {
		loading = true;
		error = null;
		
		try {
			console.log('Loading dashboard data...');
			
			// Load RFP statistics
			const statsResponse = await apiClient.getRFPStats();
			console.log('Stats response:', statsResponse);
			
			if (statsResponse.success && statsResponse.data) {
				stats = statsResponse.data;
			} else {
				throw new Error(statsResponse.message || 'Failed to load stats');
			}
			
			// Load recent RFPs
			const rfpsResponse = await apiClient.getRFPs({ size: 5 });
			console.log('RFPs response:', rfpsResponse);
			
			if (rfpsResponse.success && rfpsResponse.data) {
				recentRFPs = Array.isArray(rfpsResponse.data) ? rfpsResponse.data : [];
			}
			
			// Load organizations (if admin)
			if (authStore.isAdmin()) {
				const orgsResponse = await apiClient.getOrganizations();
				console.log('Organizations response:', orgsResponse);
				
				if (orgsResponse.success && orgsResponse.data) {
					organizations = Array.isArray(orgsResponse.data) ? orgsResponse.data : [];
				}
			}
			
			console.log('Dashboard data loaded successfully');
		} catch (err) {
			console.error('Failed to load dashboard data:', err);
			error = err.message || 'Failed to load dashboard data';
		} finally {
			loading = false;
		}
	}
	
	function formatCurrency(amount) {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'SAR',
			minimumFractionDigits: 0,
			maximumFractionDigits: 0
		}).format(amount);
	}
	
	function formatDate(dateString) {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}
	
	function getStatusBadgeClass(status) {
		const statusClasses = {
			draft: 'badge-draft',
			published: 'badge-published',
			open: 'badge-open',
			closed: 'badge-closed',
			awarded: 'badge-awarded'
		};
		return statusClasses[status?.toLowerCase()] || 'badge-draft';
	}
</script>

<svelte:head>
	<title>Dashboard - TenderWise AI</title>
</svelte:head>

<div class="space-y-6">
	<!-- Welcome Header -->
	<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
		<div>
			<h1 class="text-3xl font-bold text-white flex items-center gap-3">
				<Activity size={32} class="text-blue-400" />
				Dashboard
			</h1>
			<p class="text-gray-400 mt-2">
				Welcome back, {$authStore.user?.first_name || 'User'}! Here's your TenderWise overview.
			</p>
		</div>
		
		{#if authStore.canManageRFPs()}
			<div class="mt-4 sm:mt-0">
				<a href="/rfps/create" class="btn-primary flex items-center gap-2">
					<Plus size={16} />
					Create RFP
				</a>
			</div>
		{/if}
	</div>
	
	{#if loading}
		<div class="flex items-center justify-center py-12">
			<div class="spinner w-8 h-8"></div>
			<span class="text-gray-400 ml-3">Loading dashboard...</span>
		</div>
	{:else if error}
		<div class="card bg-red-900/20 border-red-700 text-red-300">
			<div class="flex items-center gap-3">
				<AlertCircle size={20} />
				<div>
					<h3 class="font-medium">Dashboard Error</h3>
					<p class="text-sm text-red-200 mt-1">{error}</p>
				</div>
				<button 
					on:click={loadDashboardData}
					class="ml-auto btn-secondary text-sm"
				>
					Retry
				</button>
			</div>
		</div>
	{:else}
		<!-- System Status -->
		<div class="card bg-green-900/20 border-green-700">
			<div class="flex items-center gap-3">
				<div class="w-3 h-3 rounded-full bg-green-400"></div>
				<div>
					<h3 class="text-green-300 font-medium">System Status</h3>
					<p class="text-green-200 text-sm">All systems operational • Backend & AI services running</p>
				</div>
				<div class="ml-auto text-xs text-green-300">
					Last updated: {new Date().toLocaleTimeString()}
				</div>
			</div>
		</div>

		<!-- Stats Cards -->
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
			<!-- Total RFPs -->
			<div class="card-hover">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-gray-400 text-sm">Total RFPs</p>
						<p class="text-2xl font-bold text-white">{stats.total_rfps}</p>
						<p class="text-xs text-blue-400 mt-1">All time</p>
					</div>
					<div class="p-3 bg-blue-600 rounded-lg">
						<FileText size={24} class="text-white" />
					</div>
				</div>
			</div>
			
			<!-- Active RFPs -->
			<div class="card-hover">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-gray-400 text-sm">Published RFPs</p>
						<p class="text-2xl font-bold text-white">{stats.published_rfps}</p>
						<p class="text-xs text-green-400 mt-1">Currently active</p>
					</div>
					<div class="p-3 bg-green-600 rounded-lg">
						<CheckCircle size={24} class="text-white" />
					</div>
				</div>
			</div>
			
			<!-- Draft RFPs -->
			<div class="card-hover">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-gray-400 text-sm">Draft RFPs</p>
						<p class="text-2xl font-bold text-white">{stats.draft_rfps}</p>
						<p class="text-xs text-yellow-400 mt-1">In preparation</p>
					</div>
					<div class="p-3 bg-yellow-600 rounded-lg">
						<Clock size={24} class="text-white" />
					</div>
				</div>
			</div>
			
			<!-- Average Budget -->
			<div class="card-hover">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-gray-400 text-sm">Avg. Budget</p>
						<p class="text-2xl font-bold text-white">
							{stats.average_budget ? formatCurrency(stats.average_budget) : 'N/A'}
						</p>
						<p class="text-xs text-purple-400 mt-1">Per RFP</p>
					</div>
					<div class="p-3 bg-purple-600 rounded-lg">
						<TrendingUp size={24} class="text-white" />
					</div>
				</div>
			</div>
		</div>
		
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
			<!-- Recent RFPs -->
			<div class="card">
				<div class="flex items-center justify-between mb-4">
					<h2 class="text-lg font-semibold text-white">Recent RFPs</h2>
					<a href="/rfps" class="text-blue-400 hover:text-blue-300 text-sm">
						View all
					</a>
				</div>
				
				{#if recentRFPs.length > 0}
					<div class="space-y-3">
						{#each recentRFPs as rfp}
							<div class="flex items-center justify-between p-3 bg-gray-700 rounded-md hover:bg-gray-600 transition-colors">
								<div class="flex-1 min-w-0">
									<a href="/rfps/{rfp.id}" class="text-white font-medium hover:text-blue-300 truncate block">
										{rfp.title}
									</a>
									<p class="text-gray-400 text-sm">
										{rfp.rfp_number} • {formatDate(rfp.created_at)}
									</p>
								</div>
								<div class="flex items-center gap-2 ml-4">
									<span class="badge {getStatusBadgeClass(rfp.status)}">
										{rfp.status}
									</span>
								</div>
							</div>
						{/each}
					</div>
				{:else}
					<div class="text-center py-8 text-gray-400">
						<FileText size={48} class="mx-auto mb-4 opacity-50" />
						<p class="text-lg font-medium">No RFPs yet</p>
						<p class="text-sm mt-2">Create your first RFP to get started</p>
						{#if authStore.canManageRFPs()}
							<a href="/rfps/create" class="btn-primary mt-4 inline-flex items-center gap-2">
								<Plus size={16} />
								Create RFP
							</a>
						{/if}
					</div>
				{/if}
			</div>
			
			<!-- Quick Actions -->
			<div class="card">
				<h2 class="text-lg font-semibold text-white mb-4">Quick Actions</h2>
				<div class="space-y-3">
					<a href="/rfps" class="flex items-center gap-3 p-3 bg-gray-700 rounded-md hover:bg-gray-600 transition-colors">
						<FileText size={20} class="text-blue-400" />
						<div>
							<div class="text-white font-medium">Browse RFPs</div>
							<div class="text-gray-400 text-sm">View all available RFPs</div>
						</div>
					</a>
					
					{#if authStore.canManageRFPs()}
						<a href="/rfps/create" class="flex items-center gap-3 p-3 bg-gray-700 rounded-md hover:bg-gray-600 transition-colors">
							<Plus size={20} class="text-green-400" />
							<div>
								<div class="text-white font-medium">Create RFP</div>
								<div class="text-gray-400 text-sm">Start a new RFP process</div>
							</div>
						</a>
					{/if}
					
					<a href="/analytics" class="flex items-center gap-3 p-3 bg-gray-700 rounded-md hover:bg-gray-600 transition-colors">
						<TrendingUp size={20} class="text-purple-400" />
						<div>
							<div class="text-white font-medium">Analytics</div>
							<div class="text-gray-400 text-sm">View performance insights</div>
						</div>
					</a>
					
					{#if authStore.isAdmin()}
						<a href="/organizations" class="flex items-center gap-3 p-3 bg-gray-700 rounded-md hover:bg-gray-600 transition-colors">
							<Building2 size={20} class="text-orange-400" />
							<div>
								<div class="text-white font-medium">Organizations</div>
								<div class="text-gray-400 text-sm">Manage organizations</div>
							</div>
						</a>
					{/if}
				</div>
			</div>
		</div>
		
		<!-- Upcoming Deadlines Alert -->
		{#if stats.upcoming_deadlines > 0}
			<div class="bg-yellow-900/20 border border-yellow-700 rounded-lg p-4">
				<div class="flex items-center gap-3">
					<AlertCircle size={20} class="text-yellow-400" />
					<div>
						<h3 class="text-yellow-400 font-medium">Upcoming Deadlines</h3>
						<p class="text-yellow-200 text-sm">
							You have {stats.upcoming_deadlines} RFP{stats.upcoming_deadlines > 1 ? 's' : ''} with deadlines approaching.
						</p>
					</div>
					<a href="/rfps?filter=upcoming" class="ml-auto btn-secondary text-sm">
						View RFPs
					</a>
				</div>
			</div>
		{/if}
	{/if}
</div>