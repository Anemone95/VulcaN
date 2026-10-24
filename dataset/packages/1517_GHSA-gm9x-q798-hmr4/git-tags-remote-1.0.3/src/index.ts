import { valid, compare } from 'semver';
import { exec } from 'child_process';

const lsRemoteTags = (repo: string): Promise<string> => new Promise(
	(resolve, reject) => {
		exec(`git ls-remote --tags ${repo}`, (_, stdout, stderr) => {
			if (stderr) reject(new Error(stderr));
			resolve(stdout.toString().trim());
		});
	},
);

const parseTags = (tags: string): Map<string, string> => {
	const tagMap = new Map();
	tags.split('\n')
		.forEach((str) => {
			const ref = str.split(/\t/);
			tagMap.set(ref[1].split('/')[2].replace(/\^\{\}$/, ''), ref[0]);
		});
	return new Map(
		[...tagMap.entries()]
			.filter((arr) => valid(arr[0]))
			.sort((a, b) => compare(a[0], b[0]))
			.reverse(),
	);
};

export const get = async (repo: string): Promise<Map<string, string>> => {
	const tags = await lsRemoteTags(repo);
	return parseTags(tags);
};

export const latest = async (repo: string): Promise<[string, string]> => {
	const tags = await get(repo);
	return tags.entries().next().value as [string, string];
};

module.exports = { get, latest };
