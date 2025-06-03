<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import { ArrowRight, Building2, Workflow, Shield, Zap } from 'lucide-svelte';
	
	onMount(() => {
		// Check if user is already authenticated and redirect
		if ($authStore.isAuthenticated) {
			goto('/dashboard');
		}
	});
</script>

<svelte:head>
	<title>TenderWise AI - Enterprise RFP & Tendering Platform</title>
	<meta name="description" content="AI-powered RFP management and tendering platform for enterprises. Streamline your procurement process with intelligent workflows." />
</svelte:head>

<!-- Landing Page -->
<div class="min-h-screen bg-gradient-to-br from-gray-950 via-blue-950 to-purple-950">
	<!-- Navigation -->
	<nav class="relative z-10 px-6 py-4">
		<div class="max-w-7xl mx-auto flex items-center justify-between">
			<div class="flex items-center gap-3">
				<div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
					<span class="text-white font-bold text-sm">TW</span>
				</div>
				<span class="text-white font-semibold text-xl">TenderWise AI</span>
			</div>
			
			<div class="flex items-center gap-4">
				<a 
					href="/login" 
					class="btn-primary"
				>
					Sign In
				</a>
			</div>
		</div>
	</nav>

	<!-- Hero Section -->
	<section class="relative px-6 py-20">
		<div class="max-w-7xl mx-auto text-center">
			<h1 class="text-5xl md:text-7xl font-bold text-white mb-8">
				<span class="text-gradient">AI-Powered</span><br>
				RFP Platform
			</h1>
			
			<p class="text-xl md:text-2xl text-blue-100 mb-12 max-w-3xl mx-auto">
				Streamline your procurement process with intelligent workflows, 
				AI-driven analysis, and enterprise-grade security.
			</p>
			
			<div class="flex flex-col sm:flex-row gap-4 justify-center mb-16">
				<a href="/login" class="btn-primary flex items-center gap-2 px-8 py-4 text-lg">
					Get Started
					<ArrowRight size={20} />
				</a>
				<a href="#features" class="btn-ghost px-8 py-4 text-lg">
					Learn More
				</a>
			</div>
			
			<!-- Demo Credentials Note -->
			<div class="inline-block p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
				<p class="text-sm text-blue-200 mb-2">
					<strong>Demo Access Available</strong>
				</p>
				<p class="text-xs text-blue-300">
					Use <code class="bg-blue-800 px-1 rounded">rfp@kzahhar.com</code> / 
					<code class="bg-blue-800 px-1 rounded">password123</code> to explore the platform
				</p>
			</div>
		</div>
		
		<!-- Background decoration -->
		<div class="absolute inset-0 overflow-hidden pointer-events-none">
			<div class="absolute top-1/4 left-1/4 w-64 h-64 bg-blue-500 rounded-full opacity-10 blur-3xl"></div>
			<div class="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-500 rounded-full opacity-10 blur-3xl"></div>
		</div>
	</section>

	<!-- Features Section -->
	<section id="features" class="px-6 py-20 bg-black/20">
		<div class="max-w-7xl mx-auto">
			<div class="text-center mb-16">
				<h2 class="text-4xl font-bold text-white mb-4">
					Everything you need for modern procurement
				</h2>
				<p class="text-xl text-gray-300 max-w-2xl mx-auto">
					From RFP creation to proposal analysis, TenderWise AI provides comprehensive tools 
					for enterprise procurement teams.
				</p>
			</div>
			
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
				<!-- AI-Powered Analysis -->
				<div class="text-center">
					<div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
						<Zap size={32} class="text-white" />
					</div>
					<h3 class="text-xl font-semibold text-white mb-2">AI Analysis</h3>
					<p class="text-gray-400">
						Intelligent proposal evaluation with AI-powered insights and recommendations.
					</p>
				</div>
				
				<!-- Visual Workflows -->
				<div class="text-center">
					<div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center mx-auto mb-4">
						<Workflow size={32} class="text-white" />
					</div>
					<h3 class="text-xl font-semibold text-white mb-2">Visual Workflows</h3>
					<p class="text-gray-400">
						Design custom procurement workflows with our intuitive visual editor.
					</p>
				</div>
				
				<!-- Multi-Tenant -->
				<div class="text-center">
					<div class="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center mx-auto mb-4">
						<Building2 size={32} class="text-white" />
					</div>
					<h3 class="text-xl font-semibold text-white mb-2">Multi-Tenant</h3>
					<p class="text-gray-400">
						Secure organization isolation with role-based access controls.
					</p>
				</div>
				
				<!-- Enterprise Security -->
				<div class="text-center">
					<div class="w-16 h-16 bg-gradient-to-br from-red-500 to-red-600 rounded-lg flex items-center justify-center mx-auto mb-4">
						<Shield size={32} class="text-white" />
					</div>
					<h3 class="text-xl font-semibold text-white mb-2">Enterprise Security</h3>
					<p class="text-gray-400">
						Bank-grade security with encryption, audit trails, and compliance tools.
					</p>
				</div>
			</div>
		</div>
	</section>

	<!-- CTA Section -->
	<section class="px-6 py-20">
		<div class="max-w-4xl mx-auto text-center">
			<h2 class="text-4xl font-bold text-white mb-8">
				Ready to transform your procurement process?
			</h2>
			
			<p class="text-xl text-gray-300 mb-12">
				Join leading organizations using TenderWise AI to streamline 
				their RFP and tendering operations.
			</p>
			
			<a href="/login" class="btn-primary flex items-center gap-2 px-8 py-4 text-lg mx-auto w-fit">
				Start Your Journey
				<ArrowRight size={20} />
			</a>
		</div>
	</section>

	<!-- Footer -->
	<footer class="border-t border-gray-800 px-6 py-8">
		<div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between">
			<div class="flex items-center gap-3 mb-4 md:mb-0">
				<div class="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded flex items-center justify-center">
					<span class="text-white font-bold text-xs">TW</span>
				</div>
				<span class="text-gray-400">© 2025 TenderWise AI. All rights reserved.</span>
			</div>
			
			<div class="flex gap-6 text-sm text-gray-400">
				<a href="#" class="hover:text-white transition-colors">Privacy</a>
				<a href="#" class="hover:text-white transition-colors">Terms</a>
				<a href="#" class="hover:text-white transition-colors">Contact</a>
			</div>
		</div>
	</footer>
</div>