import typescript from 'rollup-plugin-typescript';
import pkg from './package.json';

export default {
	input: 'src/index.ts',
	output: [
		{ file: pkg.browser, format: 'umd', name: 'devalue' },
		{ file: pkg.main, format: 'cjs' },
		{ file: pkg.module, format: 'es' }
	],
	plugins: [
		typescript({
			typescript: require('typescript')
		}),
		{
			generateBundle({ format }, bundle) {
				if (format === 'umd') {
					const _bundle = bundle[Object.keys(bundle)[0]]
					_bundle.code =  _bundle.code.replace(/require\('consola'\)/, 'console')
				}
			}
		}
	]
};
