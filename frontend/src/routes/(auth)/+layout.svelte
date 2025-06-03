<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	
	// Redirect if already authenticated
	onMount(() => {
		const unsubscribe = authStore.subscribe((auth) => {
			if (auth.isAuthenticated) {
				goto('/dashboard');
			}
		});
		
		return unsubscribe;
	});
</script>

<!-- Auth Layout -->
<div class="min-h-screen flex">
	<!-- Left side - Branding -->
	<div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-900 via-blue-800 to-purple-900 relative overflow-hidden">
		<div class="absolute inset-0 bg-black opacity-20"></div>
		<div class="relative z-10 flex flex-col justify-center px-12 text-white">
			<div class="max-w-md">
				<h1 class="text-4xl font-bold mb-6 text-gradient">
					TenderWise AI
				</h1>
				<p class="text-xl text-blue-100 mb-8">
					Enterprise RFP & Tendering Platform powered by AI
				</p>
				<div class="space-y-4 text-blue-200">
					<div class="flex items-center gap-3">
						<div class="w-2 h-2 bg-blue-400 rounded-full"></div>
						<span>AI-powered proposal analysis</span>
					</div>
					<div class="flex items-center gap-3">
						<div class="w-2 h-2 bg-blue-400 rounded-full"></div>
						<span>Visual workflow designer</span>
					</div>
					<div class="flex items-center gap-3">
						<div class="w-2 h-2 bg-blue-400 rounded-full"></div>
						<span>Multi-tenant organization management</span>
					</div>
					<div class="flex items-center gap-3">
						<div class="w-2 h-2 bg-blue-400 rounded-full"></div>
						<span>Enterprise-grade security</span>
					</div>
				</div>
			</div>
		</div>
		
		<!-- Decorative elements -->
		<div class="absolute top-0 right-0 w-64 h-64 bg-blue-500 rounded-full opacity-10 transform translate-x-32 -translate-y-32"></div>
		<div class="absolute bottom-0 left-0 w-48 h-48 bg-purple-500 rounded-full opacity-10 transform -translate-x-24 translate-y-24"></div>
	</div>
	
	<!-- Right side - Auth form -->
	<div class="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 bg-gray-950">
		<div class="max-w-md w-full">
			<slot />
		</div>
	</div>
</div>