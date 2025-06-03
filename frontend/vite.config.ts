import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [sveltekit()],
	
	// Development server configuration
	server: {
		host: '0.0.0.0',
		port: 5173,
		strictPort: true,
		fs: {
			allow: ['..']
		}
	},

	// Preview server configuration
	preview: {
		host: '0.0.0.0',
		port: 4173,
		strictPort: true
	},

	// Build configuration
	build: {
		target: 'esnext',
		sourcemap: true,
		rollupOptions: {
			output: {
				manualChunks: {
					vendor: ['svelte', '@sveltejs/kit'],
					ui: ['lucide-svelte', 'bits-ui'],
					workflow: ['@xyflow/svelte', 'd3'],
					utils: ['clsx', 'tailwind-merge', 'zod']
				}
			}
		}
	},

	// CSS configuration
	css: {
		preprocessorOptions: {
			scss: {
				additionalData: `@import 'src/styles/variables.scss';`
			}
		}
	},

	// Testing configuration
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}'],
		environment: 'jsdom',
		globals: true,
		setupFiles: ['src/lib/test-setup.ts']
	},

	// Dependency optimization
	optimizeDeps: {
		include: [
			'socket.io-client',
			'd3',
			'fabric',
			'uuid',
			'@tanstack/svelte-query'
		],
		exclude: ['@xyflow/svelte']
	},

	// Define global constants
	define: {
		__APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
		__BUILD_TIME__: JSON.stringify(new Date().toISOString())
	},

	// Environment variables
	envPrefix: ['VITE_', 'PUBLIC_'],

	// Resolve configuration
	resolve: {
		alias: {
			$components: '/src/lib/components',
			$stores: '/src/stores',
			$types: '/src/lib/types',
			$utils: '/src/lib/utils',
			$api: '/src/lib/api'
		}
	}
});