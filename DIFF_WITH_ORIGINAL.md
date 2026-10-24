# Differences from the original VulcaN dataset

This repository holds the VulcaN dataset of reviewed npm advisories, prepared for taint analysis with jelly-taint
(jelly-benchmarks, `misc/taint/vulcan/`). The original dataset is the state of commit `e72589b4a` (2023-04-04, the
last commit of the VulcaN authors): 957 advisory reviews. This repository differs from it in four ways: the
packages are extracted with their dependencies installed, 14 advisories are removed, the vulnerability locations of
203 reviews are corrected, and the reviews no longer hold the scores of the vulnerability detection tools. It holds
943 advisory reviews.

## 1. Extracted packages

- Each `dataset/packages/<id>/<pkg>-<ver>.tgz` is extracted to `dataset/packages/<id>/<pkg>-<ver>/` (the single
  top-level directory of the tarball is renamed) and the tarball is removed.
- The production dependencies of each package are installed with `pnpm install --prod` (pnpm 9.15.9). The
  `node_modules/` directories are git-ignored; each package directory keeps its `pnpm-install.log` and
  `pnpm-lock.yaml`, and `install-summary.json` lists the outcome per package.
- `.gitignore` also leaves out the iOS binaries that react-native-baidu-voice-synthesizer marks for Git LFS.
- `misc/taint/vulcan/install.py` of jelly-benchmarks performs these steps (commit `5199bcbce`).
- umount-1.1.6 (1512_GHSA-6q48-vjq2-mwcj) ships its JavaScript only in `build/` (the source is CoffeeScript), and
  jelly-taint does not expand directories named `build`. `build/` is renamed to `_build/`, and the `main` of its
  package.json follows (`_build/umount.js`).

## 2. Removed advisories

These 14 advisories are removed: their review `dataset/reviews/<id>.json`, their directory `dataset/packages/<id>/`,
their line in `dataset/advisories-with-reviews.txt` and their entry in `install-summary.json` (and the PoC
`dataset/reviews/pocs/1316_GHSA-2cf5-4w76-r9qv.*` and the patch `dataset/reviews/patches/117_GHSA-qg8p-v9q4-gh34.patch`).

