<script>
	import { Card } from '$lib/components/ui/card';

	let { onPhotoAnalyzed } = $props();

	let analyzing = $state(false);
	let error = $state(null);
	let dragActive = $state(false);

	async function handleFileSelect(event) {
		const file = event.target?.files?.[0] || event.dataTransfer?.files?.[0];
		if (!file) return;

		error = null;

		const validTypes = ['image/jpeg', 'image/png', 'image/heic', 'image/webp'];
		if (!validTypes.includes(file.type)) {
			error = 'Invalid file type. Please upload JPEG, PNG, HEIC, or WebP';
			return;
		}

		if (file.size > 2 * 1024 * 1024) {
			error = 'File too large. Maximum size is 2MB';
			return;
		}

		await analyzePhoto(file);
	}

	async function analyzePhoto(file) {
		analyzing = true;
		error = null;

		try {
			const reader = new FileReader();
			const base64 = await new Promise((resolve, reject) => {
				reader.onload = () => resolve(reader.result.split(',')[1]);
				reader.onerror = reject;
				reader.readAsDataURL(file);
			});

			console.log('Uploading photo for analysis...');

			const apiUrl = 'https://blindflugstudios.pythonanywhere.com';
			const response = await fetch(`${apiUrl}/api/analyze-photo`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					image: base64,
					mimeType: file.type
				})
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.error || 'Analysis failed');
			}

			const result = await response.json();
			console.log('Photo analyzed successfully!');

			onPhotoAnalyzed(result.character);
		} catch (err) {
			console.error('Photo analysis error:', err);
			error = err.message || 'Failed to analyze photo. Please try again.';
		} finally {
			analyzing = false;
		}
	}

	function handleDragOver(event) {
		event.preventDefault();
		dragActive = true;
	}

	function handleDragLeave() {
		dragActive = false;
	}

	function handleDrop(event) {
		event.preventDefault();
		dragActive = false;
		handleFileSelect(event);
	}
</script>

<Card.Root class="p-6">
	<h3 class="text-xl font-bold mb-2">📸 Generate from Photo</h3>
	<p class="text-sm text-muted-foreground mb-4">
		Upload a portrait photo to automatically generate a matching character
	</p>

	{#if analyzing}
		<div class="text-center p-10 bg-muted/50 rounded-lg">
			<div
				class="w-12 h-12 border-4 border-muted-foreground/20 border-t-foreground rounded-full animate-spin mx-auto mb-5"
			></div>
			<p class="font-medium mb-1">Analyzing photo...</p>
			<small class="text-muted-foreground">This may take a few seconds</small>
		</div>
	{:else}
		<div
			class="border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition-all hover:border-primary hover:bg-accent/50"
			class:border-primary={dragActive}
			class:bg-accent={dragActive}
			class:scale-105={dragActive}
			ondrop={handleDrop}
			ondragover={handleDragOver}
			ondragleave={handleDragLeave}
			role="button"
			tabindex="0"
		>
			<input
				type="file"
				accept="image/jpeg,image/png,image/heic,image/webp"
				onchange={handleFileSelect}
				id="photo-upload"
				class="hidden"
			/>
			<label for="photo-upload" class="cursor-pointer block">
				<div class="text-5xl mb-3">📷</div>
				<p class="font-medium mb-2">Click to upload or drag & drop</p>
				<small class="text-muted-foreground">JPEG, PNG, HEIC, WebP (max 2MB)</small>
			</label>
		</div>
	{/if}

	{#if error}
		<div class="bg-destructive/10 border border-destructive text-destructive p-3 rounded mt-4 text-sm border-l-4">
			<strong>Error:</strong> {error}
		</div>
	{/if}
</Card.Root>
