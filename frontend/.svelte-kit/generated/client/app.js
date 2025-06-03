export { matchers } from './matchers.js';

export const nodes = [
	() => import('./nodes/0'),
	() => import('./nodes/1'),
	() => import('./nodes/2'),
	() => import('./nodes/3'),
	() => import('./nodes/4'),
	() => import('./nodes/5'),
	() => import('./nodes/6'),
	() => import('./nodes/7'),
	() => import('./nodes/8'),
	() => import('./nodes/9'),
	() => import('./nodes/10'),
	() => import('./nodes/11'),
	() => import('./nodes/12'),
	() => import('./nodes/13'),
	() => import('./nodes/14')
];

export const server_loads = [];

export const dictionary = {
		"/": [4],
		"/(app)/analytics": [5,[2]],
		"/(app)/dashboard-simple": [7,[2]],
		"/(app)/dashboard": [6,[2]],
		"/(auth)/login": [12,[3]],
		"/(app)/rfps": [8,[2]],
		"/(app)/rfps/[id]": [9,[2]],
		"/(app)/rfps/[id]/documents": [10,[2]],
		"/simple-login": [13],
		"/test": [14],
		"/(app)/users": [11,[2]]
	};

export const hooks = {
	handleError: (({ error }) => { console.error(error) }),
};

export { default as root } from '../root.svelte';