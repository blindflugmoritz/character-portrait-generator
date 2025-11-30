<script>
	import PostcardGenerator from '$lib/PostcardGenerator.svelte';
	import { Button } from '$lib/components/ui/button';
	import { ArrowLeft } from 'lucide-svelte';
</script>

<svelte:head>
	<title>Postcard Generator - Ground of Aces</title>
	<meta
		name="description"
		content="Create custom Ground of Aces promotional postcards with your character portraits"
	/>
</svelte:head>

<div class="postcard-page">
	<header class="page-header">
		<Button href="/" variant="ghost" size="sm">
			<ArrowLeft class="mr-2 h-4 w-4" />
			Back to Character Generator
		</Button>
		<h1>Postcard Generator</h1>
		<p>Create promotional postcards featuring your Ground of Aces crew</p>
	</header>

	<PostcardGenerator />
</div>

<style>
	.postcard-page {
		min-height: 100vh;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		padding: 1rem;
	}

	.page-header {
		max-width: 1400px;
		margin: 0 auto 2rem;
		padding: 1rem;
		background: rgba(255, 255, 255, 0.95);
		border-radius: var(--radius);
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	}

	.page-header h1 {
		font-size: 2rem;
		font-weight: bold;
		margin: 1rem 0 0.5rem;
		color: #1a1a1a;
	}

	.page-header p {
		color: #666;
		font-size: 1rem;
	}

	@media (max-width: 768px) {
		.page-header h1 {
			font-size: 1.5rem;
		}
	}
</style>
