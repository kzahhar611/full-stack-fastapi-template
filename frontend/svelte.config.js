import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://kit.svelte.dev/docs/integrations#preprocessors
	// for more information about preprocessors
	preprocess: vitePreprocess(),

	kit: {
		// adapter-auto only supports some environments, see https://kit.svelte.dev/docs/adapter-auto for a list.
		// If your environment is not supported or you settled on a specific environment, switch out the adapter.
		// See https://kit.svelte.dev/docs/adapters for more information about adapters.
		adapter: adapter(),
		
		// Application configuration
		alias: {
			$components: 'src/lib/components',
			$stores: 'src/stores',
			$types: 'src/lib/types',
			$utils: 'src/lib/utils',
			$api: 'src/lib/api'
		},

		// Environment variables
		env: {
			publicPrefix: 'PUBLIC_',
			privatePrefix: 'PRIVATE_'
		},

		// CSP configuration for security
		csp: {
			mode: 'auto',
			directives: {
				'script-src': ['self', 'unsafe-inline'],
				'style-src': ['self', 'unsafe-inline'],
				'img-src': ['self', 'data:', 'https:'],
				'font-src': ['self', 'https://fonts.gstatic.com'],
				'connect-src': ['self', 'ws://localhost:*', 'wss://localhost:*']
			}
		},

		// Service worker
		serviceWorker: {
			register: false
		},

		// App configuration
		appDir: '_app',
		files: {
			assets: 'static',
			hooks: {
				client: 'src/hooks.client.ts',
				server: 'src/hooks.server.ts'
			},
			lib: 'src/lib',
			params: 'src/params',
			routes: 'src/routes',
			serviceWorker: 'src/service-worker.ts',
			appTemplate: 'src/app.html',
			errorTemplate: 'src/error.html'
		},

		// TypeScript configuration
		typescript: {
			config: (config) => {
				config.compilerOptions = {
					...config.compilerOptions,
					strict: true,
					noImplicitReturns: true,
					noFallthroughCasesInSwitch: true,
					noUncheckedIndexedAccess: true
				};
				return config;
			}
		}
	},

	// Svelte compiler options
	compilerOptions: {
		runes: false, // Keep false for SvelteKit compatibility
		dev: process.env.NODE_ENV === 'development'
	},

	// Vite plugin options
	vitePlugin: {
		inspector: {
			holdMode: true,
			showToggleButton: 'always',
			toggleButtonPos: 'bottom-right'
		}
	}
};

export default config;