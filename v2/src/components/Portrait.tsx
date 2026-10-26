import React from 'react';
import {Img} from 'remotion';
import {asset} from '../asset';
import {fonts} from '../fonts';
import type {Entity} from '../schema';
import type {Theme} from '../theme/themes';

const initials = (name: string) =>
	name
		.split(/\s+/)
		.map((w) => w[0])
		.join('')
		.slice(0, 3)
		.toUpperCase();

const Badge: React.FC<{src: string; size: number; round?: boolean}> = ({src, size, round}) => (
	<div
		style={{
			width: size,
			height: size,
			borderRadius: round ? '50%' : size * 0.22,
			background: '#ffffff',
			boxShadow: '0 4px 10px rgba(0,0,0,0.35)',
			display: 'flex',
			alignItems: 'center',
			justifyContent: 'center',
			overflow: 'hidden',
		}}
	>
		<Img src={asset(src)} style={{width: '84%', height: '84%', objectFit: 'contain'}} />
	</div>
);

export const Portrait: React.FC<{entity: Entity; theme: Theme; size: number; ring: string; pulse: number}> = ({
	entity,
	theme,
	size,
	ring,
	pulse,
}) => {
	// Only transparent cutouts can spill out of the frame without showing a photo rectangle
	const cutout = !!entity.image && /\.png($|\?)|^data:image\/png/i.test(entity.image);
	const pop = cutout ? 1.28 : 1;
	// Clubs without a player photo show their crest big inside the frame instead of as a corner badge
	const crest = !entity.image && entity.badge ? entity.badge : undefined;
	const badges = [crest ? undefined : entity.badge, theme.flags === 'badge' ? entity.flag : undefined].filter(Boolean) as string[];
	const glow = pulse > 0 ? `0 0 ${30 * pulse}px ${12 * pulse}px rgba(255,255,255,${0.6 * pulse})` : '0 8px 20px rgba(0,0,0,0.35)';

	if (theme.portrait === 'logo') {
		return (
			<div
				style={{
					width: size,
					height: size,
					borderRadius: '50%',
					background: 'radial-gradient(circle, #ffffff 0%, #f1e6ff 100%)',
					border: `${Math.max(4, size * 0.04)}px solid #ffffff`,
					boxShadow: `0 0 0 ${Math.max(3, size * 0.04)}px rgba(170,90,255,0.7), ${glow}`,
					display: 'flex',
					alignItems: 'center',
					justifyContent: 'center',
					overflow: 'hidden',
				}}
			>
				{entity.badge || entity.image ? (
					<Img src={asset((entity.badge || entity.image)!)} style={{width: '88%', height: '88%', objectFit: 'contain'}} />
				) : entity.flag ? (
					<Img src={asset(entity.flag)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
				) : (
					<span style={{fontFamily: fonts.number, fontSize: size * 0.4, color: '#6d28d9'}}>{initials(entity.name)}</span>
				)}
			</div>
		);
	}

	const diamond = theme.portrait === 'diamond';
	const frameStyle: React.CSSProperties = diamond
		? {
				position: 'absolute',
				left: size * 0.12,
				top: size * 0.12,
				width: size * 0.76,
				height: size * 0.76,
				transform: 'rotate(45deg)',
				borderRadius: size * 0.08,
				background: 'linear-gradient(135deg, #bfe0ff 0%, #4f8cff 100%)',
				border: `${size * 0.035}px solid #ffffff`,
				boxShadow: `0 0 24px rgba(160,200,255,0.9), ${glow}`,
			}
		: {
				position: 'absolute',
				inset: 0,
				borderRadius: '50%',
				background: `radial-gradient(circle at 50% 35%, ${ring} 0%, ${ring} 55%, rgba(0,0,0,0.35) 100%)`,
				border: `${Math.max(5, size * 0.03)}px solid #ffffff`,
				boxShadow: glow,
			};

	// Cutouts are head-and-torso shots: zoom so the face fills the frame like SKILLER's portraits
	const zoom = cutout ? 1.75 : 1;
	const headTop = -size * (pop - 1);
	const imgStyle = (top: number): React.CSSProperties => ({
		position: 'absolute',
		left: (size * (1 - zoom)) / 2,
		top,
		width: size * zoom,
		height: cutout ? size * zoom : size,
		objectFit: cutout ? 'contain' : 'cover',
		objectPosition: 'top center',
	});
	const shape = diamond ? 'polygon(50% 4%, 96% 50%, 50% 96%, 4% 50%)' : 'circle(48.5% at 50% 50%)';

	return (
		<div style={{position: 'relative', width: size, height: size}}>
			<div style={frameStyle} />
			{entity.image ? (
				<>
					{/* body inside the frame */}
					<div style={{position: 'absolute', inset: 0, clipPath: shape}}>
						<Img src={asset(entity.image)} style={imgStyle(cutout ? headTop : 0)} />
					</div>
					{/* head popping out above the frame */}
					{cutout ? (
						<div style={{position: 'absolute', left: 0, top: headTop, width: size, height: size * 0.5 - headTop, overflow: 'hidden'}}>
							<Img src={asset(entity.image)} style={imgStyle(0)} />
						</div>
					) : null}
				</>
			) : crest ? (
				<div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', clipPath: shape}}>
					<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(circle, #ffffff 0%, #e8eeff 100%)'}} />
					<Img src={asset(crest)} style={{position: 'relative', width: diamond ? '58%' : '74%', height: diamond ? '58%' : '74%', objectFit: 'contain'}} />
				</div>
			) : (
				<div
					style={{
						position: 'absolute',
						inset: 0,
						display: 'flex',
						alignItems: 'center',
						justifyContent: 'center',
						fontFamily: fonts.number,
						fontSize: size * 0.38,
						color: '#ffffff',
					}}
				>
					{initials(entity.name)}
				</div>
			)}
			{badges.length ? (
				<div style={{position: 'absolute', right: -size * 0.36, bottom: size * 0.02, display: 'flex', flexDirection: 'column', gap: size * 0.04}}>
					{badges.map((b) => (
						<Badge key={b} src={b} size={size * 0.38} />
					))}
				</div>
			) : null}
		</div>
	);
};
