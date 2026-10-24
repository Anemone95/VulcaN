#!/usr/bin/env python3
"""Replace the VulcaN packages that ship compiled code with their repository source.

The npm tarballs of these packages hold their code, or the annotated file, in dist/, build/ or a bundle, which
jelly-taint does not expand or does not analyze as an entry module. Each package directory
dataset/packages/<id>/<pkg>-<ver>/ is replaced by the repository tree (or the monorepo package directory) at the
commit whose package.json has the same name and version: the gitHead of the npm registry, a version tag, or the
version commit after the gitHead. The tree is a git checkout of that commit (a codeload archive leaves out the
paths that .gitattributes marks export-ignore); no build and no script runs. Afterwards,
misc/taint/vulcan/install.py of jelly-benchmarks (--force --only <id>) installs the production dependencies.

Usage:
  python3 get_source_code.py [--root <VulcaN root>] [--only ID_SUBSTR]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent

# (advisory, package dir, GitHub repository, ref, directory of the package in the repository)
SOURCES = [
    ("1121_GHSA-hx78-272p-mqqh", "graphql-shield-6.0.5", "maticzav/graphql-shield", "v6.0.5", ""),
    ("1176_GHSA-c3m8-x3cg-qm2c", "helmet-csp-2.9.0", "helmetjs/csp", "186abe4cd1c25d64998f7953f9d3f5cf9ea6efb9", ""),
    ("1180_GHSA-6jg8-7333-554w", "realms-shim-1.1.2", "Agoric/realms-shim", "357beba0387c0ac2c4ae20ec524e9dbb56ca0000", ""),
    ("1220_GHSA-5v7r-jg9r-vq44", "simple-crypto-js-2.2.0", "danang-id/simple-crypto-js", "dcf75e0217e8fe58657696ad8408ae8c1cf8c8f7", ""),
    ("1463_GHSA-4r97-78gf-q24v", "klona-1.1.0", "lukeed/klona", "c969b506c4ecf5677050b671ae65e87e49f4facb", ""),
    ("GHSA-8f89-2fwj-5v5r", "klona-1.1.0", "lukeed/klona", "c969b506c4ecf5677050b671ae65e87e49f4facb", ""),
    ("1517_GHSA-gm9x-q798-hmr4", "git-tags-remote-1.0.3", "sh0ji/git-tags-remote", "a21074841b25eb4efe141ea4d7c2a1519c218b90", ""),
    ("751_GHSA-w32g-5hqp-gg6q", "mermaid-8.2.2", "knsv/mermaid", "c33533082c598a0dcd4874e4a7a3365a855950ea", ""),
    ("814_GHSA-6677-83pp-f862", "devalue-1.2.2", "nuxt-community/devalue", "2f286c70034bdd3d08a41373fa3d0e5bd2f4595a", ""),
    ("883_GHSA-fj93-7wm4-8x2g", "jquery-mobile-1.4.1", "jquery/jquery-mobile", "1.4.1", ""),
    ("GHSA-2cf2-2383-h4jv", "querymen-2.1.3", "diegohaz/querymen", "74a634c83d1435d3fa3e56a688577712e23f7f3f", ""),
    ("GHSA-4j46-mp85-mv8c", "rollup-plugin-serve-1.0.1", "thgh/rollup-plugin-serve", "71cc20d4fed8da9f9ab23603b7633b5c2ce49d5c", ""),
    ("GHSA-57f3-gghm-9mhc", "jspdf-2.3.0", "MrRio/jsPDF", "63f89d47d1cd60091e62d6d51570f78f27d01a23", ""),
    ("GHSA-5pm8-492c-92p5", "chartkick-3.1.3", "ankane/chartkick.js", "5334d282d9b8cf36b766b60fd2fe01c200f566db", ""),
    # the gitHead 197aaeb has version 1.0.1; 4a7716e sets 1.0.2 and changes only the readme, license and build/docs
    ("GHSA-5wqj-f379-6jh4", "kill-process-on-port-1.0.2", "radarsu/kill-process-on-port", "4a7716e7cb3060add7e2769e3988f629feb49230", ""),
    ("GHSA-79jw-6wg7-r9g4", "mixme-0.5.0", "adaltas/node-mixme", "00ded06218a813f668946103f7f807ad5d946040", ""),
    ("GHSA-85g2-29m8-qf2p", "object-collider-1.0.3", "FireBlinkLTD/object-collider", "9842609353337a9b1c41a8594d6773bd6cbca6b8", ""),
    ("GHSA-fpm5-vv97-jfwg", "util-0.3.3", "firebase/firebase-js-sdk", "@firebase/util@0.3.3", "packages/util"),
    ("GHSA-jqh7-w5pr-cr56", "koa-shopify-auth-3.1.62", "Shopify/quilt", "@shopify/koa-shopify-auth@3.1.62", "packages/koa-shopify-auth"),
    ("GHSA-jxwx-85vp-gvwm", "jquery-validation-1.19.2", "jquery-validation/jquery-validation", "203b1fa015c30bb53f31776fd4494f5556dc6ad1", ""),
    # the gitHead 4d0aaf6 has version 1.14.4; 9f6f4d2 sets 1.14.5 and changes only dist/ and docs/package.json
    ("GHSA-qcg2-h349-vwm3", "react-draft-wysiwyg-1.14.5", "jpuri/react-draft-wysiwyg", "9f6f4d2d9e0dec2ce8e154d95052fbd395d690af", ""),
    ("GHSA-rrqm-p222-8ph2", "dynamoose-2.6.0", "dynamoose/dynamoose", "255485328e33cfceac5d543f368b2bf4ca4de0dc", ""),
    ("GHSA-xmh9-rg6f-j3mr", "identity-token-verifier-0.5.1", "solid/identity-token-verifier", "0cbb50406717496ecc900d1e3171b2f7ee946a31", ""),
    # packages that also ship their source (TypeScript in src/) or reach the compiled code only through require
    ("100_GHSA-333w-rxj3-f55r", "uri-js-2.1.1", "garycourt/uri-js", "7c1ac11617a1842576d32d4f8f937f8ffb65b2ac", ""),
    # the gitHead 87f1570 has version 1.0.0; b2b233f sets 1.0.1 and changes only package.json
    ("1016_GHSA-c53x-wwx2-pg96", "liljs-1.0.1", "bersLucas/liljs", "b2b233f6042db4ae8796c75fcf7c33c6c9c0776c", ""),
    ("1038_GHSA-4q2f-8g74-qm56", "takeapeek-0.2.2", "giodamelio/takeapeek", "a6778a4b5290e1721964a77d3ce7c9c6b5aae7ba", ""),
    ("1122_GHSA-5mrr-rgp6-x4gr", "marsdb-0.6.11", "c58/marsdb", "33856a1f929d46cbb6b4ea4a463fde3ded0f6278", ""),
    ("124_GHSA-v2jq-9475-r5g8", "bootstrap-tagsinput-0.7.1", "timschlechter/bootstrap-tagsinput", "be96ad787f171fa70e48a6967025dc962f61f31b", ""),
    ("1302_GHSA-h6mq-3cj6-h738", "showdown-1.9.0", "showdownjs/showdown", "8afa1fff0e1de2481e0545be17a906e2a68bb4e2", ""),
    ("139_GHSA-cjj8-wfrx-jqcf", "pivottable-1.6.2", "nicolaskruchten/pivottable", "e9687f56db7ccf6cef084e0fa409c2c3dae35d06", ""),
    ("1488_GHSA-6chw-6frg-f759", "acorn-6.4.0", "acornjs/acorn", "6.4.0", "acorn"),
    ("1518_GHSA-gxr4-xjj5-5px2", "jquery-3.4.1", "jquery/jquery", "3.4.1", ""),
    ("1522_GHSA-9r7h-6639-v5mw", "bootstrap-select-1.13.5", "snapappointments/bootstrap-select", "6950fba020673c94dcc60f3250bee1d0a36c9ba6", ""),
    ("1526_GHSA-w42g-7vfc-xf37", "apollo-server-azure-functions-2.14.1", "apollographql/apollo-server", "2da65ef9204027e43baedf9ce385bb3794fd0c9b", "packages/apollo-server-azure-functions"),
    ("1538_GHSA-5vj8-3v2h-h38v", "next-5.0.0", "vercel/next.js", "4697cbc485855d919ac6c2aef9a433d44b3699b6", ""),
    ("1540_GHSA-r2vw-jgq9-jqx2", "core-1.21.1", "SAP/cloud-sdk", "951e55ca8066cb7ee8c67f4727ecbe51c3b50869", "packages/core"),
    ("326_GHSA-cmh5-qc8w-xvcq", "i18next-3.4.3", "i18next/i18next", "dbf369399e7e3519d7996a2818cbeed89ec2f3f8", ""),
    ("536_GHSA-g36h-6r4f-3mqp", "string-3.3.3", "jprichardson/string.js", "21eb9f67a545d9320558b20876b1551e9f38e52f", ""),
    ("575_GHSA-4qhx-g9wp-g9m6", "squel-5.13.0", "hiddentao/squel", "d76904543849c5f53982db39ab0ae27138635e2d", ""),
    ("648_GHSA-8xqr-4cpm-wx7g", "react-svg-2.2.17", "tanem/react-svg", "9fa13da92cc4c44a10b6e2aced023d3199e8c6bb", ""),
    ("658_GHSA-rvg8-pwq2-xj7q", "base64url-2.0.0", "brianloveswords/base64url", "59b00b9bfa6ca96fb1458f0ebee269dc8f5a14c7", ""),
    ("678_GHSA-pv4c-p2j5-38j4", "url-parse-1.4.1", "unshiftio/url-parse", "89045148cd7adb753c961d05f1fa3acaa8471e74", ""),
    ("740_GHSA-23xp-j737-282v", "takeapeek-0.2.2", "giodamelio/takeapeek", "a6778a4b5290e1721964a77d3ce7c9c6b5aae7ba", ""),
    ("748_GHSA-hgr5-82rc-p936", "md-data-table-2.2.0", "iamisti/mdDataTable", "85f0902f81912208514d5d9b334e90a7cec510fc", ""),
    ("801_GHSA-f8h3-rqrm-47v9", "smart-extend-1.7.4", "danielkalen/smart-extend", "933fc50902d2304eef0f4ff26857842acfe19dc0", ""),
    ("809_GHSA-gm9g-2g8v-fvxj", "upmerge-0.1.8", "jazzfog/UpMerge", "bfbb14e4ff2fa9a9ba002196dbf6944c92b25034", ""),
    ("818_GHSA-98f7-p5rc-jx67", "materialize-css-1.0.0", "Dogfalo/materialize", "80e8ed370487aaf1e2185b028f7deda40da94eb9", ""),
    ("822_GHSA-gh4g-3gm9-5wrq", "shave-2.5.2", "dollarshaveclub/shave", "852b5372baab1d51828cb273c9e5e9d26c536805", ""),
    ("832", "verdaccio-3.11.7", "verdaccio/verdaccio", "0b1b3556d9c043857f9bb789197f6d012876e484", ""),
    ("833_GHSA-78j5-gcmf-vqc8", "verdaccio-3.11.7", "verdaccio/verdaccio", "0b1b3556d9c043857f9bb789197f6d012876e484", ""),
    ("834_GHSA-9w87-4j72-gcv7", "graphql-code-generator-0.18.0", "dotansimha/graphql-codegen", "v0.18.0", "packages/graphql-codegen-cli"),
    ("962_GHSA-9r3m-mhfm-39cm", "bigint-money-0.6.1", "evert/bigint-money", "001aebccfe5c65670e07358de5049a02d28297a0", ""),
    ("986_GHSA-vp93-gcx5-4w52", "swagger-ui-2.2.0", "swagger-api/swagger-ui", "36c5fd89d410f820d2f282e778725968459bb622", ""),
    ("988_GHSA-w992-2gmj-9xxj", "swagger-ui-2.2.0", "swagger-api/swagger-ui", "36c5fd89d410f820d2f282e778725968459bb622", ""),
    ("GHSA-4228-7qvx-f4rq", "devcert-1.1.1", "davewasmer/devcert", "e1389685b9f903b19208cabbe8c80ada33b29cd4", ""),
    ("GHSA-67mm-m3wx-j7fr", "gitlog-4.0.3", "domharrington/node-gitlog", "256a9617fcaa04bba7652ef2a20bc0aa6cc5dbe1", ""),
    ("GHSA-6g8v-hpgw-h2v7", "gsap-3.5.1", "greensock/GSAP", "3.5.1", ""),
    ("GHSA-6hwh-rqwf-cxxr", "vega-util-1.13.0", "vega/vega", "49a57c10b309addc513a52a38e1959ee169d4758", "packages/vega-util"),
    ("GHSA-7752-f4gf-94gc", "materialize-css-1.0.0", "Dogfalo/materialize", "80e8ed370487aaf1e2185b028f7deda40da94eb9", ""),
    ("GHSA-7jh9-6cpf-h4m7", "hellojs-1.18.4", "MrSwitch/hello.js", "3b79ec93781b3d7b9c0b56f598e060301d1f3e73", ""),
    ("GHSA-9qmh-276g-x5pj", "immer-8.0.0", "immerjs/immer", "v8.0.0", ""),
    ("GHSA-c4w7-xm78-47vh", "y18n-5.0.4", "yargs/y18n", "f91f68f5b7ab163d57900b4b25e4b5d0dc5581d0", ""),
    ("GHSA-m428-jqc4-2p5j", "phpjs-1.3.2", "kvz/phpjs", "v1.3.2", ""),
    ("GHSA-pg53-56cg-4m8q", "next-auth-3.2.1", "nextauthjs/next-auth", "v3.2.1", ""),
    ("GHSA-pxcc-hj8w-fmm7", "sdk-2.19.0", "prisma/prisma", "2.19.0", "src/packages/sdk"),
    ("GHSA-qwp9-52h8-xgg8", "jointjs-3.2.0", "clientIO/joint", "a27cf94bab4f96283fb224c14148e7cc67037783", ""),
    ("GHSA-wfw3-rgfr-6g67", "ag-grid-18.1.2", "ag-grid/ag-grid", "18.1.2", "packages/ag-grid"),
    ("GHSA-x56p-c8cg-q435", "next-9.5.3", "vercel/next.js", "b6df8104068fb43fc07183390d661470a3bccb95", "packages/next"),
    ("GHSA-xr9h-9m79-x29g", "rendertron-2.0.1", "GoogleChrome/rendertron", "2d95df8156614a89994bac9b8f76213614caa056", ""),
]

# the release tool of these packages (semantic-release, a publish script) writes the version into package.json when
# it publishes; the repository keeps a placeholder or an older version
VERSION_AT_PUBLISH = {"1121_GHSA-hx78-272p-mqqh", "GHSA-9qmh-276g-x5pj", "GHSA-pg53-56cg-4m8q", "GHSA-pxcc-hj8w-fmm7"}


def download(repo: str, ref: str, subdir: str, dest: Path):
    """Checks out <subdir> of the repository tree at ref to dest (a shallow fetch; blobs come only for <subdir>)."""
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    with tempfile.TemporaryDirectory(dir=dest.parent) as tmp:
        for cmd in (["init", "-q"], ["remote", "add", "origin", f"https://github.com/{repo}"],
                    ["fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", ref],
                    ["-c", "core.autocrlf=false", "-c", "gc.auto=0", "checkout", "-q", "FETCH_HEAD", "--", subdir or "."]):
            subprocess.run(["git", "-C", tmp, *cmd], check=True, env=env, timeout=1200)
        dest.mkdir()
        for e in (Path(tmp) / subdir).iterdir():
            if e.name != ".git":
                shutil.move(e, dest / e.name)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--only", help="only advisories whose id contains this substring")
    args = ap.parse_args()

    for adv, pkg, repo, ref, subdir in SOURCES:
        if args.only and args.only not in adv:
            continue
        target = args.root.resolve() / "dataset" / "packages" / adv / pkg
        new = target.with_name(pkg + ".source")
        shutil.rmtree(new, ignore_errors=True)
        download(repo, ref, subdir, new)
        pj = new / "package.json"
        if adv in VERSION_AT_PUBLISH:
            pj.write_text(re.sub(r'("version"\s*:\s*")[^"]*"', rf'\g<1>{pkg.rsplit("-", 1)[1]}"', pj.read_text(), count=1))
        meta = json.loads(pj.read_text())
        # the package dir is named <name without scope>-<version>
        assert f"{meta['name'].split('/')[-1]}-{meta['version']}" == pkg, (adv, meta["name"], meta["version"])
        shutil.rmtree(target)
        new.rename(target)
        print(f"{adv}/{pkg}: {repo}@{ref}{'/' + subdir if subdir else ''}", flush=True)


if __name__ == "__main__":
    main()
