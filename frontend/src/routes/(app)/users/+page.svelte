<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { apiClient } from '$lib/api/client';
	import { 
		Users, 
		Plus, 
		Search,
		Filter,
		MoreVertical,
		Shield,
		Mail,
		Building2
	} from 'lucide-svelte';

	let loading = true;
	let users = [];
	let searchTerm = '';
	let selectedRole = 'all';
	let error = null;

	// Check if user has access
	$: hasAccess = authStore.isAdmin();

	onMount(async () => {
		if (hasAccess) {
			await loadUsers();
		}
	});

	async function loadUsers() {
		loading = true;
		error = null;
		
		try {
			// Mock users data (in real app, would fetch from API)
			users = [
				{
					id: 1,
					email: 'rfp@kzahhar.com',
					first_name: 'Admin',
					last_name: 'User',
					role: 'super_admin',
					status: 'active',
					is_active: true,
					organization: { name: 'TenderWise' },
					last_login: '2025-01-03T10:30:00Z',
					created_at: '2024-01-01T00:00:00Z'
				},
				{
					id: 2,
					email: 'manager@company.com',
					first_name: 'John',
					last_name: 'Manager',
					role: 'manager',
					status: 'active',
					is_active: true,
					organization: { name: 'ABC Corp' },
					last_login: '2025-01-02T15:20:00Z',
					created_at: '2024-02-15T00:00:00Z'
				},
				{
					id: 3,
					email: 'user@company.com',
					first_name: 'Jane',
					last_name: 'User',
					role: 'user',
					status: 'active',
					is_active: true,
					organization: { name: 'ABC Corp' },
					last_login: '2025-01-01T09:15:00Z',
					created_at: '2024-03-10T00:00:00Z'
				}
			];
		} catch (err) {
			console.error('Failed to load users:', err);
			error = err.message || 'Failed to load users';
		} finally {
			loading = false;
		}
	}

	function getRoleBadgeClass(role) {
		const roleClasses = {
			super_admin: 'bg-red-600 text-white',
			admin: 'bg-orange-600 text-white',
			manager: 'bg-blue-600 text-white',
			user: 'bg-green-600 text-white',
			viewer: 'bg-gray-600 text-white'
		};
		return roleClasses[role] || 'bg-gray-600 text-white';
	}

	function getStatusBadgeClass(status) {
		return status === 'active' ? 'bg-green-600 text-white' : 'bg-red-600 text-white';
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

	// Filter users based on search term and role
	$: filteredUsers = users.filter(user => {
		const matchesSearch = !searchTerm || 
			user.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
			user.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
			user.email.toLowerCase().includes(searchTerm.toLowerCase());
		
		const matchesRole = selectedRole === 'all' || user.role === selectedRole;
		
		return matchesSearch && matchesRole;
	});
</script>

<svelte:head>
	<title>Users - TenderWise AI</title>
</svelte:head>

{#if !hasAccess}
	<div class="text-center py-12">
		<Shield size={64} class="mx-auto text-gray-600 mb-4" />
		<h2 class="text-xl font-bold text-white mb-2">Access Restricted</h2>
		<p class="text-gray-400">You need administrator privileges to view users.</p>
	</div>
{:else}
	<div class="space-y-6">
		<!-- Header -->
		<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-3xl font-bold text-white flex items-center gap-3">
					<Users size={32} class="text-blue-400" />
					User Management
				</h1>
				<p class="text-gray-400 mt-2">Manage user accounts and permissions</p>
			</div>
			
			<div class="mt-4 sm:mt-0">
				<button class="btn-primary flex items-center gap-2">
					<Plus size={16} />
					Add User
				</button>
			</div>
		</div>

		{#if loading}
			<div class="flex items-center justify-center py-12">
				<div class="spinner w-8 h-8"></div>
				<span class="text-gray-400 ml-3">Loading users...</span>
			</div>
		{:else if error}
			<div class="card bg-red-900/20 border-red-700 text-red-300">
				<div class="flex items-center gap-3">
					<Users size={20} />
					<div>
						<h3 class="font-medium">Failed to Load Users</h3>
						<p class="text-sm text-red-200 mt-1">{error}</p>
					</div>
					<button 
						on:click={loadUsers}
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
								placeholder="Search users..."
								bind:value={searchTerm}
								class="input pl-10"
							/>
						</div>
					</div>
					
					<!-- Role Filter -->
					<div class="sm:w-48">
						<select bind:value={selectedRole} class="input">
							<option value="all">All Roles</option>
							<option value="super_admin">Super Admin</option>
							<option value="admin">Admin</option>
							<option value="manager">Manager</option>
							<option value="user">User</option>
							<option value="viewer">Viewer</option>
						</select>
					</div>
				</div>
			</div>

			<!-- Users Table -->
			<div class="card">
				<div class="overflow-x-auto">
					<table class="w-full">
						<thead>
							<tr class="border-b border-gray-700">
								<th class="text-left py-3 px-4 text-gray-400 font-medium">User</th>
								<th class="text-left py-3 px-4 text-gray-400 font-medium">Role</th>
								<th class="text-left py-3 px-4 text-gray-400 font-medium">Organization</th>
								<th class="text-left py-3 px-4 text-gray-400 font-medium">Status</th>
								<th class="text-left py-3 px-4 text-gray-400 font-medium">Last Login</th>
								<th class="text-right py-3 px-4 text-gray-400 font-medium">Actions</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-700">
							{#each filteredUsers as user}
								<tr class="hover:bg-gray-800/50">
									<td class="py-4 px-4">
										<div class="flex items-center gap-3">
											<div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
												<span class="text-white text-sm font-medium">
													{user.first_name[0]}{user.last_name[0]}
												</span>
											</div>
											<div>
												<div class="text-white font-medium">
													{user.first_name} {user.last_name}
												</div>
												<div class="text-gray-400 text-sm flex items-center gap-1">
													<Mail size={14} />
													{user.email}
												</div>
											</div>
										</div>
									</td>
									<td class="py-4 px-4">
										<span class="badge {getRoleBadgeClass(user.role)}">
											{user.role.replace('_', ' ').toUpperCase()}
										</span>
									</td>
									<td class="py-4 px-4">
										<div class="flex items-center gap-2 text-gray-300">
											<Building2 size={16} />
											<span>{user.organization?.name || 'No Organization'}</span>
										</div>
									</td>
									<td class="py-4 px-4">
										<span class="badge {getStatusBadgeClass(user.status)}">
											{user.status.toUpperCase()}
										</span>
									</td>
									<td class="py-4 px-4 text-gray-300">
										{user.last_login ? formatDate(user.last_login) : 'Never'}
									</td>
									<td class="py-4 px-4 text-right">
										<button class="p-2 text-gray-400 hover:text-white">
											<MoreVertical size={16} />
										</button>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
				
				{#if filteredUsers.length === 0}
					<div class="text-center py-8 text-gray-400">
						<Users size={48} class="mx-auto mb-4 opacity-50" />
						<p class="text-lg font-medium">No users found</p>
						<p class="text-sm mt-2">
							{searchTerm || selectedRole !== 'all' ? 'Try adjusting your filters' : 'No users available'}
						</p>
					</div>
				{/if}
			</div>

			<!-- User Stats -->
			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
				<div class="card-hover">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-400 text-sm">Total Users</p>
							<p class="text-2xl font-bold text-white">{users.length}</p>
						</div>
						<div class="p-3 bg-blue-600 rounded-lg">
							<Users size={24} class="text-white" />
						</div>
					</div>
				</div>
				
				<div class="card-hover">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-400 text-sm">Active Users</p>
							<p class="text-2xl font-bold text-white">{users.filter(u => u.is_active).length}</p>
						</div>
						<div class="p-3 bg-green-600 rounded-lg">
							<Shield size={24} class="text-white" />
						</div>
					</div>
				</div>
				
				<div class="card-hover">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-400 text-sm">Admins</p>
							<p class="text-2xl font-bold text-white">{users.filter(u => u.role === 'admin' || u.role === 'super_admin').length}</p>
						</div>
						<div class="p-3 bg-orange-600 rounded-lg">
							<Shield size={24} class="text-white" />
						</div>
					</div>
				</div>
				
				<div class="card-hover">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-gray-400 text-sm">Managers</p>
							<p class="text-2xl font-bold text-white">{users.filter(u => u.role === 'manager').length}</p>
						</div>
						<div class="p-3 bg-purple-600 rounded-lg">
							<Users size={24} class="text-white" />
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
{/if}