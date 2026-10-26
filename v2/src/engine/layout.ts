import type {TemplateId} from '../schema';

export const W = 1080;
export const H = 1920;
export const CHART_TOP = 610;
export const CHART_BOTTOM = 1410;
export const TICK_END_X = 1010;

export type Layout = {
	axisX: number;
	flagX: number;
	tagW: number;
	pitch: number;
	firstRowY: number;
	boxH: number;
	minBoxW: number;
	barSpan: number;
	portrait: number;
	absorbX: number;
	deltaSize: number;
};

const AXIS_X: Record<TemplateId, number> = {bar: 108, navy: 196, box: 214, diamond: 232, grid: 250};
const ABSORB_X: Record<TemplateId, number> = {bar: 560, navy: 900, box: 930, diamond: 960, grid: 500};

export const layoutFor = (template: TemplateId, rows: number): Layout => {
	const usable = CHART_BOTTOM - CHART_TOP;
	const pitch = Math.min(330, usable / rows);
	const boxH = Math.min(178, pitch * 0.6);
	const delta = template === 'navy' || template === 'box' || template === 'diamond';
	return {
		axisX: AXIS_X[template],
		flagX: AXIS_X[template] - 82,
		tagW: template === 'bar' ? 0 : Math.max(34, boxH * 0.3),
		pitch,
		firstRowY: CHART_TOP + (usable - rows * pitch) / 2 + pitch / 2,
		boxH,
		minBoxW: template === 'bar' ? 150 : boxH * 1.55,
		barSpan: template === 'bar' ? 540 : template === 'grid' ? 120 : delta ? 210 : 300,
		portrait: template === 'grid' ? boxH * 1.08 : Math.min(delta ? 200 : 232, pitch * 0.78),
		absorbX: ABSORB_X[template],
		deltaSize: Math.min(118, pitch * 0.42),
	};
};
