<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { 
		FileText, 
		Upload, 
		Search,
		Filter,
		Download,
		Eye,
		MoreVertical,
		Shield,
		Clock,
		CheckCircle,
		AlertCircle,
		Brain
	} from 'lucide-svelte';

	let loading = true;
	let documents = [];
	let searchTerm = '';
	let selectedType = 'all';
	let error = null;

	// Check if user has access
	$: hasAccess = $authStore.isAuthenticated;

	onMount(async () => {
		if (hasAccess) {
			await loadDocuments();
		}
	});

	async function loadDocuments() {
		loading = true;
		error = null;
		
		try {
			// Mock documents data (in real app, would fetch from API)
			documents = [
				{
					id: 1,
					name: 'Technical Requirements Specification.pdf',
					type: 'specification',
					size: '2.4 MB',
					uploaded_by: 'John Manager',
					uploaded_at: '2025-01-03T10:30:00Z',
					ai_quality_score: 9.2,
					classification: 'Technical Specification',
					status: 'processed',
					rfp_id: 'RFP-2025-001',
					download_count: 15
				},
				{
					id: 2,
					name: 'Vendor Proposal ABC Corp.docx',
					type: 'proposal',
					size: '1.8 MB',
					uploaded_by: 'Jane User',
					uploaded_at: '2025-01-02T14:20:00Z',
					ai_quality_score: 8.7,
					classification: 'Proposal Document',
					status: 'processed',
					rfp_id: 'RFP-2025-001',
					download_count: 8
				},
				{
					id: 3,
					name: 'Contract Template v2.1.pdf',
					type: 'contract',
					size: '890 KB',
					uploaded_by: 'Admin User',
					uploaded_at: '2025-01-01T09:15:00Z',
					ai_quality_score: 9.5,
					classification: 'Contract Template',
					status: 'processed',
					rfp_id: null,
					download_count: 23
				},
				{
					id: 4,
					name: 'Financial Assessment.xlsx',
					type: 'financial',
					size: '1.2 MB',
					uploaded_by: 'Finance Team',
					uploaded_at: '2024-12-30T16:45:00Z',
					ai_quality_score: 8.1,
					classification: 'Financial Document',
					status: 'processing',
					rfp_id: 'RFP-2025-002',
					download_count: 5
				},
				{
					id: 5,
					name: 'Compliance Checklist.pdf',
					type: 'compliance',
					size: '650 KB',
					uploaded_by: 'Legal Team',
					uploaded_at: '2024-12-28T11:30:00Z',
					ai_quality_score: 9.0,
					classification: 'Compliance Document',
					status: 'processed',
					rfp_id: 'RFP-2025-003',
					download_count: 12
				}
			];
		} catch (err) {
			console.error('Failed to load documents:', err);
			error = err.message || 'Failed to load documents';
		} finally {
			loading = false;
		}
	}

	function getTypeBadgeClass(type) {
		const typeClasses = {
			specification: 'bg-blue-600 text-white',
			proposal: 'bg-green-600 text-white',
			contract: 'bg-purple-600 text-white',
			financial: 'bg-orange-600 text-white',
			compliance: 'bg-red-600 text-white',
			other: 'bg-gray-600 text-white'
		};
		return typeClasses[type] || 'bg-gray-600 text-white';
	}

	function getStatusBadgeClass(status) {
		const statusClasses = {
			processed: 'bg-green-600 text-white',
			processing: 'bg-yellow-600 text-white',
			failed: 'bg-red-600 text-white',
			pending: 'bg-gray-600 text-white'
		};
		return statusClasses[status] || 'bg-gray-600 text-white';
	}

	function getStatusIcon(status) {
		switch (status) {
			case 'processed': return CheckCircle;
			case 'processing': return Clock;
			case 'failed': return AlertCircle;
			default: return Clock;
		}
	}

	function getQualityColor(score) {
		if (score >= 9) return 'text-green-400';
		if (score >= 7) return 'text-yellow-400';
		return 'text-red-400';
	}

	function formatDate(dateString) {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	function formatFileSize(size) {
		return size;
	}

	// Filter documents based on search term and type
	$: filteredDocuments = documents.filter(doc => {
		const matchesSearch = !searchTerm || 
			doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
			doc.classification.toLowerCase().includes(searchTerm.toLowerCase()) ||
			doc.uploaded_by.toLowerCase().includes(searchTerm.toLowerCase());
		
		const matchesType = selectedType === 'all' || doc.type === selectedType;
		
		return matchesSearch && matchesType;
	});
</script>

<svelte:head>
	<title>Documents - TenderWise AI</title>
</svelte:head>

{#if !hasAccess}
	<div class="text-center py-12">
		<Shield size={64} class="mx-auto text-gray-600 mb-4" />
		<h2 class="text-xl font-bold text-white mb-2">Access Restricted</h2>
		<p class="text-gray-400">You need to be logged in to view documents.</p>
		<a href="/login" class="btn-primary mt-4">
			Sign In
		</a>
	</div>
{:else}
	<div class="space-y-6">
		<!-- Header -->
		<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-3xl font-bold text-white flex items-center gap-3">
					<FileText size={32} class="text-blue-400" />
					Document Management
				</h1>
				<p class="text-gray-400 mt-2">AI-powered document processing and analysis</p>
			</div>
			
			<div class="mt-4 sm:mt-0">
				<button class="btn-primary flex items-center gap-2">
					<Upload size={16} />
					Upload Documents
				</button>
			</div>
		</div>

		{#if loading}
			<div class="flex items-center justify-center py-12">
				<div class="spinner w-8 h-8"></div>
				<span class="text-gray-400 ml-3">Loading documents...</span>
			</div>
		{:else if error}
			<div class="card bg-red-900/20 border-red-700 text-red-300">
				<div class="flex items-center gap-3">
					<FileText size={20} />
					<div>
						<h3 class="font-medium">Failed to Load Documents</h3>
						<p class="text-sm text-red-200 mt-1">{error}</p>
					</div>
					<button 
						on:click={loadDocuments}
						class="ml-auto btn-secondary text-sm"
					>
						Retry
					</button>
				</div>
			</div>
		{:else}
			<!-- Filters -->
			<div class="card">
				<div class="flex flex-col sm:flex-row gap-4">
					<!-- Search -->
					<div class="flex-1">
						<div class="relative">
							<Search size={20} class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
							<input
								type="text"
								placeholder="Search documents..."
								bind:value={searchTerm}
								class="input pl-10"
							/>
						</div>
					</div>
					
					<!-- Type Filter -->
					<div class="sm:w-48">
						<select bind:value={selectedType} class="input">
							<option value="all">All Types</option>
							<option value="specification">Specifications</option>
							<option value="proposal">Proposals</option>
							<option value="contract">Contracts</option>
							<option value="financial">Financial</option>
							<option value="compliance">Compliance</option>
						</select>
					</div>
				</div>
			</div>

			<!-- Documents Table -->
			<div class="card">
				<div class="overflow-x-auto">
					<table class="w-full">
						<thead>
							<tr class="border-b border-gray-700">
								<th class="text-left py-3 px-4 text-gray-400 font-medium">Document</th>
								<th class="text-left py-3 px-4 text-gray-400 font-medium">Type</th>
								<th class="text-left py-3 px-4 text-gray-400 font-medium">AI Quality</th>
								<th class="text-left py-3 px-4 text-gray-400 font-medium">Status</th>
								<th class="text-left py-3 px-4 text-gray-400 font-medium">Uploaded</th>
								<th class="text-right py-3 px-4 text-gray-400 font-medium">Actions</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-700">
							{#each filteredDocuments as doc}
								<tr class="hover:bg-gray-800/50">
									<td class="py-4 px-4">
										<div class="flex items-center gap-3">
											<div class="w-8 h-8 rounded bg-blue-600 flex items-center justify-center">
												<FileText size={16} class="text-white" />
											</div>
											<div>
												<div class="text-white font-medium truncate max-w-xs">
													{doc.name}
												</div>
												<div class="text-gray-400 text-sm">
													{doc.size} • {doc.download_count} downloads
												</div>
											</div>
										</div>
									</td>
									<td class="py-4 px-4">
										<span class="badge {getTypeBadgeClass(doc.type)}">
											{doc.classification}
										</span>
									</td>
									<td class="py-4 px-4">
										<div class="flex items-center gap-2">
											<Brain size={16} class="text-blue-400" />
											<span class="font-medium {getQualityColor(doc.ai_quality_score)}">
												{doc.ai_quality_score}/10
											</span>
										</div>
									</td>
									<td class="py-4 px-4">
										<span class="badge {getStatusBadgeClass(doc.status)} flex items-center gap-1 w-fit">
											<svelte:component this={getStatusIcon(doc.status)} size={12} />
											{doc.status.toUpperCase()}
										</span>
									</td>
									<td class="py-4 px-4 text-gray-300">
										<div class="text-sm">
											<div>{formatDate(doc.uploaded_at)}</div>
											<div class="text-gray-400">by {doc.uploaded_by}</div>
										</div>
									</td>
									<td class="py-4 px-4 text-right">
										<div class="flex items-center gap-2 justify-end">
											<button class="p-2 text-gray-400 hover:text-white" title="View">
												<Eye size={16} />
											</button>
											<button class="p-2 text-gray-400 hover:text-white" title="Download">
												<Download size={16} />
											</button>
											<button class="p-2 text-gray-400 hover:text-white" title="More">
												<MoreVertical size={16} />
											</button>
										</div>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
				
				{#if filteredDocuments.length === 0}
					<div class="text-center py-8 text-gray-400">
						<FileText size={48} class="mx-auto mb-4 opacity-50" />
						<p class="text-lg font-medium">No documents found</p>
						<p class="text-sm mt-2">
							{searchTerm || selectedType !== 'all' ? 'Try adjusting your filters' : 'Upload your first document to get started'}
						</p>
					</div>
				{/if}
			</div>

			<!-- Document Stats -->
			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
				<div class="card-hover">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-400 text-sm">Total Documents</p>
							<p class="text-2xl font-bold text-white">{documents.length}</p>
						</div>
						<div class="p-3 bg-blue-600 rounded-lg">
							<FileText size={24} class="text-white" />
						</div>
					</div>
				</div>
				
				<div class="card-hover">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-400 text-sm">AI Processed</p>
							<p class="text-2xl font-bold text-white">{documents.filter(d => d.status === 'processed').length}</p>
						</div>
						<div class="p-3 bg-green-600 rounded-lg">
							<Brain size={24} class="text-white" />
						</div>
					</div>
				</div>
				
				<div class="card-hover">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-400 text-sm">Avg Quality</p>
							<p class="text-2xl font-bold text-white">
								{(documents.reduce((sum, doc) => sum + doc.ai_quality_score, 0) / documents.length).toFixed(1)}
							</p>
						</div>
						<div class="p-3 bg-purple-600 rounded-lg">
							<CheckCircle size={24} class="text-white" />
						</div>
					</div>
				</div>
				
				<div class="card-hover">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-400 text-sm">Total Downloads</p>
							<p class="text-2xl font-bold text-white">{documents.reduce((sum, doc) => sum + doc.download_count, 0)}</p>
						</div>
						<div class="p-3 bg-orange-600 rounded-lg">
							<Download size={24} class="text-white" />
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
{/if}