| advisory | extracted package | reason |
| --- | --- | --- |
| 1020_GHSA-w725-67p7-xv22 | — | The dataset has no package tarball for it: `dataset/packages/<id>/` holds only the outputs of the tools. |
| 1029_GHSA-h97g-4mx7-5p2p | apostrophe-0.5.393 | Extracted package is apostrophe 0.5.393, but the vulnerable code (lib/modules/apostrophe-pages/lib/api.js, trailing-slash redirect in self.serve) is from apostrophe 2.x (review: 2.91.1); it is in neither the package nor its dependencies. |
| 117_GHSA-qg8p-v9q4-gh34 | shell-quote-1.6.0 | Quoting library: quote() (index.js:18) leaves `;`, `{`, `}` and `>` unescaped, and the caller runs the quoted string; shell-quote itself runs no command, so no attacker data flows to a sink in the package. quote(["x;{echo,INJECTED}"]) returns the payload unchanged; only an execSync in the caller prints INJECTED. |
| 123_GHSA-7f59-x49p-v8mq | swagger-ui-2.2.0 | swagger-ui 2.2.0 already contains the fix (commit 50c713a): the content_type / parameter_content_type / response_content_type option templates in dist/swagger-ui.js escape the value; the vulnerable code is not in the package. |
| 1311_GHSA-6xc2-mj39-q599 | strapi-3.0.0-beta.17.4 | Vulnerable controllers (packages/strapi-admin, packages/strapi-plugin-users-permissions) are not in the strapi package nor in its installed dependencies. |
| 1316_GHSA-2cf5-4w76-r9qv | handlebars-4.5.1 | Extracted handlebars 4.5.1 already escapes '=' in lib/handlebars/utils.js; the vulnerable escape map is from handlebars 3.0.3 (review correct_package_link), which is not in the dataset package. |
| 232_GHSA-4pf7-579w-f4gm | dwebp-bin-1.0.0 | The packaged dwebp-bin 1.0.0 does not contain the vulnerable code: lib/install.js builds from the vendored vendor/source/libwebp-1.1.0.tar.gz and lib/index.js fetches binaries over https; the annotated binBuild.url('http://downloads.webmproject.org/...') is from 0.3.0 (the review's correct_package_link). |
| 315_GHSA-cwcp-6c48-fm7m | — | The dataset has no package tarball for it: `dataset/packages/<id>/` holds only the outputs of the tools. |
| 827_GHSA-c35v-qwqg-87jc | express-basic-auth-1.1.7 | The shipped package is express-basic-auth 1.1.7 (patched; review's correct package is 1.1.6): the non-constant-time comparison 'username == i && password == users[i]' is replaced by timingSafeEqual-based safeCompare, so the vulnerable code is in neither the package nor its dependencies. |
| 981_GHSA-7cv6-gvx3-m54m | keystone-0.3.22 | The annotated renderValue code (`innerHtml = value.md.replace(/\n/g, '<br />')`) belongs to later keystone (4.x, PR 4478); keystone 0.3.22's MarkdownField.js has 133 lines and no such code, and it is not in any dependency. |
| GHSA-34r7-q49f-h37c | uglify-js-2.4.23 | Logic error in the compressor (CVE-2015-8857: boolean expressions are rewritten without accounting for non-boolean values, the 'comparisons' option at lib/compress.js:2158); no attacker data flows to a sink. |
| GHSA-f2rp-38vg-j3gh | shescape-1.1.2 | Escaping library: escapeShellArg (src/unix.js:2, src/win.js:2) keeps null characters, and the caller gives the result to child_process (index.js:6-8: `cp.spawn("command", shescape.escapeAll(userInput), options)`); shescape itself runs no command, so no attacker data flows to a sink in the package. |
| GHSA-r578-pj6f-r4ff | data-connector-rock-1.8.0 | The vulnerable single-step Person creation (POST /People with profile fields, triggering Rock auto-merge) does not exist in data-connector-rock 1.8.0: lib/index.js has no such code and createUserProfile (lib/auth/data-source.js:188) already posts only Gender/IsSystem and patches the profile afterwards, i.e. the patched behaviour. |
| GHSA-vc9j-fhvv-8vrf | scratch-vm-0.2.0-prerelease.20200709173451 | Browser only: the extension URL taken from a project's opcode (src/serialization/sb3.js:280) reaches importScripts(extension) in a Web Worker (src/extension-support/extension-worker.js:20) through webpack's worker-loader and the postMessage dispatch; it has no Node.js sink. |

## 3. Corrected reviews

The `vulnerability.vulnerability_location` of these 203 reviews is corrected to match the extracted packages:
the files the package ships instead of its source files, line numbers of the shipped version, and sinks on the
line of the dangerous operation. The `correct_cwe` of seven of them is corrected as well (decal
GHSA-j32x-j8pj-pg2h, preact 835_GHSA-cg48-9hh2-x6mx, express-hbs GHSA-rwxp-hwwf-653v, lodash.merge
1067_GHSA-2m96-9w4j-wgv7, subtext 1480_GHSA-g9cg-h3jm-cwrc, react-marked-markdown 668_GHSA-m7qm-r2r5-f77q,
express-brute 823_GHSA-984p-xq9m-4rjw). The other fields of the reviews are unchanged.

- 1003_GHSA-vfp9-gwrh-wq9g: Each `case` sink replaced by its file-system calls: GET readdir/readFile x2, PUT createWriteStream, POST rename/mkdir, DELETE rmdir/unlink. Source moved from the cleanUrl sanitizer (line 6) to the read of req.url (line 36).
- 1017_GHSA-2598-2f59-rmhq: Removed leading '/' from file paths; source code text set to the actual line 1336 (Model.prototype.findAll).
- 1021_GHSA-r3x4-wr4h-pw33: Sink was a string-argument line of vm.runInContext; moved both locations to the shipped entry files (main lib/index.js, browser lib/browser.js) that the package loads instead of src/: vm.runInContext / Function calls and saferEval parameter lists.
- 1025_GHSA-crf7-fvjx-863q: Sink was matchPath (route lookup); the static file is served by zero-static/serve-handler, so the sink is the package's call staticHandler(request, response). Source code text fixed.
- 1028_GHSA-9qgh-7pgp-hp7r: QueryInput is shipped as src/components/search/QueryInput.ts (not .jsx); block code texts set to their first line.
- 1034_GHSA-5634-rv46-48jf: Removed leading '/'; source sanitize() is at line 62, sink `return html;` at line 98.
- 1067_GHSA-2m96-9w4j-wgv7: Sink object[key] = value (assignMergeValue) is the prototype-pollution assignment and is kept; source moved from `module.exports = merge;` to the parameter list of the exported merge function. The advisory is "Prototype Pollution in lodash.merge" (CWE-1321): merge writes Object.prototype through `__proto__` and runs no command, so correct_cwe is CWE-1321 (was CWE-78). `correct_cwe`: "CWE-1321".
- 1069_GHSA-5947-m4fg-xhqg: Sink line 2207 is module.exports; prototype-pollution sink is the assignment object[key] = value in assignMergeValue (line 856).
- 1070_GHSA-46fh-8fc5-xcwx: Package ships index.js (not lodash.js); block is assignMergeValue at lines 853-858.
- 1071_GHSA-779f-wgxg-qr8f: Block code text set to the first line of baseAssignValue (lines 808-819).
- 1081_GHSA-h9wr-xr4r-66fh: Removed former location 1 (ComboEntryFactory:54, options.id in a domQuery CSS selector, not an HTML write; the HTML write of options.id is the kept ComboEntryFactory:100 location). LinkEntryFactory source moved to `function link(options) {` (line 34); PropertiesPanel sink setStart moved to line 1213 (kept as annotated, though it is not an HTML write); code texts set to actual lines.
- 1097_GHSA-m86m-5m44-pc93: File is src/index.js (removed 'package/' prefix and added src/).
- 1110_GHSA-7j93-2h6r-hm49: Sink moved from a template .replace() to the HTML response write res.end(html) (line 194).
- 1111_GHSA-j657-59rv-qwm6: file.js does not exist (util/file.js is a file read, not XSS). XSS sink is the response write `ctx.body = _content` of the directory-listing HTML built in util/dir.js.
- 1118_GHSA-3gx7-xhv7-5mx3: Sink 3 moved from the property read `object.value[property.value]` (line 509), which obtains Function but runs no code, to `new Func(...args)` (line 520) in NewExpression, the call the PoC `new {}.constructor.constructor(...)` reaches; lines 416 and 422 are the other calls of an evaluated callee.
- 1122_GHSA-5mrr-rgp6-x4gr: Source pointed into juice-shop (not shipped); both locations moved to dist/DocumentMatcher.js loaded by index.js: $where(selectorValue, ...) and Function('obj', 'return ' + selectorValue).
- 112_GHSA-98pq-pmw9-4gpm: Abstract query-generator sinks 2 and 3 moved to lines 1771 and 1773 where the LIMIT fragments are; code texts set to actual lines.
- 114_GHSA-p788-rj37-357w: Second block: file name had surrounding spaces; the linux64 http URL is at line 6.
- 1153_GHSA-xqh8-5j36-4556: Sinks shifted by one line to the query calls (97 prune DELETE, 185 get SELECT, 209 set INSERT, 222 destroy DELETE); the .then() sink became the pgPromise.query call (166), and the pool.query call of the same wrapper (170) was added.
- 1156_GHSA-88h9-fc6v-jcw7: Source mwParse middleware is at line 54.
- 115_GHSA-cgpp-wm2h-6hqx: File name typo criteriaProcessos.js -> criteriaProcessor.js; block code text set to its first line.
- 1165_GHSA-4rgj-8mq3-hggj: File is lib/index.js; block 219-300 is internals.multipart, code text set to its first line.
- 116_GHSA-2r5h-gh4x-8hp9: Package ships index.js (no src/); http.get(link.url, ...) is at line 31; line numbers made integers.
- 1184_GHSA-pc5p-h8pf-mvwp: Block lines are correct; code text set to the first line of the block.
- 1185_GHSA-p77h-hv6g-fmfp: lib/configure.js does not exist; the debug console.log block is in lib/odbc.js 2011-2014.
- 118_GHSA-hxm2-r34f-qmc5: Line numbers were correct; sink code text set to the actual line (regex escaping).
- 1211_GHSA-phph-xpj4-wvcv: Sink moved from the debounced save call to the HTML write: the marked() output is rendered with dangerouslySetInnerHTML in client/rendered.js.
- 1221_GHSA-876r-hj45-fw7g: index.js is lib/index.js (package main); saferEval at line 92, vm.runInContext at line 64.
- 1227_GHSA-gr4j-r575-g665: js/ and ts/ are not shipped: location 0 sink moved to es-modules/parts/SvgRenderer.js:1006; location 1 (the ts copy) pointed at the same code in the shipped bundle highcharts.src.js (6440/6442).
- 124_GHSA-v2jq-9475-r5g8: Sink code text set to the actual `$('<span ...' + itemTitle ...)` line; moved to dist/bootstrap-tagsinput.js (package main, identical to src/).
- 125_GHSA-c7pp-g2v2-2766: Removed 'package/' prefix; code texts set to actual new Function lines.
- 1303_GHSA-j27j-4w6m-8fc4: Removed 'package/' prefix; readdirSync is at line 19.
- 1319_GHSA-3gpc-w23c-w59w: Removed leading '/'; script.runInNewContext is at line 73.
- 1329_GHSA-6fh5-8wq8-w3wr: File 'a/lib/index.js' -> 'lib/index.js'; source line 21 -> 22. Sinks (calls into the lodash.set / lodash.setwith dependencies) kept.
- 132_GHSA-gjhx-gxwx-jx9j: Location 1 (coffee source): source line 466 -> 462 (the DragElement constructor). Other locations unchanged.
- 1343_GHSA-89mq-4x47-5v83: File 'src/angular.js' (not shipped) -> 'angular.js'; source line 324 -> 463. Sink was the recursive call baseExtend(dst[key], [src], true); replaced by the property assignment dst[key] = src (line 488) that writes onto the prototype.
- 1347_GHSA-hg79-j56m-fxgv: Sink line 281 -> 280 (return of the unescaped dangerouslySetInnerHTML.__html).
- 135_GHSA-3j7m-hmh3-9jmp: Sink parser.write(html) -> line 159 'result += text;' in ontext, which concatenates the unescaped text (e.g. a stray '<' of a nested tag, htmlparser2 issue 105) into the returned HTML; the patch re-sanitizes the result recursively.
- 1436_GHSA-x8qc-rrcw-4r46: File 'package/node_modules/pacote/...' -> 'node_modules/pacote/lib/fetchers/directory.js' (installed dependency); source line 34 -> 35. Sink kept.
- 1440_GHSA-cfwc-xjfp-44jg: File '/gnuplot.js' -> 'gnuplot.js'; code set to the actual trimmed lines. Sink kept: plot.write writes the commands to the gnuplot process spawned via the comandante dependency.
- 1441_GHSA-65xx-c85x-wg76: File 'package/plotter.js' -> 'plotter.js'. Sinks kept: writes of option strings into the stdin of the spawned gnuplot process (command injection via gnuplot 'system').
- 1443_GHSA-v6c5-hwqg-3x5q: Files 'src/strategy.js' -> 'lib/strategy.js' and 'src/test/strategy.test.js' -> 'test/strategy.test.js'; code set to each block's actual first line; line numbers as integers.
- 1446_GHSA-7r9x-hr76-jr96: Location 2 source: line 173 -> 217 (Git.prototype.pull).
- 1449_GHSA-25v4-mcx4-hh35: File 'widgets/blocker/blocker.js' -> 'widgets/blockers/blockers.js'; lines unchanged.
- 1453_GHSA-r5fx-8r73-v86c: File 'src/angular.js' -> 'angular.js'. Sink was the sanitization condition (the patch adds xlinkHref to it); replaced by the attribute write this.$$element.attr(attrName, value) (line 7672) that puts the unsanitized a[xlink:href] value into the DOM.
- 1457_GHSA-qcff-ffx3-m25c: Sink moved from the meta-exec call (bin/meta-git-clone:20) to the call that runs the command: meta-exec without options.parallel runs cp.execSync(options.cmd, ...) (node_modules/meta-exec/index.js:61, Node.js stack trace).
- 1470_GHSA-mg69-6j3m-jvgw: Sink 'bin/sanitize.js:97' (no such file; the flawed iframe-src regex is lib/sanitize.js:97, a filter, not an output) -> lib/sanitize.js:16, the call handing the HTML and the permissive config to the sanitize-html dependency that returns it. Source getSanitizerConfig(options) (config, not attacker input) -> the exported marky(markdown, options) in index.js:21.
- 1478_GHSA-5854-jvxx-2cg9: File 'index.js' -> 'lib/index.js'; lines unchanged.
- 1480_GHSA-g9cg-h3jm-cwrc: Source line 278 -> 280 (onPart). Sink kept: data[name] = value is the property assignment with the attacker field name. The advisory is "Prototype Pollution in @hapi/subtext" (CWE-1321): a crafted multipart part becomes the prototype of the payload object, and subtext runs no command, so correct_cwe is CWE-1321 (was CWE-78; the advisory record has CWE-400). `correct_cwe`: "CWE-1321".
- 1484_GHSA-36c4-4r89-6whg: Sink line 305 -> 100 (decoder lookup by the content-encoding header in Parser.prototype.parse, the function of the source).
- 1492_GHSA-9px9-f7jw-fwhj: Files 'middleware.js'/'controller.js' -> 'src/...'. Source and sink were swapped: source is now the request body read (src/middleware.js:63) in the POST / handler, sink the spawn call (src/controller.js:140).
- 1494_GHSA-f3vw-587g-r29g: Sink read(file) replaced by the two fs.readFileSync calls it dispatches to (dev at line 2630, production at line 2631), each with the same source.
- 1499_GHSA-8whr-v3gm-w8h9: Sink code set to the actual eval lines (the package wraps the strings in parentheses); lines unchanged.
- 14_GHSA-g4xp-36c3-f7mr: Sink File.load(path, ...) (lib/directory.js:112) -> the Fs.createReadStream(path) in lib/file.js:155 that File.load reaches through the response marshal.
- 1507_GHSA-426h-24vj-qwxf: File 'package/index.js' -> 'index.js'; code set to the actual lines. Sources 1-2 (cmdString construction, code did not match) -> the exported install/uninstall parameter lists (lines 5, 37), like location 3. Location 3 (list, sink line 71) removed: its command is the constant "npm ls --depth=0 " + ("-g " or " "), and the parameter path only sets the cwd option, which the shell does not read; list("/tmp; echo INJECTED > marker") runs `npm ls --depth=0` and makes no marker file, while install and uninstall put the package names into the command.
- 1512_GHSA-6q48-vjq2-mwcj: File 'build/unmount.js' -> '_build/umount.js' (the directory is renamed, section 1); lines unchanged.
- 1517_GHSA-gm9x-q798-hmr4: Minified dist/index.js: source (exports.get) and sink (r.exec('git ls-remote --tags '+e, ...)) are both on line 1; code set to the actual line text (the annotated fragments used other quotes).
- 1523_GHSA-p6mc-m468-83gw: Source line 3965 -> 3978. Sink 'nested = nested[key]' (the walk into the prototype) -> the property assignment object[key] = value in baseAssignValue (line 2559), reached from baseSet via assignValue(nested, key, newValue) at line 4006. The review's line numbers are from lodash 4.17.15; the shipped 4.17.18 already returns early on __proto__/constructor/prototype keys in baseSet (line 3993).
- 1530_GHSA-w42g-7vfc-xf37: Code '(too large)' -> the block's actual first line; lines unchanged. The compiled class is dist/ApolloServer.js lines 17-37.
- 153_GHSA-jcw8-r9xm-32c6: Sink moved from the shell.exec(cmd, {silent: true}) wrapper call to the operation that runs cmd in shelljs 0.2.6: without a callback, exec() takes execSync, which escapes cmd into a generated script (child.exec('...' + escape(cmd) + '...'), line 48), writes it to a temp file (56) and runs it with node (57).
- 183_GHSA-ff29-f57w-2mm3: File 'updatedb.js' -> 'scripts/updatedb.js'. Source is now the insecure http URL (line 32, the former sink); sink is the http.get download it flows to through fetch(database.url) (line 117).
- 201_GHSA-6v7p-j23v-4xmw: File 'robot-js-2.0.0/package/scripts/install.js' -> 'scripts/install.js'. Sink sigs.on("data") -> the plain-http download mHTTP.get(url) (line 123) that request(SOURCE, ...) performs.
- 211_GHSA-735c-r4vc-6gm9: Source file 'test/bionode-era.js' (typo) -> 'test/bionode-sra.js'.
- 242_GHSA-vvwp-3f54-xc39: File 'scripts/install.js' -> 'scripts/update-closure.js' (the install script); code set to the block's first line; lines unchanged.
- 245_GHSA-4p7j-5ppx-rfhm: Source is now the insecure http URL (line 23, the former sink, code fixed); sink is the http.get download (line 27). The former source attemptDownload(3) is only the top-level call.
- 25_GHSA-44g9-w23c-5rw7: Sinks readContents(absolute, ...) / pipeStream(absolute, ...) -> the fs calls they perform on the path: fs.readdirSync(location) (line 157) and fs.createReadStream(dir) (line 245).
- 261_GHSA-722q-3g9x-vp8q: Code set to the block's actual first line (the annotation merged lines 15-16 with other quotes); lines unchanged.
- 267_GHSA-g84j-95x2-7g67: Block 13-15 -> 6-12, the dist map of http download URLs that the annotated code shows.
- 294_GHSA-2r9c-46v3-43fc: File 'install.js' -> 'bin/install.js'; lines unchanged.
- 2_GHSA-rph7-j9qr-h8q8: src/lib/probe-handler.js is not shipped; moved to lib/probe-handler.js (source line 16, sink is the child_process.exec call at line 19).
- 305_GHSA-2r7f-4h2c-5x73: Source file src/parser.js is not shipped; moved to lib/parser.js:124. Sink kept: swaggerParser.validate hands the document to swagger-parser, which resolves the $ref file read.
- 310_GHSA-38h8-x697-gh8q: Block range kept; code set to the actual first line of the block.
- 322_GHSA-26q7-g57v-mxcp: Location 1 sink moved from the object property 'topic: topic' to the client.emit call (line 30) that sends the IRC topic to the browser, where location 0 writes it with .html().
- 326_GHSA-cmh5-qc8w-xvcq: Location 2 sink pointed at dist/commonjs/Interpolator.js:31; set to dist/es/Interpolator.js:31 to match its dist/es source. Truncated source code text ('arguments[0>') corrected in locations 0, 2, 3.
- 329_GHSA-2pqj-h3vj-pqgw: Sinks moved from the selector regex match to the innerHTML write in jQuery.clean, reached from init via jQuery.parseHTML(match[1]) -> buildFragment -> clean.
- 32_GHSA-xwg4-93c6-3h42: Sink moved from the dotfile check to the fs.createReadStream that reads the traversed path.
- 343_GHSA-3cgg-gh9j-w8vm: File bin/iter-http.js is shipped as bin/iter-http (same line numbers; http.js is an identical copy shifted by one line). The responseFile call is replaced by its two fs.createReadStream calls.
- 347_GHSA-6w83-22gj-5pv9: Leading '/' removed from file; sink moved from response.write to the fs.readFile of the traversed path.
- 352_GHSA-5w8q-x7hc-jhp6: Location 2 sink moved from dispatch.directory(...) to the fs.readdir in dispatch.dir_list that it reaches.
- 355_GHSA-gqfv-g9f6-3v3m: Sink code text corrected (typo 'readFile*path').
- 356_GHSA-hfq9-rfpv-j8r8: Locations 0 and 1 (sinks: the two self.proc_calc calls) replaced by one location whose sink is the fs.readFile that proc_calc performs. Locations 2-4 kept (fs.readFile, exec, spawn).
- 36_GHSA-69rr-wvh9-6c4q: Sink moved from this.file(...) to the fs.createReadStream in Mount.prototype.streamFile that reads the traversed path.
- 382_GHSA-j38m-7q52-fgfh: Source code text did not match line 19; set to the request handler on line 19 (req is the attacker input; start(conf) on line 18 takes configuration).
- 394_GHSA-2958-5r4r-wvv6: Sink moved from the path construction to the fs.readFile on line 7.
- 412_GHSA-4vfj-c2xf-8r48: Sink line corrected 8 -> 9.
- 413_GHSA-xj6q-9hx8-mm7f: Source code text corrected (quote characters).
- 417_GHSA-7g8m-5qh9-9pgw: Sink moved from response.write to the fs.readFile in util4HTML.getHTMLBinary, called with '.' + pathname at controller.js:183.
- 42_GHSA-f5w6-r7rg-mcgq: 'package/' prefix removed from block 0 and its code set to the actual line text (the review had unescaped the regex). Block 1 removed: the is_url regex does not exist in 3.22.0 (isURL is implemented by string splitting).
- 433_GHSA-78h7-fgq9-625x: Source line corrected 27 -> 25.
- 439_GHSA-8vmc-g99q-xj94: Sink line corrected 10 -> 9.
- 43_GHSA-79mx-88w7-8f7q: Sink code text corrected to the actual line 917 (exports.xssClean, not xss.clean).
- 445_GHSA-vgjp-vh3c-32v3: Sink file mock.js does not exist; the readFileSync is at mocks.js:73.
- 471_GHSA-v464-rcx7-j875: File name case corrected (infra.data.js -> Infra.data.js); sink code text at line 137 corrected.
- 472_GHSA-3grc-fgh6-g5gp: 'package/' prefix removed; source line corrected 4 -> 5.
- 476_GHSA-cpp2-q66x-fq44: Sink code texts corrected (quote characters); lines unchanged.
- 47_GHSA-mvmf-cvfx-qg55: 'package/' prefix removed. Source moved from the regex definition to analyze(html), where the attacker string enters; sink (the exec applying the vulnerable regex) kept.
- 49_GHSA-qr28-7j6p-9hmv: Sink moved from infoControl.addInfo(json.attribution) to the innerHTML write in InfoControl._update that addInfo reaches.
- 523: Sink moved from the shell.exec(cmd, {silent: true}) wrapper call to the operation that runs cmd in shelljs 0.2.6: without a callback, exec() takes execSync, which escapes cmd into a generated script (child.exec('...' + escape(cmd) + '...'), line 48), writes it to a temp file (56) and runs it with node (57).
- 531_GHSA-x5pg-88wf-qq4p: Block range kept; code set to the actual first line (the em regex).
- 551_GHSA-pv8x-p9hq-j328: Source moved to parse(expr), where the expression enters; sink moved from the ObjectNode key compilation to the new Function that compiles the generated code.
- 552_GHSA-vx5c-87qx-cv6c: Source moved to parse(expr). Sink moved from the FunctionNode check to the new Function in typed-function 0.10.5 that compiles code containing the typed function name (fixed by upgrading typed-function).
- 554_GHSA-g8m7-qhv7-9h5x: Sink getFileStat (lstat) replaced by the file-system reads of the traversed path: fs.readFile (lib/read-file.js) and fs.readdir (lib/read-folder.js), called from middleware/file-explorer.js lines 51 and 36.
- 557_GHSA-m4vv-p6fq-jhqp: Source moved from the configured directory to the read of this.request.path (line 30). Sink file middleware/file_explorer.js does not exist; replaced by fs.readFile (lib/read-file.js) and fs.readdir (lib/read-folder.js) reached from middleware/file-explorer.js lines 51 and 36.
- 560_GHSA-68gr-cmcp-g3mj: Source moved to serveFile definition (line 286). Sink was the cache lookup this.cache.get (not a file-system op); now fs.createReadStream(fp) at line 579, which reads the attacker-controlled path.
- 572_GHSA-f522-ffg8-j8r6: Block code set to the actual text of formats.js line 4 (the vulnerable email regex).
- 576_GHSA-hfj4-96f7-6r5g: Sink moved to line 45, where the shipped code assigns root.innerHTML = html.
- 579_GHSA-xcvv-84j5-jw9h: Removed 'package/' prefix; sinks shifted to the target[key] assignments at lines 44, 46, 48; fixed '{{' typo in source code.
- 585_GHSA-jrhj-2j3q-xf3v: Source was code from another package; the XSS is via malicious file names, which enter at fs.readdir (line 117). Sink was fs.stat; now res.send of the directory-listing HTML (line 146).
- 586_GHSA-x26f-26qw-hhhx: Location 3 sink moved from line 106 to fs.createReadStream(file) at line 116; location 8 sink code fixed ('tif' typo).
- 590_GHSA-2x4q-6jfv-8h9h: Sink was an event emit; now filed(request.fullPath).pipe(res) at line 91, which hands the traversed path to the 'filed' dependency that reads the file.
- 595: index.js does not exist (package ships lib/simple-server.js, which only wires connect.directory). The XSS lives in the installed connect 2.10.1 directory middleware: req.url pathname (line 79) and readdir file names (line 101) are written unescaped into the listing HTML sent by res.end(str) at line 135.
- 610_GHSA-7375-vjr2-3g7w: Source was a require(); attacker file names enter via the html-ls listing stream created at line 142 (href only passed through encodeURI). Sink is the write of the rendered listing HTML to the response (.pipe(res), line 191).
- 612_GHSA-hr2v-3952-633q: File path fixed from 'lib/deep-extend' to 'lib/deep-extend.js'; lines unchanged.
- 63_GHSA-rc8h-3fv6-pxv8: File path fixed from 'transmit.js' to 'lib/transmit.js'; lines unchanged.
- 642_GHSA-m8fw-534v-xm85: Sink file typo 'commmon/' fixed to 'common/cloudfunc.js'.
- 648_GHSA-8xqr-4cpm-wx7g: File 'ReactSVG.js' is shipped as dist/ReactSVG.js; line 203 holds the evalScripts: 'once' default.
- 652_GHSA-wm77-q74p-5763: Source moved to the returned provider function (req, pathname) at line 68, where the attacker path enters (the exported factory only takes options). Sink was the ../ check; now fs.createReadStream(foundPath) at line 88.
- 665_GHSA-fm87-46vv-jqrr: Removed 'package/' prefix. Sink was the internal wrapper httpRequest.stream; now the call that hands req and the traversed path to the 'send' dependency (lib/http-request.js line 96).
- 668_GHSA-m7qm-r2r5-f77q: Code text fixed (double quotes). Source moved to the renderer.link parameter list (line 97), where the unescaped href/title/text enter; sink stays at line 98. The advisory is "Cross-Site Scripting in react-marked-markdown" (CWE-79): the sink returns an HTML string with an unescaped href and runs no command, so correct_cwe is CWE-79 (was CWE-78). `correct_cwe`: "CWE-79".
- 695_GHSA-29gp-92wp-94q8: Removed 'package/' prefix. Sink was in openBrowser.js and not a child_process call; now child_process.spawn of cmd.exe in launchEditor.js line 334, which receives the attacker file name on Windows.
- 696_GHSA-m734-r4g6-34f9: Lines shifted by one: source at 1196, sinks at 1215 and 1217.
- 717_GHSA-qw93-45r3-p66p: Removed leading '/' from file; block 1 code set to line 60 text (result[key] = clone(obj[key]);); block 2 code set to its first line.
- 736_GHSA-gwg9-rgvj-4h5j: Source moved to the exported compile(format) parameter list (line 373), where the format string enters; sink unchanged.
- 741_GHSA-jhgp-hvj6-x2p2: Source moved to the request read req.pathname (line 160). Sink was fs.readFile; the XSS is the directory listing that inserts the unescaped pathname into HTML (util.format(TEMPLATE, base, base, list), line 79).
- 745_GHSA-v2p6-4mp7-3r9v: File name typo 'underscapeHTML.js' fixed to 'unescapeHTML.js'.
- 748_GHSA-hgr5-82rc-p936: Sink was an object literal field; now element.append(val) at line 1380, which inserts the cell value into the DOM as HTML.
- 751_GHSA-w32g-5hqp-gg6q: Removed leading '/'. Sink was the (bypassable) javascript: filter; now the line writing vertex.link into the SVG anchor href (line 51119).
- 753_GHSA-44vf-8ffm-v2qh: Block code set to the actual first line of the block (decodeCookieFn definition).
- 767_GHSA-hxwc-5vw9-2w4w: File typo 'lib/mongdb.js' fixed to 'lib/mongodb.js'; lines unchanged.
- 769_GHSA-2hwp-g4g7-mwwj: Source was the anyLinks option default; now the exported $.terminal.format(str, options) (line 3586). Sink was the condition; now the line concatenating the unescaped link data into the href attribute (line 3680).
- 773_GHSA-9wjh-jr2j-6r4x: Sink file fixed to pi_video_recording.js and line to the spawn call (49); added the childProcess.exec in encodeRecord (line 69), where the same filename reaches a shell command.
- 777_GHSA-73v8-v6g4-vrpm: File name fixed from 'lib/extractor.js' to 'lib/extractors.js'; block code set to each block's first line.
- 784_GHSA-j9f8-8h89-j69x: Sink file fixed: the cp.exec(command, { shell: true }) call is in lib/bucket.js line 18, not lib/openfiles.js.
- 787_GHSA-hgch-jjmr-gp7w: Sink code set to the vm.runInContext call at line 43 (the annotated text was its argument on line 44).
- 794_GHSA-2j5v-fc74-j9q2: Block moved to line 3959 of src/editormd.js, which holds the .append(markdownParsed) (line 3971 is the same code in the built editormd.js).
- 795_GHSA-xg75-3277-gvvj: src/index.js is not shipped by serve; the code is in the installed serve-handler dependency at the same lines.
- 799_GHSA-2hhw-p8mg-jrm6: Sink was res.write; now fs.readFile(abspath) at line 93, which reads the attacker-controlled path.
- 812_GHSA-xf5p-87ch-gxw2: Block 3 code was split at the regex's literal '\n'; code set to the actual first line of each block (line numbers unchanged).
- 813_GHSA-8j8c-7jfh-h6hx: Sink '_result[keyNode] = valueNode' is a plain store; the code executed via String(keyNode)/toString is built by new Function in type/js/function.js (two branches, one location each). Source moved from internal storeMappingPair to the exported load(input, options).
- 822_GHSA-gh4g-3gm9-5wrq: Removed leading '/' from paths; src/shave.js sink moved from the template-literal argument (62) to the el.insertAdjacentHTML( call (60); codes set to actual line text.
- 823_GHSA-984p-xq9m-4rjw: Block code was a description; set to the actual first line (increment function). The advisory is "Rate Limiting Bypass in express-brute": concurrent requests race between get and set in increment, and no command runs, so correct_cwe is CWE-362 (race condition; was CWE-77, which the advisory lists without a matching description). `correct_cwe`: "CWE-362".
- 830_GHSA-9q64-mpxx-87fg: Location 0 sink (url: of the internal 404 re-dispatch, line 378) is not a redirect; the only redirect is res.setHeader('location', ...) at 395 (was annotated at 396). Both locations then coincide, so they are merged into one.
- 831_GHSA-8v5f-hp78-jgxq: File path fixed: jwt.js -> lib/jwt.js (lines unchanged).
- 833_GHSA-78j5-gcmf-vqc8: Source moved from module.exports = function(config, auth, storage) to the request read req.get('host') (64); sink moved from that line to res.send(webPage) (69), which writes the unescaped base URL into the HTML.
- 834_GHSA-9w87-4j72-gcv7: File path fixed: generate-and-save.js -> dist/generate-and-save.js.
- 835_GHSA-cg48-9hh2-x6mx: A JSON-provided vnode (no constructor check) reaches render(); source set to render(vnode, parentDom), sink set to the dom.innerHTML write of dangerouslySetInnerHTML in diff (was 'return vnode;' in createVNode and a createElement line as source). Browser only: the sink is a DOM innerHTML write (XSS), so correct_cwe is CWE-79. `correct_cwe`: "CWE-79".
- 85_GHSA-rrj3-qmh8-72pf: Sink file path fixed: src/index.js -> tasks/gh-pages.js (same line).
- 880_GHSA-42xw-2xvc-qx8m: File path typo fixed: lib/adaptares/http.js -> lib/adapters/http.js.
- 884_GHSA-8v67-x8q5-3x3g: File path fixed: lib/simeditor.js -> lib/simditor.js (lines unchanged).
- 885_GHSA-788m-pj96-7w2c: Location 2 sink module.add.userSuggestion(query) replaced by the two HTML writes it reaches: $addition.html(html) in add.userSuggestion (2761) and `$('<div />').html(html)` in create.userChoice (214).
- 889_GHSA-cgjv-rghq-qhgp: Both sinks were doStream(...) calls; the file-system call is fs.createReadStream(filePath, ...) in doStream (57). Source moved from setServePath (config) to the exported serve(request, response), which reads request.url. The two locations then coincide and are merged.
- 89_GHSA-xg5r-8j97-2wrj: Sink 'path = mellow.pathToWin(name, root)' only builds the path; replaced by one location per file-system operation it reaches (files.pipe/flop.create in put, patchfile in patch, flop.read/beautify/minify/createReadStream in get, ponse.sendFile in onGet, flop.delete in delete). Source moved from internal onFS to the request read ponse.getPathName(req).
- 915_GHSA-724c-6vrf-99rq: Source line moved 208 -> 232 (normalizeCredentials call).
- 916_GHSA-6fcr-9h9g-23fq: Block shifted to start at 'const toCancel = blocks' (90) and end at the closing of each(...) (100).
- 959_GHSA-v86x-f47q-f7f4: Source file path fixed: src/index.js -> ___fs++.js (findfiles, same line).
- 962_GHSA-9r3m-mhfm-39cm: Block lines correct; code set to the shipped JS first line (annotation had the TypeScript text).
- 966_GHSA-pmv6-gf98-p3r5: Sinks moved from the template-literal argument lines to the execa shell calls 'return sh(' (11, 16). Then moved to the call that runs the command: execa.shell reaches childProcess.spawn(parsed.cmd, parsed.args, parsed.opts) (node_modules/execa/index.js:204) in both branches (Node.js stack trace for POSIX and win32). The two locations then coincide (source index.js:5), so they are merged into one.
- 967_GHSA-45j8-pm75-5v8x: File path fixed: src/helper/route -> src/helper/route.js.
- 97_GHSA-r87w-47m8-22w3: Block moved from (0, eval)('this') (lines 16-17, a constant the patch also removed) to the template compilation new Function("data,view,j,u", code) (1789): CVE-2016-3942 is template injection, where an expression in a template tag is compiled into the generated function.
- 980_GHSA-7qcx-jmrc-h2rr: Removed '/package/' prefix from paths; code set to actual line text.
- 988_GHSA-w992-2gmj-9xxj: Sink moved from the property copy swagger.info.description = ... to the HTML write $(this.el).html(Handlebars.templates.main(this.model)) (22351), whose main template inserts info.description unescaped.
- 989_GHSA-hq8g-qq57-5275: File path fixed: model.js -> lib/model.js.
- GHSA-2m8v-572m-ff2v: Location 4/6 sinks util.execSafe('ps', args) are a package wrapper; sink moved to its spawn(cmd, args, options) (lib/util.js:399). Locations 4 and 6 then coincide; location 6 removed.
- GHSA-2mm9-c2fx-c7m4: isExternal bypass lets a remote markdown page skip purify.sanitize; source set to the URL read 'var href = location.href;' in getCurrentPath (7957), sink to the innerHTML write in _renderTo (7627) (was the url.match line inside isExternal).
- GHSA-333x-qr3v-g4xx: Sink moved from the platform-command call (lib/generator.js:32) to the call that runs the command: childProcess.exec(cmd, callback) (node_modules/platform-command/platforms/childProcess/command.js:5, Node.js stack trace).
- GHSA-35jh-r3h4-6jhm: File path typo fixed: lodhash.js -> lodash.js.
- GHSA-39q4-p535-c852: File fixed: lib/index.js -> php/net-gopher/gopher_parsedir.js; block extended to include the line applying the regex (dirent.match(entryPattern)).
- GHSA-3crj-w4f5-gwh4: Sink moved to new(Function)('return (' + expression + ')') in tree/javascript.js (20), which the JavaScript node's eval runs; location 1 (Variable eval for @{} interpolation, same source) reaches that same sink and was merged into it. The e() escape function (functions.js 215-216) and the parser for `...` JavaScript (parser.js 1001-1016) are not dangerous operations and are not locations.
- GHSA-4gfq-6m28-m5mg: Location 2 (driveList, sink line 115) removed: driveListWindows runs the constant command "wmic logicaldisk get caption,providername,drivetype,volumename", and driveList has only the parameter callback. Location 1 (detail, sink line 46) puts the drive name into the wmic command and is kept.
- GHSA-4r62-v4vq-hr96: Blocks shifted +73 lines to the shipped lib/marked.esm.js: strong/em regex objects (1202-1213), text/punctuation (1217-1218), _blockSkip/_overlapSkip (1227-1228); codes set to actual text.
- GHSA-4wv4-mgfq-598v: File path fixed: index.js -> lib/index.js.
- GHSA-6c3f-p5wp-34mh: Sink moved from the async-execute call (lib/reset/index.js:11) to the call that runs the command: exec(script, ...) of child_process (node_modules/async-execute/index.js:10, Node.js stack trace). Location 2 (lib/reset/index.js:15) removed: it runs only when destination is a number (typeof check on line 14), and Math.abs of a number gives only digits; reset(5) runs `git reset HEAD~5 --hard`.
- GHSA-6fw4-hr69-g3rv: Source line moved 11 -> 44 (setter: function(path)).
- GHSA-7p8h-86p5-wv3p: In this version the $.get callback parameter is named `prop` (line 188) and the jQuery .html() write of the fetched value is at line 191; moved source and sink to these lines.
- GHSA-8f89-2fwj-5v5r: Sink code corrected to the shipped text `tmp[k] = klona(x[k]);` (line 9).
- GHSA-8px5-63x9-5c7p: Sink moved from the template-string argument (line 38) to the execSync call on line 37.
- GHSA-9cp3-fh5x-xfcj: Source moved from a non-existent regex line (106) to the exported function's parameter list `charset(obj, data)` (line 35); sink at line 59 already applies the vulnerable regex.
- GHSA-9v3m-8fp8-mj99: Attacker data enters through the element's data-* attributes (`...$(this.element).data()`, line 641). Sinks: the .html() write of title/content (line 433) and the jQuery HTML parse of config.template (line 411). Replaced the event-trigger sink (line 324) and the former source at line 433, which is itself the HTML write.
- GHSA-c4qr-gmr9-v23w: Location 1 sink moved to `const server = new WebSocket.Server({` (line 70).
- GHSA-cf4h-3jhx-xvhq: Sink moved from the call of the compiled template (line 922) to `new Function(...)` (line 915); source code text corrected.
- GHSA-cgc7-mwp4-3ccx: Source moved from the disallowedTags list to the sanitizeHtml(html, options) parameter list (line 72); sink moved from parser.write to the line concatenating the unescaped tag and attributes into the HTML output (line 131).
- GHSA-ff7x-qrg7-qggm: Code text corrected to the shipped lines (`set(obj, path, value) {`, `obj[p] = value;`); line numbers unchanged. Note: dot-prop 4.2.1 already contains the __proto__/prototype/constructor filter.
- GHSA-h4hr-7fg3-h35w: Code placeholders replaced by each vulnerable regex line's text. Removed location 20 (prism-php.js:18 `alias: 'constant'`): the vulnerable PHP number regex fixed by the patch does not exist in prismjs 1.22.0.
- GHSA-h4j5-c7cj-74xg: Block moved to line 534, spawn(process.argv[0], ["-e", execString]), which runs the script into which request data is concatenated (line 531).
- GHSA-h6q6-9hqw-rwfv: Location 2 code corrected to the line's actual text `buf.push('">');` (line 1085, closing the PUBLIC id).
- GHSA-hxcc-f52p-wc94: Sink moved to line 196 where the RegExp is serialized.
- GHSA-j32x-j8pj-pg2h: Sink moved from the recursive assignment (line 49) to `target[name] = copy` (line 50), the write that pollutes Object.prototype after recursion through __proto__. correct_cwe without CWE-94: extend() is a prototype pollution (the deep merge writes Object.prototype through __proto__) and executes no code. `correct_cwe`: ["CWE-1321", "CWE-400"].
- GHSA-jff2-qjw8-5476: Locations 4 and 6: sink moved from util.execSafe('ps', args) to its child_process call `spawn(cmd, args, options)` in lib/util.js:399, as in locations 0 and 1.
- GHSA-jqh7-w5pr-cr56: Sink code corrected to the line's actual text (escaped \n in a single-line string); ctx.body HTML write at line 21 kept.
- GHSA-jxg6-fhwc-9v9c: File path corrected to src/lib/crawler.js.
- GHSA-ph32-23p8-9rw5: Source file path corrected to linux/manager.js.
- GHSA-pxcc-hj8w-fmm7: File path corrected to dist/getPackedPackage.js.
- GHSA-q4h8-7qff-gh6c: Version 2.38.3 has no getOembedUrlFromHTML; the fetched page arrives in the `.then((response) => {` callback (line 135), its oembed link is extracted at line 147 and requested by `externalRequest(oembedUrl, {` (line 159), the SSRF request.
- GHSA-qcg2-h349-vwm3: Line 7 is the whole minified bundle (219k chars); code set to the excerpt of that line rendering the unsanitized link href in the Link decorator.
- GHSA-qxg5-2qff-p49r: Code placeholder replaced by the block's first line.
- GHSA-r3j7-x2g5-9gx6: Location 0 source code corrected to `getFile(path, destination, workingDir) {`.
- GHSA-rhwp-9vm9-547q: File path corrected to src/oled-exp.js.
- GHSA-rwxp-hwwf-653v: Express passes the render locals and the engine options in one object (GHSL-2021-019); options.layout (line 601) goes through layoutPath and cacheLayout to fs.readFile(layoutFile) (line 109), which discloses any file. Was source render() (line 507) and sink template(localsClone, ...) (line 490), the call of the compiled template, which is not a sink; correct_cwe CWE-22 for the file read. `correct_cwe`: ["CWE-22", "CWE-200"].
- GHSA-v756-4whv-48vc: File path corrected to src/messenger-node.js.
- GHSA-vh6r-g38f-q3w8: Code placeholders replaced by each block's first line.
- GHSA-w46j-8hm6-h8mm: Location 0: the innerHTML write (line 192) is the sink; source set to the legend text read `let text = legendFormatter(legendNames[i], ...)` (line 96). Location 1: code corrected to `ttYLabel.innerHTML = seriesName ? seriesName : ''`.
- GHSA-whq6-mj2r-mjqc: File path corrected to lib/lsof.js.
- GHSA-xmxh-g7wj-8m4m: File path corrected to lib/curl-transport.js.

## 4. Removed tool scores

The `tools` field of every review, the scores (A to D) of the vulnerability detection tools of the VulcaN study
(codeql, njsscan, graudit, insidersec, eslint, msdevskim, drek, mosca, odgen, appinspector), is removed, and so is
its description in `dataset/README.md`. The outputs of those tools in `dataset/packages/<id>/` are unchanged.
