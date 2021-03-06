//Most basic JS esbuild settings
require('esbuild').build({
    entryPoints: ['src/app.js'],
    bundle: true,
    outfile: 'dist/app.js',
    target: "es6",
    loader: {
			'.html': 'text'
		},
		minify: true,
		sourcemap: true,
  }).catch(() => process.exit(1))


//ESBuild instructions:
//https://esbuild.github.io/getting-started/#your-first-bundle
//Natively builds react, ts, etc. with added specification.
