import test from 'ava';
import gtr from '.';

const https = 'https://github.com/sh0ji/focus-rover.git';
const invalid = 'github.com/sh0ji/focus-rover';

test('public https get', async (t) => {
	const tags = await gtr.get(https);
	t.is(tags.get('v1.0.0'), '100b2a539ae13406d70a2062bde8d6e4e329fa87');
	t.is(tags.get('v2.0.0'), '7480367b30525107d89aac5ae08cfec991a4e933');
});

test('public https latest', async (t) => {
	const latest = await gtr.latest(https);
	t.is(latest[0], 'v2.0.3');
	t.is(latest[1], 'db0cf6c95dab4c4f9f88d6553ee19fcba3b3b5b9');
});

test('invalid url', async (t) => {
	const error = await t.throwsAsync(gtr.get(invalid));
	t.is(
		error.message,
		`fatal: '${invalid}' does not appear to be a git repository\n`
		+ 'fatal: Could not read from remote repository.\n\n'
		+ 'Please make sure you have the correct access rights\n'
		+ 'and the repository exists.\n',
	);
});
