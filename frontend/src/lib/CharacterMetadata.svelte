<script>
	import { Card } from '$lib/components/ui/card';
	import { Label } from '$lib/components/ui/label';
	import { Input } from '$lib/components/ui/input';
	import { Textarea } from '$lib/components/ui/textarea';
	import * as Select from '$lib/components/ui/select';

	let { metadata = $bindable() } = $props();

	// Initialize metadata if empty
	if (!metadata.Id) {
		// Generate UUID with fallback for SSR
		let id;
		try {
			id = crypto.randomUUID();
		} catch (e) {
			id = `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
		}

		metadata = {
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

	const genders = ['Male', 'Female'];
	const classes = ['AirCrew', 'BaseCrew'];
	const jobs = ['None', 'AAFCook', 'FieldMechanic', 'FieldEngineer', 'RAFMedic', 'AAFLabour'];
	const roles = [
		'None',
		'Pilot',
		'Gunner',
		'Navigator',
		'BombAimer',
		'FlightEngineer',
		'RadioOperator'
	];

	function updateField(field, value) {
		metadata = { ...metadata, [field]: value };
	}

	function updateBiography(value) {
		metadata = { ...metadata, Biography: { ...metadata.Biography, en: value } };
	}

	function updateSkillRank(skill, value) {
		const rank = Math.max(0, Math.min(6, parseInt(value) || 0));
		metadata = {
			...metadata,
			SkillRanks: { ...metadata.SkillRanks, [skill]: rank }
		};
	}

	// Handle class change - reset Job or Role accordingly
	function handleClassChange(newClass) {
		if (newClass === 'BaseCrew') {
			metadata = { ...metadata, Class: newClass, Role: 'None' };
		} else {
			metadata = { ...metadata, Class: newClass, Job: 'None' };
		}
	}
</script>

<Card.Root class="p-6">
	<h2 class="text-2xl font-bold mb-6 pb-4 border-b">Character Information</h2>

	<div class="space-y-6">
		<!-- Basic Info -->
		<div class="space-y-4 p-4 bg-muted/50 rounded-lg border">
			<h3 class="text-lg font-semibold mb-3 pb-2 border-b">Basic Info</h3>

			<div class="space-y-2">
				<Label for="creatorName">Creator Name</Label>
				<Input
					id="creatorName"
					type="text"
					value={metadata.CreatorName}
					oninput={(e) => updateField('CreatorName', e.target.value)}
					placeholder="Your name"
				/>
			</div>

			<div class="space-y-2">
				<Label for="firstName">First Name</Label>
				<Input
					id="firstName"
					type="text"
					value={metadata.FirstName}
					oninput={(e) => updateField('FirstName', e.target.value)}
					placeholder="Character's first name"
				/>
			</div>

			<div class="space-y-2">
				<Label for="lastName">Last Name</Label>
				<Input
					id="lastName"
					type="text"
					value={metadata.LastName}
					oninput={(e) => updateField('LastName', e.target.value)}
					placeholder="Character's last name"
				/>
			</div>

			{#if metadata.Class === 'AirCrew'}
				<div class="space-y-2">
					<Label for="nickname">Nickname</Label>
					<Input
						id="nickname"
						type="text"
						value={metadata.Nickname}
						oninput={(e) => updateField('Nickname', e.target.value)}
						placeholder="e.g., Chief, Ace, etc."
					/>
				</div>
			{/if}

			<div class="space-y-2">
				<Label for="birthDate">Birth Date</Label>
				<Input
					id="birthDate"
					type="date"
					value={metadata.BirthDate}
					max="1921-12-31"
					oninput={(e) => updateField('BirthDate', e.target.value)}
				/>
				<p class="text-xs text-muted-foreground">Must be before 1922</p>
			</div>

			<div class="space-y-2">
				<Label>Gender</Label>
				<Select.Root
					selected={{ value: metadata.Gender, label: metadata.Gender }}
					onSelectedChange={(v) => v && updateField('Gender', v.value)}
				>
					<Select.Trigger>
						<Select.Value />
					</Select.Trigger>
					<Select.Content>
						{#each genders as gender}
							<Select.Item value={gender}>{gender}</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
			</div>
		</div>

		<!-- Role & Class -->
		<div class="space-y-4 p-4 bg-muted/50 rounded-lg border">
			<h3 class="text-lg font-semibold mb-3 pb-2 border-b">Role & Class</h3>

			<div class="space-y-2">
				<Label>Class</Label>
				<Select.Root
					selected={{ value: metadata.Class, label: metadata.Class }}
					onSelectedChange={(v) => v && handleClassChange(v.value)}
				>
					<Select.Trigger>
						<Select.Value />
					</Select.Trigger>
					<Select.Content>
						{#each classes as cls}
							<Select.Item value={cls}>{cls}</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
			</div>

			{#if metadata.Class === 'BaseCrew'}
				<div class="space-y-2">
					<Label>Job</Label>
					<Select.Root
						selected={{ value: metadata.Job, label: metadata.Job.replace(/([A-Z])/g, ' $1').trim() }}
						onSelectedChange={(v) => v && updateField('Job', v.value)}
					>
						<Select.Trigger>
							<Select.Value />
						</Select.Trigger>
						<Select.Content>
							{#each jobs as job}
								<Select.Item value={job}>{job.replace(/([A-Z])/g, ' $1').trim()}</Select.Item>
							{/each}
						</Select.Content>
					</Select.Root>
				</div>
			{:else}
				<div class="space-y-2">
					<Label>Role</Label>
					<Select.Root
						selected={{ value: metadata.Role, label: metadata.Role.replace(/([A-Z])/g, ' $1').trim() }}
						onSelectedChange={(v) => v && updateField('Role', v.value)}
					>
						<Select.Trigger>
							<Select.Value />
						</Select.Trigger>
						<Select.Content>
							{#each roles as role}
								<Select.Item value={role}>{role.replace(/([A-Z])/g, ' $1').trim()}</Select.Item>
							{/each}
						</Select.Content>
					</Select.Root>
				</div>
			{/if}
		</div>

		<!-- Biography -->
		<div class="space-y-4 p-4 bg-muted/50 rounded-lg border">
			<h3 class="text-lg font-semibold mb-3 pb-2 border-b">Biography</h3>
			<Textarea
				value={metadata.Biography?.en || ''}
				oninput={(e) => updateBiography(e.target.value)}
				placeholder="Write the character's background story..."
				rows={4}
			/>
		</div>

		<!-- Skill Ranks -->
		{#if metadata.Class === 'AirCrew'}
			<div class="space-y-4 p-4 bg-muted/50 rounded-lg border">
				<h3 class="text-lg font-semibold mb-3 pb-2 border-b">Skill Ranks (0-6)</h3>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					{#each Object.entries(metadata.SkillRanks) as [skill, rank]}
						<div class="space-y-2">
							<Label for="skill-{skill}">{skill}</Label>
							<div class="flex items-center gap-3">
								<Input
									id="skill-{skill}"
									type="number"
									min="0"
									max="6"
									value={rank}
									oninput={(e) => updateSkillRank(skill, e.target.value)}
									class="w-20 text-center"
								/>
								<input
									type="range"
									min="0"
									max="6"
									value={rank}
									oninput={(e) => updateSkillRank(skill, e.target.value)}
									class="flex-1"
								/>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	</div>
</Card.Root>
