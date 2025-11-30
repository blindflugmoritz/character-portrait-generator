<script>
	import { onMount } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Tabs from '$lib/components/ui/tabs';
	import PortraitCanvas from '$lib/PortraitCanvas.svelte';
	import CharacterControls from '$lib/CharacterControls.svelte';
	import CharacterMetadata from '$lib/CharacterMetadata.svelte';
	import CrewList from '$lib/CrewList.svelte';
	import CrewGenerator from '$lib/CrewGenerator.svelte';
	import PhotoUpload from '$lib/PhotoUpload.svelte';
	import { createDefaultCharacter, generateRandomCharacter } from '$lib/assetData.js';

	// Crew management
	let crew = $state([]);
	let selectedCrewIndex = $state(0);

	// Current crew member being edited
	let character = $state(createDefaultCharacter());
	let metadata = $state(createDefaultMetadata());

	let portraitCanvas;
	let activeTab = $state('appearance');

	// Initialize crew array
	crew = [createCrewMember()];
	character = crew[0].character;
	metadata = crew[0].metadata;

	// Initialize with one crew member
	onMount(() => {
		// Check for data version - clear if old version
		const DATA_VERSION = '2.0';
		const savedVersion = localStorage.getItem('crewDataVersion');

		if (savedVersion !== DATA_VERSION) {
			console.log('Data version mismatch, clearing localStorage');
			localStorage.removeItem('crew');
			localStorage.setItem('crewDataVersion', DATA_VERSION);
			return;
		}

		// Try to load from localStorage
		try {
			const saved = localStorage.getItem('crew');
			if (saved) {
				const parsed = JSON.parse(saved);
				if (parsed && Array.isArray(parsed) && parsed.length > 0) {
					crew = parsed;
					character = crew[selectedCrewIndex].character;
					metadata = crew[selectedCrewIndex].metadata;
				}
			}
		} catch (e) {
			console.error('Failed to load crew from localStorage:', e);
		}
	});

	// Save to localStorage whenever crew changes (browser only)
	function saveCrew() {
		if (typeof window !== 'undefined' && crew.length > 0) {
			try {
				localStorage.setItem('crew', JSON.stringify(crew));
			} catch (e) {
				console.error('Failed to save crew to localStorage:', e);
			}
		}
	}

	// Update crew member when character or metadata changes
	$effect(() => {
		if (crew[selectedCrewIndex]) {
			crew[selectedCrewIndex].character = character;
			crew[selectedCrewIndex].metadata = metadata;
			saveCrew();
		}
	});

	function createDefaultMetadata() {
		// Generate UUID with fallback for SSR
		let id;
		try {
			id = crypto.randomUUID();
		} catch (e) {
			// Fallback for SSR: simple random ID
			id = `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
		}

		return {
			Id: id,
			CreatorName: '',
			FirstName: '',
			LastName: '',
			Nickname: '',
			BirthDate: '1920-01-01',
			Gender: 'Male',
			Class: 'AirCrew',
			Job: 'None',
			Role: 'Pilot',
			Biography: { en: '' },
			SkillRanks: {
				Flying: 0,
				Shooting: 0,
				Bombing: 0,
				Endurance: 0,
				Engineering: 0,
				Navigating: 0
			}
		};
	}

	function createCrewMember() {
		return {
			character: createDefaultCharacter(),
			metadata: createDefaultMetadata()
		};
	}

	// Crew management functions
	function addCrewMember() {
		const newMember = createCrewMember();
		crew = [...crew, newMember];
		selectedCrewIndex = crew.length - 1;
		character = newMember.character;
		metadata = newMember.metadata;
	}

	function deleteCrewMember(index) {
		if (crew.length <= 1) {
			alert('You must have at least one crew member!');
			return;
		}

		crew = crew.filter((_, i) => i !== index);

		// Adjust selected index if needed
		if (selectedCrewIndex >= crew.length) {
			selectedCrewIndex = crew.length - 1;
		}

		// Load the character and metadata of the newly selected member
		character = crew[selectedCrewIndex].character;
		metadata = crew[selectedCrewIndex].metadata;
	}

	function selectCrewMember(index) {
		selectedCrewIndex = index;
		character = crew[index].character;
		metadata = crew[index].metadata;
	}

	// Handle AI-generated crew
	function handleCrewGenerated(generatedCrew, replaceExisting) {
		if (replaceExisting) {
			crew = generatedCrew;
			selectedCrewIndex = 0;
		} else {
			crew = [...crew, ...generatedCrew];
			// Don't change selection when adding to existing crew
		}

		// Load the selected crew member
		if (crew.length > 0) {
			character = crew[selectedCrewIndex].character;
			metadata = crew[selectedCrewIndex].metadata;
		}
	}

	// Handle photo-generated character
	function handlePhotoAnalyzed(generatedCharacter) {
		// Update current crew member's character
		character = generatedCharacter;
		crew[selectedCrewIndex].character = generatedCharacter;
	}

	// Export portrait as PNG
	function exportPortrait() {
		if (portraitCanvas) {
			const dataUrl = portraitCanvas.exportPortrait();
			const link = document.createElement('a');
			const fileName =
				metadata.FirstName && metadata.LastName
					? `${metadata.FirstName}_${metadata.LastName}.png`
					: 'character-portrait.png';
			link.download = fileName;
			link.href = dataUrl;
			link.click();
		}
	}

	// Export single character data as JSON
	function exportJSON() {
		const editorData = {
			BodyShapeIndex: character.bodyShapeIndex || 1,
			AccessoryColorIndex: character.colorIndices?.Accessory ?? 1,
			SkinColorIndex: character.colorIndices?.Skin ?? 2,
			HairColorIndex: character.colorIndices?.Hair ?? 3,
			EyeColorIndex: character.colorIndices?.Eye ?? 2
		};

		const partMapping = {
			AccessoryFront: 'Accessory',
			Blemish: 'Blemish',
			Nose: 'Nose',
			Eyebrows: 'Eyebrows',
			Eyes: 'Eyes',
			Moustache: 'Moustache',
			Beard: 'Beard',
			Mouth: 'Mouth',
			Hair: 'Hair',
			DetailUpper: 'Detail',
			Headshape: 'Headshape',
			Ears: 'Ears'
		};

		for (const [layerName, jsonKey] of Object.entries(partMapping)) {
			const part = character.parts[layerName] || { index: -1, variant: -1 };
			editorData[jsonKey] = {
				Index: part.index,
				Variant: part.variant
			};
		}

		const exportData = {
			...metadata,
			EditorData: editorData
		};

		const jsonStr = JSON.stringify(exportData, null, 2);
		const blob = new Blob([jsonStr], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const link = document.createElement('a');
		const fileName =
			metadata.FirstName && metadata.LastName
				? `${metadata.FirstName}_${metadata.LastName}.json`
				: 'character-data.json';
		link.download = fileName;
		link.href = url;
		link.click();
		URL.revokeObjectURL(url);
	}

	// Export entire crew as JSON array
	function exportCrewJSON() {
		const crewData = crew.map((member) => {
			const editorData = {
				BodyShapeIndex: member.character.bodyShapeIndex || 1,
				AccessoryColorIndex: member.character.colorIndices?.Accessory ?? 1,
				SkinColorIndex: member.character.colorIndices?.Skin ?? 2,
				HairColorIndex: member.character.colorIndices?.Hair ?? 3,
				EyeColorIndex: member.character.colorIndices?.Eye ?? 2
			};

			const partMapping = {
				AccessoryFront: 'Accessory',
				Blemish: 'Blemish',
				Nose: 'Nose',
				Eyebrows: 'Eyebrows',
				Eyes: 'Eyes',
				Moustache: 'Moustache',
				Beard: 'Beard',
				Mouth: 'Mouth',
				Hair: 'Hair',
				DetailUpper: 'Detail',
				Headshape: 'Headshape',
				Ears: 'Ears'
			};

			for (const [layerName, jsonKey] of Object.entries(partMapping)) {
				const part = member.character.parts[layerName] || { index: -1, variant: -1 };
				editorData[jsonKey] = {
					Index: part.index,
					Variant: part.variant
				};
			}

			return {
				...member.metadata,
				EditorData: editorData
			};
		});

		const jsonStr = JSON.stringify(crewData, null, 2);
		const blob = new Blob([jsonStr], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const link = document.createElement('a');
		link.download = 'crew-data.json';
		link.href = url;
		link.click();
		URL.revokeObjectURL(url);
	}

	// Import crew from JSON
	function importCrewJSON() {
		const input = document.createElement('input');
		input.type = 'file';
		input.accept = '.json';
		input.onchange = (e) => {
			const file = e.target.files[0];
			if (file) {
				const reader = new FileReader();
				reader.onload = (event) => {
					try {
						const importedData = JSON.parse(event.target.result);

						// Check if it's an array (crew) or single character
						const dataArray = Array.isArray(importedData) ? importedData : [importedData];

						// Convert imported data to internal format
						const importedCrew = dataArray.map((charData) => {
							const editorData = charData.EditorData || {};

							const character = {
								bodyShapeIndex: editorData.BodyShapeIndex ?? 1,
								colorIndices: {
									Skin: editorData.SkinColorIndex ?? 2,
									Hair: editorData.HairColorIndex ?? 3,
									Eye: editorData.EyeColorIndex ?? 2,
									Accessory: editorData.AccessoryColorIndex ?? 1
								},
								parts: {
									AccessoryFront: editorData.Accessory || { index: -1, variant: -1 },
									Blemish: editorData.Blemish || { index: -1, variant: -1 },
									Nose: editorData.Nose || { index: 0, variant: 0 },
									Eyebrows: editorData.Eyebrows || { index: 0, variant: 0 },
									Eyes: editorData.Eyes || { index: 0, variant: 0 },
									Moustache: editorData.Moustache || { index: -1, variant: -1 },
									Beard: editorData.Beard || { index: -1, variant: -1 },
									Mouth: editorData.Mouth || { index: 0, variant: 0 },
									Hair: editorData.Hair || { index: 0, variant: 0 },
									HairBack: { index: 4, variant: 0 },
									DetailUpper: editorData.Detail || { index: -1, variant: -1 },
									DetailLower: { index: -1, variant: -1 },
									Headshape: editorData.Headshape || { index: 0, variant: 0 },
									HeadAuxiliary: { index: -1, variant: -1 },
									Ears: editorData.Ears || { index: 0, variant: 0 },
									Body: { index: 0, variant: 0 },
									Clothes: { index: 0, variant: 0 },
									ClothesBack: { index: 0, variant: 0 }
								}
							};

							// Generate UUID with fallback
							let id = charData.Id;
							if (!id) {
								try {
									id = crypto.randomUUID();
								} catch (e) {
									id = `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
								}
							}

							const metadata = {
								Id: id,
								CreatorName: charData.CreatorName || '',
								FirstName: charData.FirstName || '',
								LastName: charData.LastName || '',
								Nickname: charData.Nickname || '',
								BirthDate: charData.BirthDate || '1920-01-01',
								Gender: charData.Gender || 'Male',
								Class: charData.Class || 'AirCrew',
								Job: charData.Job || 'None',
								Role: charData.Role || 'Pilot',
								Biography: charData.Biography || { en: '' },
								SkillRanks: charData.SkillRanks || {
									Flying: 0,
									Shooting: 0,
									Bombing: 0,
									Endurance: 0,
									Engineering: 0,
									Navigating: 0
								}
							};

							return { character, metadata };
						});

						crew = importedCrew;
						selectedCrewIndex = 0;
						alert(`Successfully imported ${importedCrew.length} crew member(s)!`);
					} catch (err) {
						alert('Failed to import crew data. Invalid JSON format.');
						console.error(err);
					}
				};
				reader.readAsText(file);
			}
		};
		input.click();
	}

	// Share portrait
	function sharePortrait() {
		if (portraitCanvas && navigator.share) {
			const dataUrl = portraitCanvas.exportPortrait();
			fetch(dataUrl)
				.then((res) => res.blob())
				.then((blob) => {
					const file = new File([blob], 'character-portrait.png', { type: 'image/png' });
					navigator.share({
						title: 'My Character Portrait',
						text: `Check out ${metadata.FirstName || 'my'} ${metadata.LastName || 'character'}!`,
						files: [file]
					});
				});
		} else if (navigator.clipboard && portraitCanvas) {
			const dataUrl = portraitCanvas.exportPortrait();
			fetch(dataUrl)
				.then((res) => res.blob())
				.then((blob) => {
					navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]);
					alert('Portrait copied to clipboard!');
				});
		}
	}
