import type {ShortProps} from '../schema';

export const INTRO_S = 0.6;
export const OUTRO_S = 2.4;
const COUNT_UP_STEPS = 0.4;
const RANK_SMOOTH_S = 0.38;

const clamp01 = (x: number) => Math.min(1, Math.max(0, x));
export const easeOutCubic = (x: number) => 1 - Math.pow(1 - clamp01(x), 3);
export const easeInOutCubic = (x: number) => {
	const t = clamp01(x);
	return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
};

export type Timing = {
	duration: number;
	animStart: number;
	animEnd: number;
	stepDur: number;
	steps: number;
};

export const getTiming = (p: ShortProps): Timing => {
	const duration = p.durationSec;
	const animStart = INTRO_S;
	const animEnd = duration - OUTRO_S;
	const steps = p.steps.length;
	// Half a step of headroom so the last column is absorbed and counted up before the finale
	return {duration, animStart, animEnd, steps, stepDur: (animEnd - animStart) / (steps + 0.5)};
};

/** Continuous step progress: column k reaches the absorb line at s = k + 1. */
export const progressAt = (t: number, tm: Timing) =>
	Math.min(tm.steps + 0.5, Math.max(0, (t - tm.animStart) / tm.stepDur));

export const absorbTime = (k: number, tm: Timing) => tm.animStart + (k + 1) * tm.stepDur;

export const valuesAt = (p: ShortProps, s: number): Record<string, number> => {
	const out: Record<string, number> = {};
	for (const e of p.entities) {
		let v = 0;
		p.steps.forEach((step, k) => {
			v += (step.values[e.id] ?? 0) * easeOutCubic((s - (k + 1)) / COUNT_UP_STEPS);
		});
		out[e.id] = v;
	}
	return out;
};

/** Discrete order: highest value first, "others" always last, ties keep input order. */
export const ranksFor = (p: ShortProps, values: Record<string, number>): Record<string, number> => {
	const order = p.entities
		.map((e, i) => ({e, i}))
		.sort((a, b) => {
			if (!!a.e.others !== !!b.e.others) return a.e.others ? 1 : -1;
			const dv = (values[b.e.id] ?? 0) - (values[a.e.id] ?? 0);
			return Math.abs(dv) > 1e-6 ? dv : a.i - b.i;
		});
	const r: Record<string, number> = {};
	order.forEach((o, idx) => (r[o.e.id] = idx));
	return r;
};

/** Smooth row slot (fractional rank) via a weighted look-back over discrete ranks — deterministic per frame. */
export const smoothRanksAt = (p: ShortProps, t: number, tm: Timing): Record<string, number> => {
	const samples = 12;
	const acc: Record<string, number> = {};
	let wsum = 0;
	for (let i = 0; i < samples; i++) {
		const back = (i / (samples - 1)) * RANK_SMOOTH_S;
		const w = 1 - i / samples;
		const r = ranksFor(p, valuesAt(p, progressAt(t - back, tm)));
		for (const id in r) acc[id] = (acc[id] ?? 0) + r[id] * w;
		wsum += w;
	}
	for (const id in acc) acc[id] = easeInOutSlot(acc[id] / wsum);
	return acc;
};

// Keeps slots crisp near integers so rows settle firmly between swaps
const easeInOutSlot = (x: number) => {
	const base = Math.floor(x);
	return base + easeInOutCubic(x - base);
};

export type SfxEvent = {t: number; kind: 'pop' | 'whoosh' | 'tick' | 'impact' | 'win' | 'swoosh'; entity?: string};

export const buildEvents = (p: ShortProps, fps: number, popDelay = 0): SfxEvent[] => {
	const tm = getTiming(p);
	const ev: SfxEvent[] = [{t: 0.05, kind: 'swoosh'}];
	p.steps.forEach((step, k) => {
		const t = absorbTime(k, tm);
		const gained = Object.values(step.values).some((v) => v > 0);
		ev.push({t: t - tm.stepDur * 0.5, kind: 'tick'});
		if (gained) ev.push({t: t + popDelay, kind: 'pop'});
	});
	let prev = ranksFor(p, valuesAt(p, 0));
	for (let f = 1; f < tm.animEnd * fps + COUNT_UP_STEPS * tm.stepDur * fps; f++) {
		const t = f / fps;
		const r = ranksFor(p, valuesAt(p, progressAt(t, tm)));
		for (const id in r) {
			if (r[id] < prev[id]) {
				const last = ev.filter((e) => e.kind === 'whoosh').pop();
				if (!last || t - last.t > 0.3) ev.push({t, kind: 'whoosh', entity: id});
				break;
			}
		}
		prev = r;
	}
	ev.push({t: tm.animEnd + 0.15, kind: 'impact'}, {t: tm.animEnd + 0.3, kind: 'win'});
	return ev.sort((a, b) => a.t - b.t);
};

export const leaderAtEnd = (p: ShortProps) => {
	const r = ranksFor(p, valuesAt(p, p.steps.length + 1));
	return Object.keys(r).find((id) => r[id] === 0)!;
};
