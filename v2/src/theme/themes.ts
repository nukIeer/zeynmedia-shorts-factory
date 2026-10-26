import type {TemplateId} from '../schema';

export type Theme = {
	background: string;
	glow: string;
	subtitleStyle: 'yellow' | 'box';
	subtitleBox: string;
	box: 'entity' | 'navy' | 'alt' | 'white';
	boxColor: string;
	boxAltColor: string;
	number: string;
	numberAlt: string;
	tag: string;
	tagText: string;
	tagSide: 'right' | 'left' | 'outside';
	portrait: 'circle' | 'diamond' | 'logo';
	delta: 'green' | 'navy' | 'diamond' | 'grid' | 'none';
	deltaTrack: string;
	flags: 'left' | 'badge';
	lAxis: boolean;
	columnSpacing: number;
	zoomScale: boolean;
};

export const themes: Record<TemplateId, Theme> = {
	// Ronaldo vs Messi — Goals Per Year
	bar: {
		background:
			'radial-gradient(120% 70% at 85% 15%, #8b5cf6 0%, rgba(139,92,246,0) 60%), linear-gradient(160deg, #3b4cf0 0%, #4f46e5 38%, #6d3df0 70%, #8f45e8 100%)',
		glow: 'rgba(196,181,253,0.55)',
		subtitleStyle: 'yellow',
		subtitleBox: 'transparent',
		box: 'entity',
		boxColor: '#e5484d',
		boxAltColor: '#7cc0f5',
		number: '#ffffff',
		numberAlt: '#ffffff',
		tag: 'transparent',
		tagText: '#ffffff',
		tagSide: 'outside',
		portrait: 'circle',
		delta: 'none',
		deltaTrack: '#3df04a',
		flags: 'badge',
		lAxis: false,
		columnSpacing: 620,
		zoomScale: true,
	},
	// R9 vs Neymar — Goals Per Age
	navy: {
		background:
			'radial-gradient(90% 55% at 50% 30%, #1d2c86 0%, rgba(29,44,134,0) 70%), linear-gradient(180deg, #121a5c 0%, #0c1347 45%, #080d33 100%)',
		glow: 'rgba(120,150,255,0.45)',
		subtitleStyle: 'box',
		subtitleBox: 'transparent',
		box: 'alt',
		boxColor: '#1a2a8c',
		boxAltColor: '#5470ff',
		number: '#ffffff',
		numberAlt: '#0b1240',
		tag: '#4361ee',
		tagText: '#0b1240',
		tagSide: 'right',
		portrait: 'circle',
		delta: 'green',
		deltaTrack: '#3df04a',
		flags: 'left',
		lAxis: false,
		columnSpacing: 640,
		zoomScale: false,
	},
	// Most Trophies Won / Instagram followers
	box: {
		background:
			'radial-gradient(100% 60% at 30% 20%, #3b82f6 0%, rgba(59,130,246,0) 65%), linear-gradient(165deg, #1d4ed8 0%, #1e5af0 45%, #1a3fd0 100%)',
		glow: 'rgba(191,219,254,0.55)',
		subtitleStyle: 'box',
		subtitleBox: '#0f1c63',
		box: 'navy',
		boxColor: '#0f1c63',
		boxAltColor: '#0f1c63',
		number: '#ffffff',
		numberAlt: '#ffffff',
		tag: '#1f46d6',
		tagText: '#ffffff',
		tagSide: 'right',
		portrait: 'circle',
		delta: 'navy',
		deltaTrack: 'rgba(15,28,99,0.9)',
		flags: 'left',
		lAxis: false,
		columnSpacing: 640,
		zoomScale: false,
	},
	// Buffon vs Casillas — Most Clean Sheets
	diamond: {
		background:
			'linear-gradient(125deg, rgba(255,255,255,0) 30%, rgba(255,255,255,0.10) 38%, rgba(255,255,255,0) 46%), radial-gradient(90% 60% at 60% 45%, #2f6bff 0%, #1240f5 45%, #0a2ad8 100%)',
		glow: 'rgba(191,219,254,0.7)',
		subtitleStyle: 'box',
		subtitleBox: '#0b2fb8',
		box: 'white',
		boxColor: '#ffffff',
		boxAltColor: '#ffffff',
		number: '#2e62ff',
		numberAlt: '#2e62ff',
		tag: '#0b2fb8',
		tagText: '#ffffff',
		tagSide: 'left',
		portrait: 'diamond',
		delta: 'diamond',
		deltaTrack: '#3df04a',
		flags: 'badge',
		lAxis: true,
		columnSpacing: 640,
		zoomScale: false,
	},
	// Champions League — All Winners
	grid: {
		background:
			'radial-gradient(80% 50% at 30% 25%, #c43cff 0%, rgba(196,60,255,0) 70%), linear-gradient(165deg, #9b1ff0 0%, #7a16dc 45%, #5a10c2 100%)',
		glow: 'rgba(233,213,255,0.65)',
		subtitleStyle: 'box',
		subtitleBox: '#5b14b8',
		box: 'white',
		boxColor: '#ffffff',
		boxAltColor: '#ffffff',
		number: '#8a1fe6',
		numberAlt: '#8a1fe6',
		tag: '#4b0f9c',
		tagText: '#ffffff',
		tagSide: 'left',
		portrait: 'logo',
		delta: 'grid',
		deltaTrack: '#3df04a',
		flags: 'badge',
		lAxis: true,
		columnSpacing: 300,
		zoomScale: false,
	},
};
