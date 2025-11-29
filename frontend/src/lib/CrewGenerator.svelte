<script>
	import { env } from '$env/dynamic/public';

	export let onCrewGenerated = (crew) => {};

	let description = '';
	let replaceExisting = false;
	let loading = false;
	let error = '';
	let successMessage = '';

	// Get API URL from environment (defaults to localhost for development)
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

			// Call the callback with generated crew
			onCrewGenerated(data.crew, data.replaceExisting);

			successMessage = `Successfully generated ${data.count} crew member${data.count !== 1 ? 's' : ''}!`;

			// Clear description after successful generation
			description = '';
		} catch (err) {
			error = err.message;
			console.error('Crew generation error:', err);
		} finally {
			loading = false;
		}
	}

	// Example descriptions
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

<div class="generator-container">
	<div class="generator-header">
		<h3>🤖 AI Crew Generator</h3>
		<p>Describe your crew and let AI generate authentic characters with backgrounds</p>
		<p class="limit-note">Maximum 10 crew members per generation</p>
	</div>

	<div class="examples">
		<label>Quick examples:</label>
		<div class="example-buttons">
			{#each examples as example}
				<button class="example-btn" on:click={() => useExample(example)}>
					{example}
				</button>
			{/each}
		</div>
	</div>

	<div class="input-section">
		<label for="crew-description">Crew Description</label>
		<textarea
			id="crew-description"
			bind:value={description}
			placeholder="E.g., 'Create a crew of 10 Polish pilots from 303 Squadron with varied experience levels'"
			rows="4"
			disabled={loading}
		/>
	</div>

	<div class="options">
		<label class="checkbox-label">
			<input type="checkbox" bind:checked={replaceExisting} disabled={loading} />
			Replace existing crew (otherwise adds to current crew)
		</label>
	</div>

	{#if error}
		<div class="error-message">
			<strong>Error:</strong>
			{error}
		</div>
	{/if}

	{#if successMessage}
		<div class="success-message">{successMessage}</div>
	{/if}

	<button class="generate-btn" on:click={generateCrew} disabled={loading || !description.trim()}>
		{#if loading}
			<span class="spinner"></span>
			Generating crew...
		{:else}
			✨ Generate Crew
		{/if}
	</button>
</div>

<style>
	.generator-container {
		background: white;
		border: 2px solid #333;
		border-radius: 8px;
		padding: 20px;
		margin-bottom: 20px;
	}

	.generator-header {
		margin-bottom: 20px;
	}

	.generator-header h3 {
		margin: 0 0 8px 0;
		color: #333;
		font-size: 20px;
	}

	.generator-header p {
		margin: 0;
		color: #666;
		font-size: 14px;
	}

	.generator-header .limit-note {
		margin-top: 8px;
		color: #888;
		font-size: 12px;
		font-style: italic;
	}

	.examples {
		margin-bottom: 20px;
		padding: 15px;
		background: #f8f9fa;
		border-radius: 5px;
	}

	.examples label {
		display: block;
		font-weight: bold;
		color: #555;
		font-size: 13px;
		margin-bottom: 10px;
	}

	.example-buttons {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.example-btn {
		background: white;
		border: 1px solid #ddd;
		padding: 6px 12px;
		border-radius: 4px;
		font-size: 12px;
		cursor: pointer;
		transition: all 0.2s ease;
		color: #555;
	}

	.example-btn:hover {
		border-color: #667eea;
		color: #667eea;
		background: #f0f4ff;
	}

	.input-section {
		margin-bottom: 15px;
	}

	.input-section label {
		display: block;
		margin-bottom: 8px;
		font-weight: bold;
		color: #333;
		font-size: 14px;
	}

	textarea {
		width: 100%;
		padding: 12px;
		border: 1px solid #ccc;
		border-radius: 4px;
		font-size: 14px;
		font-family: inherit;
		resize: vertical;
		transition: border-color 0.2s ease;
	}

	textarea:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
	}

	textarea:disabled {
		background: #f5f5f5;
		cursor: not-allowed;
	}

	.options {
		margin-bottom: 20px;
	}

	.checkbox-label {
		display: flex;
		align-items: center;
		font-size: 14px;
		color: #555;
		cursor: pointer;
	}

	.checkbox-label input[type='checkbox'] {
		margin-right: 8px;
		cursor: pointer;
	}

	.error-message {
		background: #fee;
		border: 1px solid #fcc;
		color: #c33;
		padding: 12px;
		border-radius: 4px;
		margin-bottom: 15px;
		font-size: 14px;
	}

	.success-message {
		background: #efe;
		border: 1px solid #cfc;
		color: #3a3;
		padding: 12px;
		border-radius: 4px;
		margin-bottom: 15px;
		font-size: 14px;
	}

	.generate-btn {
		width: 100%;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		padding: 14px 24px;
		border-radius: 6px;
		font-size: 16px;
		font-weight: bold;
		cursor: pointer;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
	}

	.generate-btn:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3);
	}

	.generate-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none;
	}

	.spinner {
		display: inline-block;
		width: 16px;
		height: 16px;
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	@media (max-width: 768px) {
		.example-buttons {
			flex-direction: column;
		}

		.example-btn {
			width: 100%;
			text-align: left;
		}
	}
</style>
