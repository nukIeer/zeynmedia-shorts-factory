import React from 'react';
import {AbsoluteFill, random} from 'remotion';
import {CrownIcon} from './Icons';

export type Burst = {t: number; x: number; y: number; seed: string};

const SPARK_LIFE = 0.5;
const SPARK_COLORS = ['#ffffff', '#ffe066', '#7dff6b', '#9be7ff'];

export const Sparks: React.FC<{bursts: Burst[]; t: number}> = ({bursts, t}) => (
	<AbsoluteFill style={{pointerEvents: 'none'}}>
		{bursts.map((b) => {
			const age = t - b.t;
			if (age < 0 || age > SPARK_LIFE) return null;
			const k = age / SPARK_LIFE;
			return Array.from({length: 14}).map((_, i) => {
				const ang = random(`${b.seed}-a${i}`) * Math.PI * 2;
				const dist = (1 - Math.pow(1 - k, 3)) * (80 + random(`${b.seed}-d${i}`) * 110);
				const size = 6 + random(`${b.seed}-s${i}`) * 10;
				return (
					<div
						key={`${b.seed}-${i}`}
						style={{
							position: 'absolute',
							left: b.x + Math.cos(ang) * dist - size / 2,
							top: b.y + Math.sin(ang) * dist - size / 2,
							width: size,
							height: size,
							borderRadius: '50%',
							background: SPARK_COLORS[i % SPARK_COLORS.length],
							boxShadow: `0 0 12px ${SPARK_COLORS[i % SPARK_COLORS.length]}`,
							opacity: 1 - k,
						}}
					/>
				);
			});
		})}
		{bursts.map((b) => {
			const age = t - b.t;
			if (age < 0 || age > 0.35) return null;
			const k = age / 0.35;
			return (
				<div
					key={`${b.seed}-ring`}
					style={{
						position: 'absolute',
						left: b.x - 120 * k,
						top: b.y - 120 * k,
						width: 240 * k,
						height: 240 * k,
						borderRadius: '50%',
						border: `${6 * (1 - k)}px solid rgba(255,255,255,${1 - k})`,
					}}
				/>
			);
		})}
	</AbsoluteFill>
);

const CONFETTI_COLORS = ['#ffd23f', '#ff4d6d', '#4dd2ff', '#7dff6b', '#ffffff', '#b46bff'];

export const Confetti: React.FC<{start: number; t: number}> = ({start, t}) => {
	const age = t - start;
	if (age < 0) return null;
	return (
		<AbsoluteFill style={{pointerEvents: 'none'}}>
			{Array.from({length: 90}).map((_, i) => {
				const x0 = random(`cx${i}`) * 1080;
				const vx = (random(`cvx${i}`) - 0.5) * 500;
				const vy = -900 - random(`cvy${i}`) * 700;
				const g = 2200;
				const x = x0 + vx * age;
				const y = 1500 + vy * age + 0.5 * g * age * age;
				const rot = age * (300 + random(`cr${i}`) * 600);
				const w = 14 + random(`cw${i}`) * 14;
				if (y > 2000) return null;
				return (
					<div
						key={i}
						style={{
							position: 'absolute',
							left: x,
							top: y,
							width: w,
							height: w * 0.55,
							background: CONFETTI_COLORS[i % CONFETTI_COLORS.length],
							transform: `rotate(${rot}deg) rotateX(${rot * 1.7}deg)`,
							borderRadius: 2,
						}}
					/>
				);
			})}
		</AbsoluteFill>
	);
};

export const Crown: React.FC<{x: number; y: number; k: number}> = ({x, y, k}) => {
	if (k <= 0) return null;
	const pop = k < 1 ? 1 + Math.sin(k * Math.PI) * 0.35 : 1;
	return (
		<div style={{position: 'absolute', left: x - 60, top: y - 70, transform: `scale(${pop * Math.min(1, k * 1.6)}) rotate(-12deg)`, filter: 'drop-shadow(0 0 18px rgba(255,210,63,0.9))'}}>
			<CrownIcon size={120} />
		</div>
	);
};

export const Flash: React.FC<{opacity: number}> = ({opacity}) =>
	opacity > 0 ? <AbsoluteFill style={{background: '#ffffff', opacity, pointerEvents: 'none'}} /> : null;
