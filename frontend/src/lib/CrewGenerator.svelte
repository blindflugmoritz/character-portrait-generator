<script>
	import { Button } from '$lib/components/ui/button';
	import { Textarea } from '$lib/components/ui/textarea';
	import { Label } from '$lib/components/ui/label';

	let { onCrewGenerated } = $props();

	let description = $state('');
	let replaceExisting = $state(false);
	let loading = $state(false);
	let error = $state('');
	let successMessage = $state('');

	const API_URL = 'https://blindflugstudios.pythonanywhere.com';

	async function generateCrew() {
		if (!description.trim()) {
			error = 'Please enter a description';
			return;
		}

		loading = true;
		error = '';
		successMessage = '';

		try {
			const response = await fetch(`${API_URL}/api/generate-crew`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					description,
					replaceExisting
				})
			});

			const data = await response.json();

			if (!response.ok) {
				throw new Error(data.error || 'Failed to generate crew');
			}

			onCrewGenerated(data.crew, data.replaceExisting);
			successMessage = `Successfully generated ${data.count} crew member${data.count !== 1 ? 's' : ''}!`;
			description = '';
		} catch (err) {
			error = err.message;
			console.error('Crew generation error:', err);
		} finally {
			loading = false;
		}
	}

	const examples = [
		'Create a crew of 10 Polish pilots from 303 Squadron',
		'Generate 5 American bomber crew members from the 8th Air Force',
		'Create 8 British ground crew mechanics and engineers',
		'Generate a diverse crew of 6 female pilots from the ATA',
		'Create 10 Canadian aircrew from 6 Group Bomber Command'
	];

	function useExample(example) {
		description = example;
	}
</script>

<div class="bg-card text-card-foreground flex flex-col gap-6 rounded-xl border py-6 shadow-sm p-6">
	<div class="mb-5">
		<h3 class="text-xl font-bold mb-2">🤖 AI Crew Generator</h3>
		<p class="text-sm text-muted-foreground mb-1">
			Describe your crew and let AI generate authentic characters with backgrounds
		</p>
		<p class="text-xs text-muted-foreground italic">Maximum 10 crew members per generation</p>
	</div>

	<div class="mb-5 p-4 bg-muted/50 rounded-lg border">
		<Label class="text-sm font-semibold mb-3 block">Quick examples:</Label>
		<div class="flex flex-wrap gap-2">
			{#each examples as example}
				<Button
					onclick={() => useExample(example)}
					variant="outline"
					size="sm"
					class="text-xs"
				>
					{example}
				</Button>
			{/each}
		</div>
	</div>

	<div class="mb-4">
		<Label for="crew-description">Crew Description</Label>
		<Textarea
			id="crew-description"
			bind:value={description}
			placeholder="E.g., 'Create a crew of 10 Polish pilots from 303 Squadron with varied experience levels'"
			rows={4}
			disabled={loading}
			class="mt-2"
		/>
	</div>

	<div class="mb-4">
		<label class="flex items-center gap-2 cursor-pointer">
			<input type="checkbox" bind:checked={replaceExisting} disabled={loading} class="cursor-pointer" />
			<span class="text-sm">Replace existing crew (otherwise adds to current crew)</span>
		</label>
	</div>

	{#if error}
		<div class="bg-destructive/10 border border-destructive text-destructive p-3 rounded mb-4 text-sm">
			<strong>Error:</strong>
			{error}
		</div>
	{/if}

	{#if successMessage}
		<div class="bg-green-50 border border-green-200 text-green-700 p-3 rounded mb-4 text-sm">
			{successMessage}
		</div>
	{/if}

	<Button onclick={generateCrew} disabled={loading || !description.trim()} class="w-full">
		{#if loading}
			<div class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></div>
			Generating crew...
		{:else}
			✨ Generate Crew
		{/if}
	</Button>
</div>
