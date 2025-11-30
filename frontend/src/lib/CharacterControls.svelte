<script>
	import { Button } from '$lib/components/ui/button';
	import { Card } from '$lib/components/ui/card';
	import { Label } from '$lib/components/ui/label';
	import * as Select from '$lib/components/ui/select';
	import {
		LAYERS,
		BODY_SHAPES,
		COLOR_PALETTES,
		getAvailableIndices,
		getAvailableVariants,
		getAssetFilename,
		generateRandomCharacter,
		createDefaultCharacter,
		CLOTHES_BACK_MAPPING,
		getMatchingHairBackIndices
	} from './assetData.js';
	import { spriteLabels } from './spriteLabels.js';

	let { character = $bindable() } = $props();

	// Initialize with default character if empty
	if (!character.parts) {
		character = createDefaultCharacter();
	}

	// Ensure gender exists
	if (!character.gender) {
		character.gender = 'Male';
	}

	// Randomize character
	function randomizeCharacter() {
		character = generateRandomCharacter(character.gender);
	}

	// Update gender - regenerate random character with new gender
	function updateGender(newGender) {
		console.log('Gender changed to:', newGender, '- generating new random character');
		character = generateRandomCharacter(newGender);
	}

	// Update part
	function updatePart(layerName, index, variant) {
		const newParts = {
			...character.parts,
			[layerName]: { index: parseInt(index), variant: parseInt(variant) }
		};

		// If setting Moustache to a value (not -1), clear Mouth
		if (layerName === 'Moustache' && parseInt(index) !== -1) {
			newParts.Mouth = { index: -1, variant: -1 };
		}

		// If setting Clothes, automatically set ClothesBack based on mapping
		if (layerName === 'Clothes') {
			const clothesIndex = parseInt(index);
			const clothesBackIndex = CLOTHES_BACK_MAPPING[clothesIndex];
			if (clothesBackIndex !== undefined) {
				newParts.ClothesBack = { index: clothesBackIndex, variant: 0 };
			}
		}

		// If setting Hair, update HairBack to match or clear if no match exists
		if (layerName === 'Hair') {
			const hairIndex = parseInt(index);
			if (hairIndex !== -1) {
				const matchingHairBackIndices = getMatchingHairBackIndices(hairIndex, character.gender);
				const currentHairBack = character.parts.HairBack?.index;

				// If current HairBack doesn't match new Hair, clear it or set to first matching
				if (!matchingHairBackIndices.includes(currentHairBack)) {
					if (matchingHairBackIndices.length > 0) {
						// Set to first matching HairBack
						newParts.HairBack = { index: matchingHairBackIndices[0], variant: 0 };
					} else {
						// No matching HairBack exists, clear it
						newParts.HairBack = { index: -1, variant: -1 };
					}
				}
			} else {
				// Hair removed, clear HairBack
				newParts.HairBack = { index: -1, variant: -1 };
			}
		}

		character = {
			...character,
			parts: newParts
		};
	}

	// Remove part (set to -1)
	function removePart(layerName) {
		character = {
			...character,
			parts: {
				...character.parts,
				[layerName]: { index: -1, variant: -1 }
			}
		};
	}

	// Update color
	function updateColor(colorType, colorIndex) {
		character = {
			...character,
			colorIndices: {
				...character.colorIndices,
				[colorType]: parseInt(colorIndex)
			}
		};
	}

	// Update body shape
	function updateBodyShape(shapeIndex) {
		character = {
			...character,
			bodyShapeIndex: parseInt(shapeIndex)
		};
	}

	// Get layers grouped by category
	let layersByCategory = $derived(
		Object.entries(LAYERS).reduce((acc, [name, layer]) => {
			if (!acc[layer.category]) {
				acc[layer.category] = [];
			}
			acc[layer.category].push({ name, ...layer });
			return acc;
		}, {})
	);

	// Sort categories with Background at the end
	let sortedCategories = $derived(
		Object.entries(layersByCategory).sort(([catA], [catB]) => {
			if (catA === 'Background') return 1;
			if (catB === 'Background') return -1;
			return 0;
		})
	);

	// Helper: Get sprite label from layer, index, variant
	function getSpriteLabel(layerName, index, variant) {
		// Try to get label without gender suffix first (base sprite name)
		const baseFilename = getAssetFilename(layerName, index, variant, 'Male');
		if (!baseFilename) return 'Unknown';

		const layer = LAYERS[layerName];
		const folder = layer.folder;

		// Look up label using base filename (labels are stored without _female suffix)
		return spriteLabels[folder]?.[baseFilename] || `${layerName} ${index}`;
	}
