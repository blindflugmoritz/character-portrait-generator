<script>
	export let onPhotoAnalyzed = (character) => {};

	let analyzing = false;
	let error = null;
	let dragActive = false;

	async function handleFileSelect(event) {
		const file = event.target?.files?.[0] || event.dataTransfer?.files?.[0];
		if (!file) return;

		error = null;

		// Validate file type
		const validTypes = ['image/jpeg', 'image/png', 'image/heic', 'image/webp'];
		if (!validTypes.includes(file.type)) {
			error = 'Invalid file type. Please upload JPEG, PNG, HEIC, or WebP';
			return;
		}

		// Validate file size (2MB max)
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
			// Convert to base64
			const reader = new FileReader();
			const base64 = await new Promise((resolve, reject) => {
				reader.onload = () => resolve(reader.result.split(',')[1]);
				reader.onerror = reject;
				reader.readAsDataURL(file);
			});

			console.log('Uploading photo for analysis...');

			// Call Django backend API
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

			// Pass generated character to parent
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

<div class="upload-container">
	<h3>📸 Generate from Photo</h3>
	<p class="description">Upload a portrait photo to automatically generate a matching character</p>

	{#if analyzing}
		<div class="analyzing">
			<div class="spinner"></div>
			<p>Analyzing photo...</p>
			<small>This may take a few seconds</small>
		</div>
	{:else}
		<div
			class="drop-zone"
			class:drag-active={dragActive}
			on:drop={handleDrop}
			on:dragover={handleDragOver}
			on:dragleave={handleDragLeave}
			role="button"
			tabindex="0"
		>
			<input
				type="file"
				accept="image/jpeg,image/png,image/heic,image/webp"
				on:change={handleFileSelect}
				id="photo-upload"
				style="display: none;"
			/>
			<label for="photo-upload">
				<div class="upload-icon">📷</div>
				<p class="upload-text">Click to upload or drag & drop</p>
				<small class="upload-hint">JPEG, PNG, HEIC, WebP (max 2MB)</small>
			</label>
		</div>
	{/if}

	{#if error}
		<div class="error">
			<strong>Error:</strong> {error}
		</div>
	{/if}
</div>

<style>
	.upload-container {
		background: white;
		border: 2px solid #333;
		border-radius: 8px;
		padding: 20px;
		margin-bottom: 20px;
	}

	.upload-container h3 {
		margin: 0 0 8px 0;
		color: #333;
		font-size: 20px;
	}

	.description {
		margin: 0 0 15px 0;
		color: #666;
		font-size: 14px;
	}

	.drop-zone {
		border: 2px dashed #ccc;
		border-radius: 8px;
		padding: 40px;
		text-align: center;
		cursor: pointer;
		transition: all 0.3s ease;
		background: #fafafa;
	}

	.drop-zone:hover,
	.drop-zone.drag-active {
		border-color: #4caf50;
		background: #f0f9f0;
		transform: scale(1.02);
	}

	.drop-zone label {
		cursor: pointer;
		display: block;
	}

	.upload-icon {
		font-size: 48px;
		margin-bottom: 10px;
	}

	.upload-text {
		margin: 10px 0;
		color: #333;
		font-size: 16px;
		font-weight: 500;
	}

	.upload-hint {
		color: #999;
		font-size: 13px;
	}

	.analyzing {
		text-align: center;
		padding: 40px;
		background: #f0f9f0;
		border-radius: 8px;
	}

	.spinner {
		width: 50px;
		height: 50px;
		border: 5px solid #e0e0e0;
		border-top: 5px solid #4caf50;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin: 0 auto 20px;
	}

	@keyframes spin {
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
	}

	.analyzing p {
		margin: 0 0 5px 0;
		color: #333;
		font-size: 16px;
		font-weight: 500;
	}

	.analyzing small {
		color: #666;
		font-size: 13px;
	}

	.error {
		color: #d32f2f;
		padding: 12px;
		background: #ffebee;
		border-radius: 4px;
		margin-top: 15px;
		border-left: 4px solid #d32f2f;
	}

	.error strong {
		font-weight: 600;
	}
</style>
