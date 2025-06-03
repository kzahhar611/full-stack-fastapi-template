<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import AnalyticsDashboard from '$lib/components/dashboard/AnalyticsDashboard.svelte';
	import { BarChart3, TrendingUp, Brain, FileText } from 'lucide-svelte';

	// Check if user has access to analytics
	$: hasAccess = $authStore.isAuthenticated();

	onMount(() => {
		// Analytics page loaded
	});
</script>

<svelte:head>
	<title>Analytics - TenderWise AI</title>
	<meta name="description" content="Comprehensive analytics and insights for TenderWise AI platform" />
</svelte:head>

{#if hasAccess}
	<div class="space-y-6">
		<!-- Page Header -->
		<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-3xl font-bold text-white flex items-center gap-3">
					<BarChart3 size={32} class="text-blue-400" />
					Analytics & Insights
				</h1>
				<p class="text-gray-400 mt-2">
					Comprehensive analytics and performance insights for your TenderWise AI platform
				</p>
			</div>
		</div>

		<!-- Analytics Dashboard Component -->
		<AnalyticsDashboard />
		
		<!-- Additional Analytics Sections -->
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- AI Performance Insights -->
			<div class="card">
				<div class="flex items-center gap-3 mb-4">
					<Brain size={20} class="text-blue-400" />
					<h3 class="text-lg font-semibold text-white">AI Performance</h3>
				</div>
				<div class="space-y-3">
					<div class="flex justify-between items-center">
						<span class="text-gray-400">Response Quality</span>
						<span class="text-green-400 font-medium">Excellent</span>
					</div>
					<div class="flex justify-between items-center">
						<span class="text-gray-400">Cost Efficiency</span>
						<span class="text-blue-400 font-medium">Optimized</span>
					</div>
					<div class="flex justify-between items-center">
						<span class="text-gray-400">Provider Reliability</span>
						<span class="text-green-400 font-medium">99.8%</span>
					</div>
				</div>
			</div>

			<!-- Document Processing -->
			<div class="card">
				<div class="flex items-center gap-3 mb-4">
					<FileText size={20} class="text-purple-400" />
					<h3 class="text-lg font-semibold text-white">Document Processing</h3>
				</div>
				<div class="space-y-3">
					<div class="flex justify-between items-center">
						<span class="text-gray-400">Processing Speed</span>
						<span class="text-green-400 font-medium">Fast</span>
					</div>
					<div class="flex justify-between items-center">
						<span class="text-gray-400">Quality Score</span>
						<span class="text-blue-400 font-medium">8.7/10</span>
					</div>
					<div class="flex justify-between items-center">
						<span class="text-gray-400">Success Rate</span>
						<span class="text-green-400 font-medium">96.4%</span>
					</div>
				</div>
			</div>

			<!-- Optimization Recommendations -->
			<div class="card">
				<div class="flex items-center gap-3 mb-4">
					<TrendingUp size={20} class="text-yellow-400" />
					<h3 class="text-lg font-semibold text-white">Recommendations</h3>
				</div>
				<div class="space-y-3 text-sm">
					<div class="p-3 bg-blue-900/20 rounded-md border border-blue-700">
						<p class="text-blue-300 font-medium">Performance Tip</p>
						<p class="text-blue-200 mt-1">Consider enabling AI response caching for frequently asked questions</p>
					</div>
					<div class="p-3 bg-green-900/20 rounded-md border border-green-700">
						<p class="text-green-300 font-medium">Cost Optimization</p>
						<p class="text-green-200 mt-1">Current AI usage is well within budget targets</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Export Options -->
		<div class="card">
			<div class="flex items-center justify-between">
				<div>
					<h3 class="text-lg font-semibold text-white">Export Analytics</h3>
					<p class="text-gray-400 text-sm mt-1">Download analytics data for external analysis</p>
				</div>
				<div class="flex gap-3">
					<button class="btn-secondary">
						Export CSV
					</button>
					<button class="btn-secondary">
						Export PDF Report
					</button>
				</div>
			</div>
		</div>
	</div>
{:else}
	<div class="text-center py-12">
		<BarChart3 size={64} class="mx-auto text-gray-600 mb-4" />
		<h2 class="text-xl font-bold text-white mb-2">Access Restricted</h2>
		<p class="text-gray-400">You need to be logged in to view analytics.</p>
		<a href="/login" class="btn-primary mt-4">
			Sign In
		</a>
	</div>
{/if}