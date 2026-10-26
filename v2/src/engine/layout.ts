import type {TemplateId} from '../schema';

export const W = 1080;
export const H = 1920;
export const CHART_TOP = 530;
// Bottom ~15% stays clear: YouTube Shorts overlays the channel name, title and buttons there
export const CHART_BOTTOM = 1440;
export const TICK_END_X = 1010;

export type Layout = {
	axisX: number;
	flagX: number;
	tagW: number;
	pitch: number;
	firstRowY: number;
	boxH: number;
	minBoxW: number;
		portrait: number;
	absorbX: number;
	deltaSize: number;
	scaleEnd: number; // x where the axis maximum sits; the right side stays free for the step columns
};

const AXIS_X: Record<TemplateId, number> = {bar: 108, navy: 196, box: 214, diamond: 232, grid: 250};
// Columns travel the whole chart and are absorbed at the axis, like the L-line in Zeynel's studio
const ABSORB_OFFSET = 14;
const SCALE_END: Record<TemplateId, number> = {bar: 880, navy: 760, box: 800, diamond: 810, grid: 780};

export const layoutFor = (template: TemplateId, rows: number): Layout => {
	const usable = CHART_BOTTOM - CHART_TOP;
	const pitch = Math.min(330, usable / rows);
	const boxH = Math.min(190, pitch * 0.7);
	const delta = template === 'navy' || template === 'box' || template === 'diamond';
	return {
		axisX: AXIS_X[template],
		flagX: AXIS_X[template] - 82,
		tagW: template === 'bar' ? 0 : Math.max(42, boxH * 0.32),
		pitch,
		firstRowY: CHART_TOP + (usable - rows * pitch) / 2 + pitch / 2,
		boxH,
		minBoxW: template === 'bar' ? 150 : boxH * 1.05,
		portrait: template === 'grid' ? pitch * 0.92 : Math.min(delta ? 210 : 240, pitch * 0.86),
		absorbX: AXIS_X[template] + ABSORB_OFFSET,
		deltaSize: Math.min(124, pitch * 0.5),
		scaleEnd: SCALE_END[template],
	};
};

/** Value -> x on the shared axis; box right edges and tick marks both use this so bars stay true to the numbers. */
export const xOfValue = (layout: Layout, domain: {min: number; max: number}, v: number) =>
	layout.axisX + ((v - domain.min) / (domain.max - domain.min)) * (layout.scaleEnd - layout.axisX);
