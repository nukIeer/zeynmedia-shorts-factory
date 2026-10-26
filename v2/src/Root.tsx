import React from 'react';
import {Composition} from 'remotion';
import bar from '../samples/bar.json';
import box from '../samples/box.json';
import diamond from '../samples/diamond.json';
import grid from '../samples/grid.json';
import navy from '../samples/navy.json';
import {shortSchema, type ShortProps} from './schema';
import {Short} from './Short';

const FPS = 60;
const samples: Record<string, unknown> = {bar, navy, box, diamond, grid};

export const Root: React.FC = () => (
	<>
		{Object.entries(samples).map(([id, props]) => (
			<Composition
				key={id}
				id={id === 'bar' ? 'Short' : `Sample-${id}`}
				component={Short}
				schema={shortSchema}
				defaultProps={shortSchema.parse(props) as ShortProps}
				fps={FPS}
				width={1080}
				height={1920}
				durationInFrames={18 * FPS}
				calculateMetadata={({props}) => ({durationInFrames: Math.round(props.durationSec * FPS)})}
			/>
		))}
	</>
);
