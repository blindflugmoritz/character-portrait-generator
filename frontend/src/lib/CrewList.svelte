<script>
	import { LAYERS, COLOR_PALETTES, getAssetPath } from './assetData.js';

	export let crew = [];
	export let selectedIndex = 0;
	export let onSelect = (index) => {};
	export let onDelete = (index) => {};
	export let onAdd = () => {};

	// Generate thumbnail for a crew member
	async function generateThumbnail(member, canvasElement) {
		const ctx = canvasElement.getContext('2d');
		const size = 100;

		ctx.clearRect(0, 0, size, size);

		// Get colors
		const skinColor =
			COLOR_PALETTES.Skin[member.character?.colorIndices?.Skin ?? 2]?.hex ??
			COLOR_PALETTES.Skin[2].hex;
		const hairColor =
			COLOR_PALETTES.Hair[member.character?.colorIndices?.Hair ?? 3]?.hex ??
			COLOR_PALETTES.Hair[3].hex;
		const eyeColor =
			COLOR_PALETTES.Eye[member.character?.colorIndices?.Eye ?? 2]?.hex ??
			COLOR_PALETTES.Eye[2].hex;
		const accessoryColor =
			COLOR_PALETTES.Accessory[member.character?.colorIndices?.Accessory ?? 1]?.hex ??
			COLOR_PALETTES.Accessory[1].hex;

		// Sort layers by ID (back to front)
		const sortedLayers = Object.entries(LAYERS).sort((a, b) => b[1].id - a[1].id);

		for (const [layerName, layerInfo] of sortedLayers) {
			const partData = member.character?.parts?.[layerName];

			if (!partData || partData.index === -1 || partData.variant === -1) {
				continue;
			}

			// Skip mouth if moustache is present
			if (layerName === 'Mouth') {
				const moustache = member.character?.parts?.Moustache;
				if (moustache && moustache.index !== -1) {
					continue;
				}
			}

			const assetPath = getAssetPath(layerName, partData.index, partData.variant);
			if (assetPath) {
				try {
					const img = await loadImageAsync(assetPath);
					if (img) {
						// Apply color tinting
						let renderImg = img;

						if (layerInfo.useSkinColor) {
							renderImg = applyColorTint(img, skinColor);
						} else if (layerInfo.useHairColor) {
							renderImg = applyColorTint(img, hairColor);
						} else if (layerInfo.useEyeColor) {
							renderImg = applyColorTint(img, eyeColor);
						} else if (layerInfo.useAccessoryColor) {
							renderImg = applyColorTint(img, accessoryColor);
						}

						const scale = Math.min(size / renderImg.width, size / renderImg.height);
						const scaledWidth = renderImg.width * scale;
						const scaledHeight = renderImg.height * scale;
						const x = (size - scaledWidth) / 2;
						const y = (size - scaledHeight) / 2;

						ctx.drawImage(renderImg, x, y, scaledWidth, scaledHeight);
					}
				} catch (err) {
					console.warn(`Failed to render layer ${layerName}:`, err);
				}
			}
		}
	}

	function loadImageAsync(src) {
		return new Promise((resolve) => {
			const img = new Image();
			img.onload = () => resolve(img);
			img.onerror = () => resolve(null);
			img.src = src;
		});
	}

	function applyColorTint(img, hexColor) {
		const tempCanvas = document.createElement('canvas');
		tempCanvas.width = img.width;
		tempCanvas.height = img.height;
		const tempCtx = tempCanvas.getContext('2d');

		tempCtx.drawImage(img, 0, 0);
		tempCtx.globalCompositeOperation = 'multiply';
		tempCtx.fillStyle = hexColor;
		tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
		tempCtx.globalCompositeOperation = 'destination-in';
		tempCtx.drawImage(img, 0, 0);

		return tempCanvas;
	}

	// Re-render thumbnails when crew changes
	let thumbnailCanvases = [];
	$: if (crew.length > 0 && thumbnailCanvases.length > 0) {
		crew.forEach((member, index) => {
			if (thumbnailCanvases[index]) {
				generateThumbnail(member, thumbnailCanvases[index]);
			}
		});
	}
