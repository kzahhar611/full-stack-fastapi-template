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
	() => import('./nodes/14'),
	() => import('./nodes/15'),
	() => import('./nodes/16'),
	() => import('./nodes/17')
];

export const server_loads = [];

export const dictionary = {
		"/": [4],
		"/(app)/analytics": [5,[2]],
		"/(app)/dashboard-simple": [7,[2]],
		"/(app)/dashboard": [6,[2]],
		"/(app)/documents": [8,[2]],
		"/(auth)/login": [15,[3]],
		"/(app)/organizations": [9,[2]],
		"/(app)/rfps": [10,[2]],
		"/(app)/rfps/[id]": [11,[2]],
		"/(app)/rfps/[id]/documents": [12,[2]],
		"/simple-login": [16],
		"/test": [17],
		"/(app)/users": [13,[2]],
		"/(app)/workflows": [14,[2]]
	};

export const hooks = {
	handleError: (({ error }) => { console.error(error) }),
};

export { default as root } from '../root.svelte';