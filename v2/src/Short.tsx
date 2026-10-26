import React, {useMemo} from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {Axis} from './components/Axis';
import {Background} from './components/Background';
import {Columns} from './components/Columns';
import {Confetti, Crown, Flash, Sparks, type Burst} from './components/Effects';
import {Header} from './components/Header';
import {Row} from './components/Row';
import {Sound} from './components/Sound';
import {layoutFor} from './engine/layout';
import {domainFor, formatValue} from './engine/scale';
import {
	absorbTime,
	buildEvents,
	easeOutCubic,
	getTiming,
	leaderAtEnd,
	progressAt,
	smoothRanksAt,
	valuesAt,
} from './engine/timeline';
import {fonts} from './fonts';
import type {ShortProps} from './schema';
import {themes} from './theme/themes';

const FLASH_S = 0.32;
const FLY_S_STEPS = 0.28;

export const Short: React.FC<ShortProps> = (p) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const t = frame / fps;
	const theme = themes[p.template];
	const layout = layoutFor(p.template, p.entities.length);
	const tm = getTiming(p);
	const flies = theme.delta !== 'none' && theme.delta !== 'grid';
	const events = useMemo(() => buildEvents(p, fps, flies ? FLY_S_STEPS * tm.stepDur : 0), [p, fps, flies, tm.stepDur]);
	const leader = useMemo(() => leaderAtEnd(p), [p]);

	const s = progressAt(t, tm);
	const values = valuesAt(p, s);
	const slots = smoothRanksAt(p, t, tm);
	const realValues = p.entities.filter((e) => !e.others).map((e) => values[e.id]);
	const domain = domainFor(realValues, theme.zoomScale);
	const ratio = (v: number) => Math.max(0, Math.min(1, (v - domain.min) / (domain.max - domain.min)));

	const rowY: Record<string, number> = {};
	const boxW: Record<string, number> = {};
	const boxRight: Record<string, number> = {};
	for (const e of p.entities) {
		rowY[e.id] = layout.firstRowY + slots[e.id] * layout.pitch;
		boxW[e.id] = e.others ? layout.minBoxW * 1.35 : layout.minBoxW + ratio(values[e.id]) * layout.barSpan;
		boxRight[e.id] = layout.axisX + 3 + boxW[e.id];
	}

	// Gain moments per entity: the bubble lands FLY_S_STEPS after the column reaches the absorb line
	const gains = p.steps.flatMap((step, k) =>
		p.entities
			.filter((e) => (step.values[e.id] ?? 0) > 0 && !e.others)
			.map((e) => ({id: e.id, t: absorbTime(k, tm) + (flies ? FLY_S_STEPS * tm.stepDur : 0)})),
	);
	const bursts: Burst[] = gains.map((g, i) => ({t: g.t, x: boxRight[g.id] - 40, y: rowY[g.id], seed: `${g.id}-${i}`}));
	const overtakes = events.filter((e) => e.kind === 'whoosh');

	const outroStart = tm.animEnd + 0.15;
	const winnerK = easeOutCubic((t - outroStart) / 0.4);
	const shakeAge = Math.min(...overtakes.map((o) => (t >= o.t ? t - o.t : 99)), outroStart <= t ? t - outroStart : 99);
	const shake = shakeAge < 0.28 ? (1 - shakeAge / 0.28) * 9 : 0;
	const camScale = 1 + (1 - easeOutCubic(t / 0.6)) * 0.06 + winnerK * 0.03;
	const flash = Math.max(1 - t / 0.25, (t - (tm.duration - 0.22)) / 0.22, 0);

	return (
		<AbsoluteFill style={{background: '#000', overflow: 'hidden', fontFamily: fonts.title}}>
			<AbsoluteFill
				style={{
					transform: `translate(${Math.sin(t * 90) * shake}px, ${Math.cos(t * 77) * shake}px) scale(${camScale})`,
				}}
			>
				<Background theme={theme} brand={p.brand} />
				<Header title={p.title} subtitle={p.subtitle} theme={theme} />
				<Axis layout={layout} domain={domain} theme={theme} format={p.valueFormat} opacity={easeOutCubic(t / 0.5)} />
				{theme.delta === 'grid' ? <Columns p={p} theme={theme} layout={layout} s={s} rowY={rowY} boxRight={boxRight} t={t} /> : null}
				{[...p.entities]
					.map((e, i) => ({e, i}))
					.sort((a, b) => slots[b.e.id] - slots[a.e.id])
					.map(({e, i}) => {
						const lastGain = gains.filter((g) => g.id === e.id && g.t <= t).pop();
						const gAge = lastGain ? t - lastGain.t : 99;
						const gainK = gAge < FLASH_S ? 1 - gAge / FLASH_S : 0;
						const over = overtakes.filter((o) => o.entity === e.id && o.t <= t).pop();
						const oAge = over ? t - over.t : 99;
						const overK = oAge < 0.35 ? Math.sin((oAge / 0.35) * Math.PI) : 0;
						const isWinner = e.id === leader;
						return (
							<Row
								key={e.id}
								entity={e}
								index={i}
								theme={theme}
								layout={layout}
								y={rowY[e.id]}
								boxW={boxW[e.id]}
								label={e.others ? 'OTHERS' : formatValue(values[e.id], p.valueFormat)}
								fx={{
									flash: Math.max(gainK, overK * 0.6),
									punch: gainK * 0.05 + overK * 0.07 + (isWinner ? winnerK * 0.04 : 0),
									winner: isWinner ? winnerK * (0.75 + 0.25 * Math.sin(t * 10)) : 0,
									enter: easeOutCubic((t - 0.08 * slots[e.id]) / 0.45),
								}}
							/>
						);
					})}
				{theme.delta !== 'grid' ? <Columns p={p} theme={theme} layout={layout} s={s} rowY={rowY} boxRight={boxRight} t={t} /> : null}
				<Sparks bursts={bursts} t={t} />
				<Crown
					x={theme.portrait === 'logo' ? boxRight[leader] + layout.portrait * 0.15 : boxRight[leader] + layout.tagW + layout.portrait * 0.3}
					y={rowY[leader] - layout.portrait * (theme.portrait === 'logo' ? 0.55 : 0.85)}
					k={winnerK}
				/>
				<Confetti start={outroStart} t={t} />
				<div
					style={{
						position: 'absolute',
						bottom: 175,
						left: 0,
						right: 0,
						textAlign: 'center',
						fontFamily: fonts.title,
						fontStyle: 'italic',
						fontWeight: 900,
						fontSize: 66,
						letterSpacing: 1,
						color: '#ffffff',
						textShadow: '0 4px 14px rgba(0,0,0,0.25)',
					}}
				>
					{p.brand}
				</div>
			</AbsoluteFill>
			<Flash opacity={flash * 0.85} />
			<Sound events={events} sfx={p.sfx} sfxVolume={p.sfxVolume} music={p.music} musicStart={p.musicStart} musicVolume={p.musicVolume} />
		</AbsoluteFill>
	);
};
