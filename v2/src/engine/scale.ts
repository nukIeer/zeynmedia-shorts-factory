const niceStep = (span: number, targetTicks: number) => {
	const raw = span / targetTicks;
	const mag = Math.pow(10, Math.floor(Math.log10(Math.max(raw, 1e-9))));
	const n = raw / mag;
	const m = n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10;
	return Math.max(m * mag, 1);
};

export type Domain = {min: number; max: number; ticks: number[]};

/** Axis domain follows the data; "zoom" starts above zero when bars are close (Goals Per Year style). */
export const domainFor = (values: number[], zoom: boolean): Domain => {
	const hi = Math.max(1, ...values);
	const lo = Math.min(...values);
	let min = 0;
	if (zoom && lo > hi * 0.6) min = lo - (hi - lo) * 0.9 - hi * 0.04;
	const max = hi + (hi - min) * 0.35;
	const step = niceStep(max - min, 7);
	const ticks: number[] = [];
	for (let v = Math.ceil(min / step) * step; v <= max + 1e-9; v += step) ticks.push(v);
	return {min, max, ticks};
};

export const formatValue = (v: number, mode: 'int' | 'compact') => {
	if (mode === 'compact') {
		if (v >= 1e9) return `${(v / 1e9).toFixed(1)}B`;
		if (v >= 1e6) return `${(v / 1e6).toFixed(1)}M`;
		if (v >= 1e3) return `${(v / 1e3).toFixed(1)}K`;
		return `${Math.round(v)}`;
	}
	return `${Math.round(v)}`;
};

export const formatTick = (v: number, mode: 'int' | 'compact') =>
	mode === 'compact' ? formatValue(v, 'compact').replace('.0', '') : `${Math.round(v)}`;
