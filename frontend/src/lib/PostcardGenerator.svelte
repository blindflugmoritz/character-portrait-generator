<script>
	import { onMount } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import { Label } from '$lib/components/ui/label';
	import { Separator } from '$lib/components/ui/separator';
	import * as Select from '$lib/components/ui/select';
	import * as Card from '$lib/components/ui/card';
	import { Download } from 'lucide-svelte';

	/**
	 * @type {string}
	 */
	let selectedColor = 'blue';

	/**
	 * @type {Array<Object>}
	 */
	let crew = [];

	/**
	 * @type {Array<boolean>}
	 */
	let selectedCrewIndices = [];

	/**
	 * @type {Array<Object>}
	 */
	let selectedCharacters = [];

	/**
	 * @type {boolean}
	 */
	let isExporting = false;

	/**
	 * @type {boolean}
	 */
	let isGeneratingPreview = false;

	/**
	 * @type {string | null}
	 */
	let previewImage = null;

	// Load crew from localStorage
	onMount(() => {
		try {
			const saved = localStorage.getItem('crew');
			if (saved) {
				const parsed = JSON.parse(saved);
				if (parsed && Array.isArray(parsed) && parsed.length > 0) {
					crew = parsed;
					// Use all crew members (up to 10)
					const count = Math.min(crew.length, 10);
					selectedCrewIndices = crew.map((_, i) => i < count);
					updateSelectedCharacters();
					// Generate initial preview
					generatePreview();
				}
			}
		} catch (e) {
			console.error('Failed to load crew from localStorage:', e);
		}
	});

	/**
	 * Update the selected characters array based on checkbox selections
	 */
	function updateSelectedCharacters() {
		selectedCharacters = crew
			.filter((_, i) => selectedCrewIndices[i])
			.map(member => member.character)
			.slice(0, 10); // Max 10 characters
	}

	/**
	 * Generate preview image from server
	 */
	async function generatePreview() {
		if (selectedCharacters.length === 0) {
			previewImage = null;
			return;
		}

		isGeneratingPreview = true;

		try {
			// Always use localhost for now during development
			const apiUrl = 'http://localhost:8000/api/generate-postcard';

			console.log('=== STARTING PREVIEW GENERATION ===');
			console.log('API URL:', apiUrl);
			console.log('Character count:', selectedCharacters.length);
			console.log('First character data:', JSON.stringify(selectedCharacters[0], null, 2));

			const requestBody = {
				color: selectedColor,
				characters: selectedCharacters,
				format: 'base64'
			};
			console.log('Request body:', JSON.stringify(requestBody, null, 2));

			console.log('Making fetch request...');
			const response = await fetch(apiUrl, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(requestBody)
			});

			console.log('Fetch completed. Response status:', response.status);
			console.log('Response headers:', [...response.headers.entries()]);

			if (!response.ok) {
				const errorText = await response.text();
				console.error('Server error response:', errorText);
				throw new Error(`Failed to generate preview: ${response.status}`);
			}

			const data = await response.json();
			console.log('Got response data, image length:', data.image?.length);
			previewImage = `data:image/png;base64,${data.image}`;
			console.log('=== PREVIEW GENERATION SUCCESSFUL ===');
		} catch (error) {
			console.error('=== PREVIEW GENERATION FAILED ===');
			console.error('Error type:', error.constructor.name);
			console.error('Error message:', error.message);
			console.error('Full error:', error);
			alert(`Failed to generate preview: ${error.message}`);
			previewImage = null;
		} finally {
			isGeneratingPreview = false;
		}
	}

	/**
	 * Export postcard as PNG - now using server-side generation
	 */
	async function exportPostcard() {
		if (selectedCharacters.length === 0) return;

		isExporting = true;

		try {
			// Always use localhost for now during development
			const apiUrl = 'http://localhost:8000/api/generate-postcard';

			// Call server API to generate postcard
			const response = await fetch(apiUrl, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					color: selectedColor,
					characters: selectedCharacters,
					format: 'image'
				})
			});

			if (!response.ok) {
				const error = await response.json();
				throw new Error(error.error || 'Failed to generate postcard');
			}

			// Get the PNG blob from response
			const blob = await response.blob();

			// Create download link
			const url = URL.createObjectURL(blob);
			const link = document.createElement('a');
			const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
			const count = selectedCharacters.length;
			link.download = `GOA_Postcard_${selectedColor}_${count}crew_${timestamp}.png`;
			link.href = url;
			link.click();

			// Cleanup
			URL.revokeObjectURL(url);
		} catch (error) {
			console.error('Failed to export postcard:', error);
			alert(`Failed to generate postcard: ${error.message}`);
		} finally {
			isExporting = false;
		}
	}


	/**
	 * Regenerate preview when color changes
	 */
	let lastColor = selectedColor;
	$: if (selectedCharacters.length > 0 && selectedColor !== lastColor) {
		lastColor = selectedColor;
		generatePreview();
	}

	// Color options
	const colorOptions = [
		{ value: 'blue', label: 'Blue (R.A.F. Lichfield)' },
		{ value: 'orange', label: 'Orange (Lichfield Crew)' }
	];
