<script>
	import { Button } from '$lib/components/ui/button';
	import { LAYERS, COLOR_PALETTES, getAssetPath } from './assetData.js';

	let { crew = $bindable([]), selectedIndex = $bindable(0), onSelect, onDelete, onAdd, onNavigateToPostcard } = $props();

	// Generate thumbnail for a crew member
	async function generateThumbnail(member, canvasElement) {
		const ctx = canvasElement.getContext('2d');
		const size = 256;

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

			const assetPath = getAssetPath(layerName, partData.index, partData.variant, member.character?.gender || 'Male');
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
	let thumbnailCanvases = $state([]);

	// Watch for any changes to the crew array and re-render ALL thumbnails
	$effect(() => {
		// Access crew to make effect reactive to any changes
		const currentCrew = crew;

		// Re-render all thumbnails whenever crew changes
		if (thumbnailCanvases.length > 0) {
			currentCrew.forEach((member, index) => {
				if (thumbnailCanvases[index]) {
					generateThumbnail(member, thumbnailCanvases[index]);
				}
			});
		}
	});

	// Function to manually update a specific thumbnail (called by parent)
	function updateThumbnail(index) {
		if (thumbnailCanvases[index] && crew[index]) {
			generateThumbnail(crew[index], thumbnailCanvases[index]);
		}
	}
</script>

<div class="bg-card text-card-foreground flex flex-col gap-6 rounded-xl border py-6 shadow-sm p-4 mb-5">
	<div class="flex justify-between items-center mb-4 pb-3 border-b-2">
		<h3 class="text-lg font-semibold">Crew Members ({crew.length})</h3>
		<div class="flex gap-2">
			<Button onclick={onAdd} variant="default" size="sm"> + New Member </Button>
			<Button onclick={onNavigateToPostcard} variant="secondary" size="sm"> 🖼️ Create Postcard </Button>
		</div>
	</div>

	<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 max-h-[300px] overflow-y-auto">
		{#each crew as member, index}
			<div
				class="relative border-2 rounded-lg p-2 cursor-pointer transition-all hover:border-primary hover:-translate-y-1 hover:shadow-md group"
				class:border-primary={index === selectedIndex}
				class:border-3={index === selectedIndex}
				class:bg-accent={index === selectedIndex}
				onclick={() => onSelect(index)}
				onkeydown={(e) => e.key === 'Enter' && onSelect(index)}
				role="button"
				tabindex="0"
			>
				<canvas
					bind:this={thumbnailCanvases[index]}
					width="256"
					height="256"
					class="w-full h-auto block mb-2 rounded bg-muted"
					style="image-rendering: pixelated; image-rendering: -moz-crisp-edges; image-rendering: crisp-edges;"
				/>
				<div class="text-center">
					<div class="font-bold text-xs mb-1 overflow-hidden text-ellipsis whitespace-nowrap">
						{member.metadata?.FirstName || 'Unnamed'}
						{member.metadata?.LastName || ''}
					</div>
					<div class="text-[10px] text-muted-foreground overflow-hidden text-ellipsis whitespace-nowrap">
						{member.metadata?.Role || member.metadata?.Job || 'No Role'}
					</div>
				</div>
				{#if crew.length > 1}
					<Button
						onclick={(e) => {
							e.stopPropagation();
							onDelete(index);
						}}
						variant="destructive"
						size="icon"
						class="absolute top-1 right-1 w-6 h-6 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
					>
						×
					</Button>
				{/if}
			</div>
		{/each}
	</div>
</div>