</script>

<Card.Root class="p-6">
	<div class="flex justify-between items-center mb-6">
		<h2 class="text-2xl font-bold">Character Customization</h2>
		<Button onclick={randomizeCharacter} variant="default">
			🎲 Randomize
		</Button>
	</div>

	<!-- Gender Selection -->
	<div class="mb-6">
		<Label>Gender</Label>
		<Select.Root
			selected={{ value: character.gender, label: character.gender }}
			onSelectedChange={(v) => v && updateGender(v.value)}
		>
			<Select.Trigger class="w-full">
				<Select.Value placeholder="Select gender" />
			</Select.Trigger>
			<Select.Content>
				<Select.Item value="Male">Male</Select.Item>
				<Select.Item value="Female">Female</Select.Item>
			</Select.Content>
		</Select.Root>
	</div>

	<!-- Body Shape Selection -->
	<div class="mb-6">
		<Label>Body Shape</Label>
		<Select.Root
			selected={{ value: String(character.bodyShapeIndex), label: BODY_SHAPES.find(s => s.index === character.bodyShapeIndex)?.name || 'Average' }}
			onSelectedChange={(v) => v && updateBodyShape(v.value)}
		>
			<Select.Trigger class="w-full">
				<Select.Value placeholder="Select body shape" />
			</Select.Trigger>
			<Select.Content>
				{#each BODY_SHAPES as shape}
					<Select.Item value={String(shape.index)}>{shape.name}</Select.Item>
				{/each}
			</Select.Content>
		</Select.Root>
	</div>

	<!-- Color Selection -->
	<div class="mb-6">
		<Label class="text-lg font-semibold mb-3 block">Colors</Label>
		<div class="space-y-4">
			<!-- Skin Color -->
			<div class="flex items-center gap-3">
				<Label class="w-32">Skin Color</Label>
				<Select.Root
					selected={{ value: String(character.colorIndices?.Skin ?? 2), label: COLOR_PALETTES.Skin[character.colorIndices?.Skin ?? 2].name }}
					onSelectedChange={(v) => v && updateColor('Skin', v.value)}
				>
					<Select.Trigger class="flex-1">
						<Select.Value />
					</Select.Trigger>
					<Select.Content>
						{#each COLOR_PALETTES.Skin as color}
							<Select.Item value={String(color.index)}>{color.name}</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
				<div
					class="w-8 h-8 rounded border-2 border-gray-300"
					style="background-color: {COLOR_PALETTES.Skin[character.colorIndices?.Skin ?? 2].hex}"
				></div>
			</div>

			<!-- Hair Color -->
			<div class="flex items-center gap-3">
				<Label class="w-32">Hair Color</Label>
				<Select.Root
					selected={{ value: String(character.colorIndices?.Hair ?? 3), label: COLOR_PALETTES.Hair[character.colorIndices?.Hair ?? 3].name }}
					onSelectedChange={(v) => v && updateColor('Hair', v.value)}
				>
					<Select.Trigger class="flex-1">
						<Select.Value />
					</Select.Trigger>
					<Select.Content>
						{#each COLOR_PALETTES.Hair as color}
							<Select.Item value={String(color.index)}>{color.name}</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
				<div
					class="w-8 h-8 rounded border-2 border-gray-300"
					style="background-color: {COLOR_PALETTES.Hair[character.colorIndices?.Hair ?? 3].hex}"
				></div>
			</div>

			<!-- Eye Color -->
			<div class="flex items-center gap-3">
				<Label class="w-32">Eye Color</Label>
				<Select.Root
					selected={{ value: String(character.colorIndices?.Eye ?? 2), label: COLOR_PALETTES.Eye[character.colorIndices?.Eye ?? 2].name }}
					onSelectedChange={(v) => v && updateColor('Eye', v.value)}
				>
					<Select.Trigger class="flex-1">
						<Select.Value />
					</Select.Trigger>
					<Select.Content>
						{#each COLOR_PALETTES.Eye as color}
							<Select.Item value={String(color.index)}>{color.name}</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
				<div
					class="w-8 h-8 rounded border-2 border-gray-300"
					style="background-color: {COLOR_PALETTES.Eye[character.colorIndices?.Eye ?? 2].hex}"
				></div>
			</div>

			<!-- Accessory Color -->
			<div class="flex items-center gap-3">
				<Label class="w-32">Accessory Color</Label>
				<Select.Root
					selected={{ value: String(character.colorIndices?.Accessory ?? 1), label: COLOR_PALETTES.Accessory[character.colorIndices?.Accessory ?? 1].name }}
					onSelectedChange={(v) => v && updateColor('Accessory', v.value)}
				>
					<Select.Trigger class="flex-1">
						<Select.Value />
					</Select.Trigger>
					<Select.Content>
						{#each COLOR_PALETTES.Accessory as color}
							<Select.Item value={String(color.index)}>{color.name}</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
				<div
					class="w-8 h-8 rounded border-2 border-gray-300"
					style="background-color: {COLOR_PALETTES.Accessory[character.colorIndices?.Accessory ?? 1].hex}"
				></div>
			</div>
		</div>
	</div>

	<!-- Layer Controls by Category -->
	<div class="space-y-6">
		{#each sortedCategories as [categoryName, layers]}
			{@const hairIndex = character.parts?.Hair?.index}
			<div class="border rounded-lg p-4 bg-muted/50">
				<h3 class="text-lg font-semibold mb-4">{categoryName}</h3>
				<div class="space-y-4">
					{#each layers as layer}
						{@const baseIndices = getAvailableIndices(layer.name, character.gender)}
						{@const indices = layer.name === 'HairBack' && hairIndex !== -1 ? getMatchingHairBackIndices(hairIndex, character.gender) : baseIndices}
						{@const partData = character.parts?.[layer.name] || { index: -1, variant: -1 }}
						{@const variants = partData.index !== -1 ? getAvailableVariants(layer.name, partData.index, character.gender) : []}
						{@const hasMoustache = character.parts?.Moustache?.index !== -1}
						{@const isMouthDisabled = layer.name === 'Mouth' && hasMoustache}
						{@const isFemaleHiddenLayer = character.gender === 'Female' && (layer.name === 'Beard' || layer.name === 'Moustache')}

						{#if indices.length > 0 && !isFemaleHiddenLayer}
							<div class:opacity-50={isMouthDisabled}>
								<Label>
									{layer.name.replace(/([A-Z])/g, ' $1').trim()}
									{#if isMouthDisabled}
										<span class="text-xs text-muted-foreground">(disabled when moustache present)</span>
									{/if}
								</Label>
								<div class="flex gap-2 mt-2">
									<!-- Index selector -->
									<Select.Root
										selected={partData.index === -1 ? { value: '-1', label: 'None' } : { value: String(partData.index), label: getSpriteLabel(layer.name, partData.index, getAvailableVariants(layer.name, partData.index, character.gender)[0] || 0) }}
										onSelectedChange={(v) => {
											if (!v || isMouthDisabled) return;
											const newIndex = parseInt(v.value);
											if (newIndex === -1) {
												removePart(layer.name);
											} else {
												const availVariants = getAvailableVariants(layer.name, newIndex, character.gender);
												updatePart(layer.name, newIndex, availVariants[0] || 0);
											}
										}}
										disabled={isMouthDisabled}
									>
										<Select.Trigger class="flex-[2]">
											<Select.Value />
										</Select.Trigger>
										<Select.Content>
											{#if layer.canBeNone}
												<Select.Item value="-1">None</Select.Item>
											{/if}
											{#each indices as index}
												{@const firstVariant = getAvailableVariants(layer.name, index, character.gender)[0] || 0}
												<Select.Item value={String(index)}>{getSpriteLabel(layer.name, index, firstVariant)}</Select.Item>
											{/each}
										</Select.Content>
									</Select.Root>

									<!-- Variant selector (only show if index is selected AND has multiple variants) -->
									{#if partData.index !== -1 && variants.length > 1}
										<Select.Root
											selected={{ value: String(partData.variant), label: getSpriteLabel(layer.name, partData.index, partData.variant) }}
											onSelectedChange={(v) => v && !isMouthDisabled && updatePart(layer.name, partData.index, v.value)}
											disabled={isMouthDisabled}
										>
											<Select.Trigger class="flex-1">
												<Select.Value />
											</Select.Trigger>
											<Select.Content>
												{#each variants as variant}
													<Select.Item value={String(variant)}>{getSpriteLabel(layer.name, partData.index, variant)}</Select.Item>
												{/each}
											</Select.Content>
										</Select.Root>
									{/if}

									<!-- Remove button -->
									{#if layer.canBeNone && partData.index !== -1 && !isMouthDisabled}
										<Button onclick={() => removePart(layer.name)} variant="destructive" size="icon">
											✕
										</Button>
									{/if}
								</div>
							</div>
						{/if}
					{/each}
				</div>
			</div>
		{/each}
	</div>
</Card.Root>
