import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {fonts} from '../fonts';
import type {Theme} from '../theme/themes';

const Watermark: React.FC<{text: string; top: number; drift: number}> = ({text, top, drift}) => (
	<div
		style={{
			position: 'absolute',
			top,
			left: -120 + drift,
			whiteSpace: 'nowrap',
			fontFamily: fonts.title,
			fontStyle: 'italic',
			fontWeight: 900,
			fontSize: 300,
			letterSpacing: -6,
			color: 'rgba(255,255,255,0.075)',
			lineHeight: 1,
		}}
	>
		{text}
	</div>
);

export const Background: React.FC<{theme: Theme; brand: string}> = ({theme, brand}) => {
	const frame = useCurrentFrame();
	const drift = Math.sin(frame / 90) * 18;
	return (
		<AbsoluteFill style={{background: theme.background, overflow: 'hidden'}}>
			{/* diagonal light streaks */}
			<div
				style={{
					position: 'absolute',
					inset: -200,
					background:
						'linear-gradient(115deg, rgba(255,255,255,0) 35%, rgba(255,255,255,0.09) 41%, rgba(255,255,255,0) 47%, rgba(255,255,255,0) 58%, rgba(255,255,255,0.06) 62%, rgba(255,255,255,0) 66%)',
					transform: `translateX(${drift * 2}px)`,
				}}
			/>
			<div
				style={{
					position: 'absolute',
					right: -260,
					top: 420,
					width: 900,
					height: 1100,
					background: 'linear-gradient(115deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0) 100%)',
					transform: `skewX(-18deg) translateY(${drift}px)`,
				}}
			/>
			<Watermark text={brand} top={-110} drift={drift} />
			<Watermark text={brand} top={1690} drift={-drift} />
			<AbsoluteFill style={{background: 'radial-gradient(120% 80% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.28) 100%)'}} />
		</AbsoluteFill>
	);
};
