<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { apiClient } from '$lib/api/client';
	import { 
		Building2, 
		Plus, 
		Search,
		Users,
		Settings,
		MoreVertical,
		Shield
	} from 'lucide-svelte';

	let loading = true;
	let organizations = [];
	let searchTerm = '';
	let error = null;

	// Check if user has access
	$: hasAccess = authStore.isAdmin();

	onMount(async () => {
		if (hasAccess) {
			await loadOrganizations();
		}
	});

	async function loadOrganizations() {
		loading = true;
		error = null;
		
		try {
			// Mock organizations data (in real app, would fetch from API)
			organizations = [
				{
					id: 1,
					name: 'TenderWise',
					slug: 'tenderwise',
					organization_type: 'Enterprise',
					description: 'Primary organization for TenderWise AI platform',
					user_count: 15,
					rfp_count: 25,
					status: 'active',
					created_at: '2024-01-01T00:00:00Z',
					contact_email: 'admin@tenderwise.ai'
				},
				{
					id: 2,
					name: 'ABC Corporation',
					slug: 'abc-corp',
					organization_type: 'Corporate',
					description: 'Large corporation using TenderWise for procurement',
					user_count: 45,
					rfp_count: 120,
					status: 'active',
					created_at: '2024-02-15T00:00:00Z',
					contact_email: 'procurement@abc-corp.com'
				},
				{
					id: 3,
					name: 'Government Agency',
					slug: 'gov-agency',
					organization_type: 'Government',
					description: 'Government procurement department',
					user_count: 30,
					rfp_count: 85,
					status: 'active',
					created_at: '2024-03-10T00:00:00Z',
					contact_email: 'tender@gov-agency.org'
				}
			];
		} catch (err) {
			console.error('Failed to load organizations:', err);
			error = err.message || 'Failed to load organizations';
		} finally {
			loading = false;
		}
	}

	function getStatusBadgeClass(status) {
		return status === 'active' ? 'bg-green-600 text-white' : 'bg-red-600 text-white';
	}

	function getTypeBadgeClass(type) {
		const typeClasses = {
			Enterprise: 'bg-blue-600 text-white',
			Corporate: 'bg-purple-600 text-white',
			Government: 'bg-orange-600 text-white',
			Nonprofit: 'bg-green-600 text-white'
		};
		return typeClasses[type] || 'bg-gray-600 text-white';
	}

	function formatDate(dateString) {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	// Filter organizations based on search term
	$: filteredOrganizations = organizations.filter(org => 
		!searchTerm || 
		org.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
		org.organization_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
		org.description.toLowerCase().includes(searchTerm.toLowerCase())
	);
</script>

<svelte:head>
	<title>Organizations - TenderWise AI</title>
</svelte:head>

{#if !hasAccess}
	<div class="text-center py-12">
		<Shield size={64} class="mx-auto text-gray-600 mb-4" />
		<h2 class="text-xl font-bold text-white mb-2">Access Restricted</h2>
		<p class="text-gray-400">You need administrator privileges to manage organizations.</p>
	</div>
{:else}
	<div class="space-y-6">
		<!-- Header -->
		<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-3xl font-bold text-white flex items-center gap-3">
					<Building2 size={32} class="text-blue-400" />
					Organizations
				</h1>
				<p class="text-gray-400 mt-2">Manage organizations and their settings</p>
			</div>
			
			<div class="mt-4 sm:mt-0">
				<button class="btn-primary flex items-center gap-2">
					<Plus size={16} />
					Add Organization
				</button>
			</div>
		</div>

		{#if loading}
			<div class="flex items-center justify-center py-12">
				<div class="spinner w-8 h-8"></div>
				<span class="text-gray-400 ml-3">Loading organizations...</span>
			</div>
		{:else if error}
			<div class="card bg-red-900/20 border-red-700 text-red-300">
				<div class="flex items-center gap-3">
					<Building2 size={20} />
					<div>
						<h3 class="font-medium">Failed to Load Organizations</h3>
						<p class="text-sm text-red-200 mt-1">{error}</p>
					</div>
					<button 
						on:click={loadOrganizations}
						class="ml-auto btn-secondary text-sm"
					>
						Retry
					</button>
				</div>
			</div>
		{:else}
			<!-- Search -->
			<div class="card">
				<div class="relative">
					<Search size={20} class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
					<input
						type="text"
						placeholder="Search organizations..."
						bind:value={searchTerm}
						class="input pl-10"
					/>
				</div>
			</div>

			<!-- Organizations Grid -->
			<div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
				{#each filteredOrganizations as org}
					<div class="card-hover">
						<div class="flex items-start justify-between mb-4">
							<div class="flex items-center gap-3">
								<div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
									<Building2 size={24} class="text-white" />
								</div>
								<div>
									<h3 class="text-lg font-semibold text-white">{org.name}</h3>
									<p class="text-sm text-gray-400">{org.slug}</p>
								</div>
							</div>
							<button class="p-2 text-gray-400 hover:text-white">
								<MoreVertical size={16} />
							</button>
						</div>
						
						<p class="text-gray-300 text-sm mb-4 line-clamp-2">
							{org.description}
						</p>
						
						<div class="flex flex-wrap items-center gap-2 mb-4">
							<span class="badge {getTypeBadgeClass(org.organization_type)}">
								{org.organization_type}
							</span>
							<span class="badge {getStatusBadgeClass(org.status)}">
								{org.status.toUpperCase()}
							</span>
						</div>
						
						<div class="grid grid-cols-2 gap-4 text-sm">
							<div>
								<p class="text-gray-400">Users</p>
								<p class="text-white font-medium flex items-center gap-1">
									<Users size={14} />
									{org.user_count}
								</p>
							</div>
							<div>
								<p class="text-gray-400">RFPs</p>
								<p class="text-white font-medium">{org.rfp_count}</p>
							</div>
						</div>
						
						<div class="mt-4 pt-4 border-t border-gray-700">
							<div class="flex items-center justify-between text-xs text-gray-400">
								<span>Created {formatDate(org.created_at)}</span>
								<div class="flex gap-2">
									<button class="text-blue-400 hover:text-blue-300">
										<Settings size={14} />
									</button>
								</div>
							</div>
						</div>
					</div>
				{/each}
			</div>
			
			{#if filteredOrganizations.length === 0}
				<div class="text-center py-12">
					<Building2 size={48} class="mx-auto text-gray-600 mb-4" />
					<p class="text-lg font-medium text-white">No organizations found</p>
					<p class="text-sm mt-2 text-gray-400">
						{searchTerm ? 'Try adjusting your search terms' : 'Create your first organization to get started'}
					</p>
				</div>
			{/if}

			<!-- Organization Stats -->
			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
				<div class="card-hover">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-400 text-sm">Total Organizations</p>
							<p class="text-2xl font-bold text-white">{organizations.length}</p>
						</div>
						<div class="p-3 bg-blue-600 rounded-lg">
							<Building2 size={24} class="text-white" />
						</div>
					</div>
				</div>
				
				<div class="card-hover">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-400 text-sm">Active Orgs</p>
							<p class="text-2xl font-bold text-white">{organizations.filter(o => o.status === 'active').length}</p>
						</div>
						<div class="p-3 bg-green-600 rounded-lg">
							<Shield size={24} class="text-white" />
						</div>
					</div>
				</div>
				
				<div class="card-hover">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-400 text-sm">Total Users</p>
							<p class="text-2xl font-bold text-white">{organizations.reduce((sum, org) => sum + org.user_count, 0)}</p>
						</div>
						<div class="p-3 bg-purple-600 rounded-lg">
							<Users size={24} class="text-white" />
						</div>
					</div>
				</div>
				
				<div class="card-hover">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-400 text-sm">Total RFPs</p>
							<p class="text-2xl font-bold text-white">{organizations.reduce((sum, org) => sum + org.rfp_count, 0)}</p>
						</div>
						<div class="p-3 bg-orange-600 rounded-lg">
							<Building2 size={24} class="text-white" />
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
{/if}