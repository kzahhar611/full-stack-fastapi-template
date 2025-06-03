<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { 
		Workflow, 
		Plus, 
		Search,
		Play,
		Pause,
		Settings,
		MoreVertical,
		Shield,
		Clock,
		CheckCircle,
		AlertCircle
	} from 'lucide-svelte';

	let loading = true;
	let workflows = [];
	let searchTerm = '';
	let error = null;

	// Check if user has access
	$: hasAccess = authStore.canManageRFPs();

	onMount(async () => {
		if (hasAccess) {
			await loadWorkflows();
		}
	});

	async function loadWorkflows() {
		loading = true;
		error = null;
		
		try {
			// Mock workflows data (in real app, would fetch from API)
			workflows = [
				{
					id: 1,
					name: 'Standard RFP Approval',
					description: 'Standard workflow for RFP review and approval process',
					status: 'active',
					trigger: 'rfp_created',
					steps: 5,
					active_instances: 12,
					completed_instances: 45,
					success_rate: 0.89,
					avg_completion_time: '3.2 days',
					created_at: '2024-01-15T00:00:00Z',
					updated_at: '2024-12-01T00:00:00Z'
				},
				{
					id: 2,
					name: 'Document Review Workflow',
					description: 'Automated document analysis and quality assessment',
					status: 'active',
					trigger: 'document_uploaded',
					steps: 3,
					active_instances: 8,
					completed_instances: 123,
					success_rate: 0.95,
					avg_completion_time: '45 minutes',
					created_at: '2024-02-20T00:00:00Z',
					updated_at: '2024-11-15T00:00:00Z'
				},
				{
					id: 3,
					name: 'Vendor Notification',
					description: 'Notify vendors about RFP opportunities and updates',
					status: 'paused',
					trigger: 'rfp_published',
					steps: 2,
					active_instances: 0,
					completed_instances: 67,
					success_rate: 0.92,
					avg_completion_time: '2 hours',
					created_at: '2024-03-05T00:00:00Z',
					updated_at: '2024-10-30T00:00:00Z'
				},
				{
					id: 4,
					name: 'AI Quality Assessment',
					description: 'Automated AI-powered quality scoring and recommendations',
					status: 'active',
					trigger: 'proposal_submitted',
					steps: 4,
					active_instances: 15,
					completed_instances: 89,
					success_rate: 0.87,
					avg_completion_time: '30 minutes',
					created_at: '2024-04-10T00:00:00Z',
					updated_at: '2024-12-15T00:00:00Z'
				}
			];
		} catch (err) {
			console.error('Failed to load workflows:', err);
			error = err.message || 'Failed to load workflows';
		} finally {
			loading = false;
		}
	}

	function getStatusBadgeClass(status) {
		const statusClasses = {
			active: 'bg-green-600 text-white',
			paused: 'bg-yellow-600 text-white',
			draft: 'bg-gray-600 text-white',
			archived: 'bg-red-600 text-white'
		};
		return statusClasses[status] || 'bg-gray-600 text-white';
	}

	function getStatusIcon(status) {
		switch (status) {
			case 'active': return CheckCircle;
			case 'paused': return Pause;
			case 'draft': return Clock;
			default: return AlertCircle;
		}
	}

	function formatDate(dateString) {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	function formatPercentage(value) {
		return (value * 100).toFixed(1) + '%';
	}

	// Filter workflows based on search term
	$: filteredWorkflows = workflows.filter(workflow => 
		!searchTerm || 
		workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
		workflow.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
		workflow.trigger.toLowerCase().includes(searchTerm.toLowerCase())
	);
</script>

<svelte:head>
	<title>Workflows - TenderWise AI</title>
</svelte:head>

{#if !hasAccess}
	<div class="text-center py-12">
		<Shield size={64} class="mx-auto text-gray-600 mb-4" />
		<h2 class="text-xl font-bold text-white mb-2">Access Restricted</h2>
		<p class="text-gray-400">You need appropriate permissions to manage workflows.</p>
	</div>
{:else}
	<div class="space-y-6">
		<!-- Header -->
		<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-3xl font-bold text-white flex items-center gap-3">
					<Workflow size={32} class="text-blue-400" />
					Workflows
				</h1>
				<p class="text-gray-400 mt-2">Automate your RFP and procurement processes</p>
			</div>
			
			<div class="mt-4 sm:mt-0">
				<button class="btn-primary flex items-center gap-2">
					<Plus size={16} />
					Create Workflow
				</button>
			</div>
		</div>

		{#if loading}
			<div class="flex items-center justify-center py-12">
				<div class="spinner w-8 h-8"></div>
				<span class="text-gray-400 ml-3">Loading workflows...</span>
			</div>
		{:else if error}
			<div class="card bg-red-900/20 border-red-700 text-red-300">
				<div class="flex items-center gap-3">
					<Workflow size={20} />
					<div>
						<h3 class="font-medium">Failed to Load Workflows</h3>
						<p class="text-sm text-red-200 mt-1">{error}</p>
					</div>
					<button 
						on:click={loadWorkflows}
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
						placeholder="Search workflows..."
						bind:value={searchTerm}
						class="input pl-10"
					/>
				</div>
			</div>

			<!-- Workflows Grid -->
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
				{#each filteredWorkflows as workflow}
					<div class="card-hover">
						<div class="flex items-start justify-between mb-4">
							<div class="flex items-center gap-3">
								<div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-600 rounded-lg flex items-center justify-center">
									<Workflow size={24} class="text-white" />
								</div>
								<div class="flex-1">
									<h3 class="text-lg font-semibold text-white">{workflow.name}</h3>
									<p class="text-sm text-gray-400">Trigger: {workflow.trigger}</p>
								</div>
							</div>
							<div class="flex items-center gap-2">
								<span class="badge {getStatusBadgeClass(workflow.status)} flex items-center gap-1">
									<svelte:component this={getStatusIcon(workflow.status)} size={12} />
									{workflow.status.toUpperCase()}
								</span>
								<button class="p-2 text-gray-400 hover:text-white">
									<MoreVertical size={16} />
								</button>
							</div>
						</div>
						
						<p class="text-gray-300 text-sm mb-4">
							{workflow.description}
						</p>
						
						<div class="grid grid-cols-2 gap-4 mb-4 text-sm">
							<div>
								<p class="text-gray-400">Steps</p>
								<p class="text-white font-medium">{workflow.steps}</p>
							</div>
							<div>
								<p class="text-gray-400">Success Rate</p>
								<p class="text-green-400 font-medium">{formatPercentage(workflow.success_rate)}</p>
							</div>
							<div>
								<p class="text-gray-400">Active</p>
								<p class="text-blue-400 font-medium">{workflow.active_instances}</p>
							</div>
							<div>
								<p class="text-gray-400">Completed</p>
								<p class="text-white font-medium">{workflow.completed_instances}</p>
							</div>
						</div>
						
						<div class="mb-4">
							<p class="text-gray-400 text-sm">Average Completion Time</p>
							<p class="text-white font-medium flex items-center gap-1">
								<Clock size={14} />
								{workflow.avg_completion_time}
							</p>
						</div>
						
						<div class="flex items-center justify-between pt-4 border-t border-gray-700">
							<span class="text-xs text-gray-400">
								Updated {formatDate(workflow.updated_at)}
							</span>
							<div class="flex gap-2">
								<button class="text-blue-400 hover:text-blue-300">
									<Play size={14} />
								</button>
								<button class="text-gray-400 hover:text-white">
									<Settings size={14} />
								</button>
							</div>
						</div>
					</div>
				{/each}
			</div>
			
			{#if filteredWorkflows.length === 0}
				<div class="text-center py-12">
					<Workflow size={48} class="mx-auto text-gray-600 mb-4" />
					<p class="text-lg font-medium text-white">No workflows found</p>
					<p class="text-sm mt-2 text-gray-400">
						{searchTerm ? 'Try adjusting your search terms' : 'Create your first workflow to automate processes'}
					</p>
				</div>
			{/if}

			<!-- Workflow Stats -->
			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
				<div class="card-hover">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-400 text-sm">Total Workflows</p>
							<p class="text-2xl font-bold text-white">{workflows.length}</p>
						</div>
						<div class="p-3 bg-purple-600 rounded-lg">
							<Workflow size={24} class="text-white" />
						</div>
					</div>
				</div>
				
				<div class="card-hover">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-400 text-sm">Active</p>
							<p class="text-2xl font-bold text-white">{workflows.filter(w => w.status === 'active').length}</p>
						</div>
						<div class="p-3 bg-green-600 rounded-lg">
							<CheckCircle size={24} class="text-white" />
						</div>
					</div>
				</div>
				
				<div class="card-hover">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-400 text-sm">Running Instances</p>
							<p class="text-2xl font-bold text-white">{workflows.reduce((sum, w) => sum + w.active_instances, 0)}</p>
						</div>
						<div class="p-3 bg-blue-600 rounded-lg">
							<Play size={24} class="text-white" />
						</div>
					</div>
				</div>
				
				<div class="card-hover">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-400 text-sm">Avg Success Rate</p>
							<p class="text-2xl font-bold text-white">{formatPercentage(workflows.reduce((sum, w) => sum + w.success_rate, 0) / workflows.length)}</p>
						</div>
						<div class="p-3 bg-orange-600 rounded-lg">
							<CheckCircle size={24} class="text-white" />
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
{/if}