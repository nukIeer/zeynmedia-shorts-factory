import React from 'react';
import {CHART_BOTTOM, CHART_TOP, TICK_END_X, xOfValue, type Layout} from '../engine/layout';
import {formatTick, type Domain} from '../engine/scale';
import {fonts} from '../fonts';
import type {Theme} from '../theme/themes';

export const Axis: React.FC<{
	layout: Layout;
	domain: Domain;
	theme: Theme;
	format: 'int' | 'compact';
	opacity: number;
}> = ({layout, domain, theme, format, opacity}) => {
	const x0 = layout.axisX;
	const xEnd = layout.scaleEnd;
	const xOf = (v: number) => xOfValue(layout, domain, v);
	const top = CHART_TOP - 30;
	return (
		<div style={{position: 'absolute', inset: 0, opacity}}>
			{domain.ticks.map((v) => {
				const x = xOf(v);
				const edge = Math.min(1, (x - x0 + 20) / 60, (xEnd + 30 - x) / 60);
				return (
					<React.Fragment key={v}>
						<div
							style={{
								position: 'absolute',
								left: x,
								top,
								width: 2,
								height: CHART_BOTTOM - top,
								background: 'linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.16) 15%, rgba(255,255,255,0.16) 85%, rgba(255,255,255,0) 100%)',
								opacity: Math.max(0, edge),
							}}
						/>
						<div
							style={{
								position: 'absolute',
								left: x - 60,
								width: 120,
								top: CHART_BOTTOM + 36,
								textAlign: 'center',
								fontFamily: fonts.number,
								fontSize: 36,
								color: 'rgba(255,255,255,0.72)',
								opacity: Math.max(0, edge),
							}}
						>
							{formatTick(v, format)}
						</div>
					</React.Fragment>
				);
			})}
			<div
				style={{
					position: 'absolute',
					left: layout.axisX - 3,
					top: top - 20,
					width: 6,
					height: CHART_BOTTOM - top + (theme.lAxis ? 26 : 40),
					background: theme.lAxis
						? '#ffffff'
						: 'linear-gradient(180deg, rgba(255,255,255,0) 0%, #ffffff 12%, #ffffff 88%, rgba(255,255,255,0) 100%)',
					boxShadow: `0 0 16px 2px ${theme.glow}`,
					borderRadius: 3,
				}}
			/>
			{theme.lAxis ? (
				<div
					style={{
						position: 'absolute',
						left: layout.axisX - 3,
						top: CHART_BOTTOM + 6,
						width: TICK_END_X + 40 - layout.axisX,
						height: 6,
						background: 'linear-gradient(90deg, #ffffff 0%, #ffffff 80%, rgba(255,255,255,0) 100%)',
						boxShadow: `0 0 16px 2px ${theme.glow}`,
						borderRadius: 3,
					}}
				/>
			) : null}
		</div>
	);
};
