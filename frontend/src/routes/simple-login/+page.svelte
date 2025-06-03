<script>
	let email = 'rfp@kzahhar.com';
	let password = 'password123';
	let loading = false;
	let error = '';

	async function handleLogin() {
		loading = true;
		error = '';

		try {
			const response = await fetch('/api/v1/auth/login', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ email, password }),
			});

			const result = await response.json();

			if (response.ok) {
				localStorage.setItem('auth_token', result.access_token);
				window.location.href = '/app';
			} else {
				error = result.detail || 'Login failed';
			}
		} catch (err) {
			error = 'Network error. Please try again.';
		} finally {
			loading = false;
		}
	}
</script>

<div class="min-h-screen bg-gray-950 flex items-center justify-center">
	<div class="bg-gray-900 p-8 rounded-lg border border-gray-700 w-full max-w-md">
		<h1 class="text-2xl font-bold text-white mb-6 text-center">TenderWise AI Login</h1>
		
		<form on:submit|preventDefault={handleLogin}>
			<div class="mb-4">
				<label class="block text-gray-300 mb-2">Email</label>
				<input 
					type="email" 
					bind:value={email}
					class="w-full px-3 py-2 bg-gray-800 border border-gray-600 text-white rounded-lg"
					required
				/>
			</div>
			
			<div class="mb-6">
				<label class="block text-gray-300 mb-2">Password</label>
				<input 
					type="password" 
					bind:value={password}
					class="w-full px-3 py-2 bg-gray-800 border border-gray-600 text-white rounded-lg"
					required
				/>
			</div>
			
			{#if error}
				<div class="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
					{error}
				</div>
			{/if}
			
			<button 
				type="submit" 
				disabled={loading}
				class="w-full py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white rounded-lg"
			>
				{loading ? 'Logging in...' : 'Login'}
			</button>
		</form>
		
		<div class="mt-4 text-center text-gray-400 text-sm">
			<p>AI Features Active: OpenAI + Anthropic</p>
			<p>API Documentation: <a href="http://localhost:8000/docs" class="text-blue-400">localhost:8000/docs</a></p>
		</div>
	</div>
</div></div>