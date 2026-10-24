import typescript from '@rollup/plugin-typescript';
import { terser } from 'rollup-plugin-terser';

const prod = process.env.NODE_ENV === 'production';

export default {
	input: 'src/index.ts',
	output: {
		dir: 'dist',
		format: 'cjs',
		sourcemap: true,
		exports: 'named',
	},
	external: ['semver', 'child_process'],
	plugins: [
		typescript(),
		prod && terser(),
	],
};