</script>

<div class="crew-list-container">
	<div class="crew-header">
		<h3>Crew Members ({crew.length})</h3>
		<button class="add-btn" on:click={onAdd} title="Add new crew member"> + New Member </button>
	</div>

	<div class="crew-grid">
		{#each crew as member, index}
			<div
				class="crew-card"
				class:selected={index === selectedIndex}
				on:click={() => onSelect(index)}
				on:keydown={(e) => e.key === 'Enter' && onSelect(index)}
				role="button"
				tabindex="0"
			>
				<canvas
					bind:this={thumbnailCanvases[index]}
					width="100"
					height="100"
					class="crew-thumbnail"
				/>
				<div class="crew-info">
					<div class="crew-name">
						{member.metadata?.FirstName || 'Unnamed'}
						{member.metadata?.LastName || ''}
					</div>
					<div class="crew-role">{member.metadata?.Role || member.metadata?.Job || 'No Role'}</div>
				</div>
				{#if crew.length > 1}
					<button
						class="delete-btn"
						on:click|stopPropagation={() => onDelete(index)}
						title="Delete crew member"
					>
						×
					</button>
				{/if}
			</div>
		{/each}
	</div>
</div>

<style>
	.crew-list-container {
		background: white;
		border: 2px solid #333;
		border-radius: 8px;
		padding: 15px;
		margin-bottom: 20px;
	}

	.crew-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 15px;
		padding-bottom: 10px;
		border-bottom: 2px solid #333;
	}

	.crew-header h3 {
		margin: 0;
		color: #333;
		font-size: 18px;
	}

	.add-btn {
		background: #4caf50;
		color: white;
		border: none;
		padding: 8px 16px;
		border-radius: 5px;
		cursor: pointer;
		font-size: 14px;
		font-weight: bold;
		transition: all 0.2s ease;
	}

	.add-btn:hover {
		background: #45a049;
		transform: translateY(-1px);
	}

	.crew-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
		gap: 15px;
		max-height: 300px;
		overflow-y: auto;
	}

	.crew-card {
		position: relative;
		border: 2px solid #ddd;
		border-radius: 8px;
		padding: 10px;
		cursor: pointer;
		transition: all 0.2s ease;
		background: white;
	}

	.crew-card:hover {
		border-color: #667eea;
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	}

	.crew-card.selected {
		border-color: #667eea;
		border-width: 3px;
		background: #f0f4ff;
	}

	.crew-thumbnail {
		width: 100px;
		height: 100px;
		display: block;
		margin: 0 auto 8px;
		border-radius: 4px;
		background: #f5f5f5;
		image-rendering: pixelated;
		image-rendering: -moz-crisp-edges;
		image-rendering: crisp-edges;
	}

	.crew-info {
		text-align: center;
	}

	.crew-name {
		font-weight: bold;
		color: #333;
		font-size: 13px;
		margin-bottom: 3px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.crew-role {
		color: #666;
		font-size: 11px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.delete-btn {
		position: absolute;
		top: 5px;
		right: 5px;
		background: #f44336;
		color: white;
		border: none;
		width: 24px;
		height: 24px;
		border-radius: 50%;
		cursor: pointer;
		font-size: 18px;
		line-height: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		opacity: 0;
		transition: opacity 0.2s ease;
	}

	.crew-card:hover .delete-btn {
		opacity: 1;
	}

	.delete-btn:hover {
		background: #d32f2f;
	}

	@media (max-width: 768px) {
		.crew-grid {
			grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
			gap: 10px;
		}

		.crew-thumbnail {
			width: 80px;
			height: 80px;
		}
	}
</style>