</script>

<div class="postcard-generator">
	<Card.Root>
		<Card.Header>
			<Card.Title>Postcard Generator</Card.Title>
			<Card.Description>Create a Ground of Aces postcard with your crew</Card.Description>
		</Card.Header>
		<Card.Content class="space-y-6">
			{#if crew.length === 0}
				<div class="empty-state">
					<p>No crew members found. Create some on the main page first!</p>
					<Button href="/" variant="outline" class="mt-4">Go to Character Generator</Button>
				</div>
			{:else}
				<!-- Info -->
				<div class="info-section">
					<p>Creating postcard with {Math.min(crew.length, 10)} crew member{Math.min(crew.length, 10) !== 1 ? 's' : ''}</p>
					{#if crew.length > 10}
						<p class="text-sm text-muted-foreground">Using first 10 crew members (maximum)</p>
					{/if}
				</div>

				<!-- Postcard Style Selection -->
				<div class="setting-group">
					<Label>Postcard Style</Label>
					<Select.Root type="single" bind:value={selectedColor}>
						<Select.Trigger class="w-full">
							{colorOptions.find((c) => c.value === selectedColor)?.label || 'Select style'}
						</Select.Trigger>
						<Select.Content>
							{#each colorOptions as option}
								<Select.Item value={option.value}>{option.label}</Select.Item>
							{/each}
						</Select.Content>
					</Select.Root>
				</div>

				<!-- Preview -->
				<div class="preview-section">
					<Label>Preview</Label>
					{#if previewImage}
						<img src={previewImage} alt="Postcard preview" class="preview-image" />
						{#if isGeneratingPreview}
							<div class="preview-overlay">
								<div class="spinner"></div>
								<p>Generating preview...</p>
							</div>
						{/if}
					{:else}
						<div class="preview-placeholder">
							{#if isGeneratingPreview}
								<div class="spinner"></div>
								<p>Generating preview...</p>
							{:else}
								<p>Preview will appear here</p>
							{/if}
						</div>
					{/if}
				</div>

				<!-- Export Button -->
				<Button onclick={exportPostcard} class="w-full" size="lg" disabled={isExporting}>
					<Download class="mr-2 h-4 w-4" />
					{isExporting ? 'Generating High-Quality Postcard...' : 'Export High-Quality Postcard'}
				</Button>
			{/if}
		</Card.Content>
	</Card.Root>
</div>

<style>
	.postcard-generator {
		max-width: 900px;
		margin: 0 auto;
		padding: 2rem;
	}

	.empty-state {
		text-align: center;
		padding: 3rem;
		color: var(--muted-foreground);
	}

	.setting-group {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.info-section {
		padding: 1rem;
		background: var(--muted);
		border-radius: var(--radius);
		text-align: center;
	}

	.info-section p {
		font-weight: 500;
		color: var(--foreground);
	}

	.preview-section {
		position: relative;
	}

	.preview-image {
		width: 100%;
		height: auto;
		border-radius: var(--radius);
		border: 1px solid var(--border);
		margin-top: 0.5rem;
	}

	.preview-placeholder {
		width: 100%;
		min-height: 400px;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		border: 2px dashed var(--border);
		border-radius: var(--radius);
		margin-top: 0.5rem;
		color: var(--muted-foreground);
	}

	.preview-overlay {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.7);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		border-radius: var(--radius);
		color: white;
	}

	.spinner {
		width: 40px;
		height: 40px;
		border: 4px solid rgba(255, 255, 255, 0.3);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin-bottom: 1rem;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	@media (max-width: 768px) {
		.character-count-grid {
			grid-template-columns: repeat(5, 1fr);
		}
	}
</style>
