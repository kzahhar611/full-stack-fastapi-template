<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { Eye, EyeOff, Loader2, AlertCircle } from 'lucide-svelte';
	
	let email = '';
	let password = '';
	let showPassword = false;
	let isLoading = false;
	let errorMessage = '';
	
	// Clear any existing errors when component mounts
	onMount(() => {
		authStore.clearError();
	});
	
	// Subscribe to auth store for error handling
	$: if ($authStore.error) {
		errorMessage = $authStore.error;
		isLoading = false;
	}
	
	async function handleLogin() {
		if (!email || !password) {
			errorMessage = 'Please enter both email and password';
			return;
		}
		
		errorMessage = '';
		isLoading = true;
		
		try {
			const result = await authStore.login(email, password);
			
			if (result.success) {
				goto('/dashboard');
			} else {
				errorMessage = result.error || 'Login failed';
				isLoading = false;
			}
		} catch (error) {
			console.error('Login error:', error);
			errorMessage = 'An unexpected error occurred';
			isLoading = false;
		}
	}
	
	function handleKeyPress(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			handleLogin();
		}
	}
	
	function togglePasswordVisibility() {
		showPassword = !showPassword;
	}
</script>

<svelte:head>
	<title>Login - TenderWise AI</title>
	<meta name="description" content="Sign in to TenderWise AI - Enterprise RFP & Tendering Platform" />
</svelte:head>

<div class="animate-fadeIn">
	<!-- Header -->
	<div class="text-center mb-8">
		<h2 class="text-3xl font-bold text-white mb-2">
			Welcome back
		</h2>
		<p class="text-gray-400">
			Sign in to your TenderWise AI account
		</p>
	</div>
	
	<!-- Login Form -->
	<form on:submit|preventDefault={handleLogin} class="space-y-6">
		<!-- Email Field -->
		<div class="form-group">
			<label for="email" class="form-label">
				Email address
			</label>
			<input
				id="email"
				type="email"
				bind:value={email}
				on:keypress={handleKeyPress}
				class="input"
				placeholder="Enter your email"
				required
				disabled={isLoading}
			/>
		</div>
		
		<!-- Password Field -->
		<div class="form-group">
			<label for="password" class="form-label">
				Password
			</label>
			<div class="relative">
				{#if showPassword}
					<input
						id="password"
						type="text"
						bind:value={password}
						on:keypress={handleKeyPress}
						class="input pr-10"
						placeholder="Enter your password"
						required
						disabled={isLoading}
					/>
				{:else}
					<input
						id="password"
						type="password"
						bind:value={password}
						on:keypress={handleKeyPress}
						class="input pr-10"
						placeholder="Enter your password"
						required
						disabled={isLoading}
					/>
				{/if}
				<button
					type="button"
					on:click={togglePasswordVisibility}
					class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-300"
					disabled={isLoading}
				>
					{#if showPassword}
						<EyeOff size={20} />
					{:else}
						<Eye size={20} />
					{/if}
				</button>
			</div>
		</div>
		
		<!-- Error Message -->
		{#if errorMessage}
			<div class="flex items-center gap-2 p-3 bg-red-900/20 border border-red-700 rounded-md text-red-300">
				<AlertCircle size={16} />
				<span class="text-sm">{errorMessage}</span>
			</div>
		{/if}
		
		<!-- Submit Button -->
		<button
			type="submit"
			disabled={isLoading || !email || !password}
			class="w-full btn-primary flex items-center justify-center gap-2 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
		>
			{#if isLoading}
				<Loader2 size={20} class="animate-spin" />
				<span>Signing in...</span>
			{:else}
				<span>Sign in</span>
			{/if}
		</button>
		
		<!-- Demo Credentials -->
		<div class="mt-6 p-4 bg-blue-900/20 border border-blue-700 rounded-md">
			<h4 class="text-sm font-medium text-blue-300 mb-2">Demo Credentials</h4>
			<div class="text-xs text-blue-200 space-y-1">
				<div>Email: <code class="bg-blue-800 px-1 rounded">rfp@kzahhar.com</code></div>
				<div>Password: <code class="bg-blue-800 px-1 rounded">password123</code></div>
			</div>
			<button
				type="button"
				on:click={() => {
					email = 'rfp@kzahhar.com';
					password = 'password123';
				}}
				class="mt-2 text-xs text-blue-300 hover:text-blue-200 underline"
				disabled={isLoading}
			>
				Fill demo credentials
			</button>
		</div>
	</form>
	
	<!-- Footer -->
	<div class="mt-8 text-center">
		<p class="text-sm text-gray-400">
			Don't have an account? 
			<a href="/contact" class="text-blue-400 hover:text-blue-300 underline">
				Contact admin
			</a>
		</p>
	</div>
</div>

<style>
	code {
		font-family: 'JetBrains Mono', monospace;
	}
</style>