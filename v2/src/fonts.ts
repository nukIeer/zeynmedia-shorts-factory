import {loadFont as loadMontserrat} from '@remotion/google-fonts/Montserrat';
import {loadFont as loadBebas} from '@remotion/google-fonts/BebasNeue';

const montserrat = loadMontserrat('normal', {weights: ['700', '800', '900'], subsets: ['latin', 'latin-ext']});
loadMontserrat('italic', {weights: ['900'], subsets: ['latin', 'latin-ext']});
const bebas = loadBebas('normal', {weights: ['400'], subsets: ['latin', 'latin-ext']});

export const fonts = {
	title: montserrat.fontFamily,
	number: bebas.fontFamily,
};
