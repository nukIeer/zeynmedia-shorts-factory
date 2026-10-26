import React from 'react';

export const BallIcon: React.FC<{size: number}> = ({size}) => (
	<svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
		<circle cx="12" cy="12" r="10.5" fill="#ffffff" stroke="#1e1e2e" strokeWidth="1.5" />
		<path d="M12 7.2l3.6 2.6-1.4 4.2H9.8L8.4 9.8z" fill="#1e1e2e" />
		<path d="M12 7.2V2M15.6 9.8l4.9-1.6M14.2 14l3 4.2M9.8 14l-3 4.2M8.4 9.8L3.5 8.2" stroke="#1e1e2e" strokeWidth="1.3" />
	</svg>
);

export const TrophyIcon: React.FC<{size: number}> = ({size}) => (
	<svg width={size} height={size * 1.25} viewBox="0 0 24 30" aria-hidden="true">
		<defs>
			<linearGradient id="silver" x1="0" x2="1">
				<stop offset="0" stopColor="#9aa3b5" />
				<stop offset="0.5" stopColor="#ffffff" />
				<stop offset="1" stopColor="#8a93a6" />
			</linearGradient>
		</defs>
		<path d="M6 2h12v6a6 6 0 0 1-12 0z" fill="url(#silver)" />
		<path d="M6 4H2.5a3.5 3.5 0 0 0 4 4.5M18 4h3.5a3.5 3.5 0 0 1-4 4.5" fill="none" stroke="url(#silver)" strokeWidth="1.8" />
		<path d="M10.5 14h3v6h-3z" fill="url(#silver)" />
		<path d="M7 20h10l1 4H6z" fill="url(#silver)" />
		<path d="M5 24h14v4H5z" fill="#6b7280" />
	</svg>
);

export const CrownIcon: React.FC<{size: number}> = ({size}) => (
	<svg width={size} height={size * 0.75} viewBox="0 0 32 24" aria-hidden="true">
		<path d="M2 6l7 7 7-11 7 11 7-7-3 16H5z" fill="#ffd23f" stroke="#b7791f" strokeWidth="1.5" strokeLinejoin="round" />
		<circle cx="16" cy="15" r="2.2" fill="#e11d48" />
	</svg>
);
