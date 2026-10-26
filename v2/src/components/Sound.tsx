import React from 'react';
import {Audio, Sequence, interpolate, staticFile, useVideoConfig} from 'remotion';
import type {SfxEvent} from '../engine/timeline';

type Layer = {files: string[]; volume: number};

// 808 / sub layers (scripts/make_bass_sfx.py) carry the hits under phonk; the bright layers keep the sparkle
const SFX: Record<SfxEvent['kind'], Layer[]> = {
	swoosh: [{files: ['bass_riser.mp3'], volume: 0.9}],
	tick: [{files: ['deep_tick.mp3'], volume: 0.55}],
	pop: [{files: ['bass_hit.mp3'], volume: 0.95}, {files: ['win_3.mp3', 'win_1.mp3'], volume: 0.25}],
	whoosh: [{files: ['sub_whoosh.mp3'], volume: 1}],
	impact: [{files: ['sub_boom.mp3'], volume: 1}],
	win: [{files: ['bass_drop.mp3'], volume: 0.9}, {files: ['win_4.mp3'], volume: 0.45}],
};

export const Sound: React.FC<{
	events: SfxEvent[];
	sfx: boolean;
	sfxVolume: number;
	music?: string;
	musicStart: number;
	musicVolume: number;
}> = ({events, sfx, sfxVolume, music, musicStart, musicVolume}) => {
	const {fps, durationInFrames} = useVideoConfig();
	return (
		<>
			{music ? (
				<Audio
					src={music.startsWith('http') ? music : staticFile(music)}
					trimBefore={Math.round(musicStart * fps)}
					volume={(f) =>
						musicVolume *
						interpolate(f, [0, 8, durationInFrames - 20, durationInFrames], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})
					}
				/>
			) : null}
			{sfx
				? events.flatMap((e, i) =>
						SFX[e.kind].map((layer, j) => (
							<Sequence key={`${i}-${j}`} from={Math.max(0, Math.round(e.t * fps))} durationInFrames={Math.round(2.5 * fps)} layout="none">
								<Audio src={staticFile(`sfx/${layer.files[i % layer.files.length]}`)} volume={layer.volume * sfxVolume} />
							</Sequence>
						)),
				  )
				: null}
		</>
	);
};
