import React from 'react';
import {Audio, Sequence, interpolate, staticFile, useVideoConfig} from 'remotion';
import type {SfxEvent} from '../engine/timeline';

const SFX: Record<SfxEvent['kind'], {files: string[]; volume: number}> = {
	swoosh: {files: ['whoosh_4.mp3'], volume: 0.7},
	tick: {files: ['tick_1.mp3', 'tick_2.mp3'], volume: 0.35},
	pop: {files: ['win_3.mp3', 'win_1.mp3'], volume: 0.55},
	whoosh: {files: ['whoosh_1.mp3', 'whoosh_2.mp3', 'whoosh_3.mp3'], volume: 0.85},
	impact: {files: ['impact_1.mp3'], volume: 1},
	win: {files: ['win_4.mp3'], volume: 0.8},
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
				? events.map((e, i) => {
						const spec = SFX[e.kind];
						const file = spec.files[i % spec.files.length];
						return (
							<Sequence key={i} from={Math.max(0, Math.round(e.t * fps))} durationInFrames={Math.round(2.5 * fps)} layout="none">
								<Audio src={staticFile(`sfx/${file}`)} volume={spec.volume * sfxVolume} />
							</Sequence>
						);
				  })
				: null}
		</>
	);
};
