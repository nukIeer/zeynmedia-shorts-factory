import {staticFile} from 'remotion';

/** Props may hold remote URLs, data URIs or paths under public/ (pre-fetched assets). */
export const asset = (src: string) => (/^(https?:|data:)/.test(src) ? src : staticFile(src));