</script>

<svelte:head>
	<title>Crew Portrait Generator</title>
	<meta name="description" content="Create custom character portraits for your crew" />
</svelte:head>

<main class="min-h-screen p-5 bg-gradient-to-br from-blue-500 to-purple-600">
	<header class="text-center mb-8 text-white">
		<h1 class="text-5xl font-bold mb-3 drop-shadow-lg">Crew Portrait Generator</h1>
		<p class="text-xl opacity-90">Create and manage your entire crew with customizable portraits and metadata</p>
	</header>

	<div class="max-w-[1600px] mx-auto space-y-5">
		<!-- Crew List Section -->
		<CrewList
			bind:crew
			bind:selectedIndex={selectedCrewIndex}
			onSelect={selectCrewMember}
			onDelete={deleteCrewMember}
			onAdd={addCrewMember}
		/>

		<div class="grid grid-cols-1 lg:grid-cols-[auto_1fr] gap-8 items-start">
			<div class="flex flex-col items-center gap-4">
				<h3 class="text-white text-xl font-semibold px-5 py-2 bg-black/30 rounded-lg">
					Editing: {metadata.FirstName || 'Unnamed'} {metadata.LastName || ''}
				</h3>

				<PortraitCanvas bind:this={portraitCanvas} {character} canvasSize={512} />

				<div class="flex flex-wrap gap-2 justify-center">
					<Button onclick={exportPortrait} variant="default">💾 Download PNG</Button>
					<Button onclick={exportJSON} variant="secondary">📄 Export Character</Button>
					<Button onclick={sharePortrait} variant="outline">📤 Share</Button>
				</div>

				<div class="flex flex-wrap gap-2 justify-center">
					<Button onclick={exportCrewJSON} variant="default">📦 Export Crew</Button>
					<Button onclick={importCrewJSON} variant="secondary">📥 Import Crew</Button>
				</div>
			</div>

			<div class="min-w-0">
				<Tabs.Root value={activeTab} onValueChange={(v) => (activeTab = v)}>
					<Tabs.List class="grid w-full grid-cols-2">
						<Tabs.Trigger value="appearance">Appearance</Tabs.Trigger>
						<Tabs.Trigger value="info">Character Info</Tabs.Trigger>
					</Tabs.List>
					<Tabs.Content value="appearance">
						<CharacterControls bind:character />
					</Tabs.Content>
					<Tabs.Content value="info">
						<CharacterMetadata bind:metadata />
					</Tabs.Content>
				</Tabs.Root>
			</div>
		</div>

		<!-- AI Features at Bottom -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mt-5">
			<CrewGenerator onCrewGenerated={handleCrewGenerated} />
			<PhotoUpload onPhotoAnalyzed={handlePhotoAnalyzed} />
		</div>
	</div>

	<footer class="text-center mt-10 text-white/80">
		<p>Built with SvelteKit • {crew.length} crew member(s) • Advanced color system</p>
	</footer>
</main>
