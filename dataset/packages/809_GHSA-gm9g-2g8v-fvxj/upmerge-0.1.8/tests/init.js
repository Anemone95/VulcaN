casesMerge.forEach((item, index) => {

	let testNum = index + 1;

	QUnit.test('Test `Merge` #' + testNum, (assert) => {

		log('---------------------------------------------------');
		log('Test', testNum);
		log('Obj Base', item.base);
		log('Obj Ext ', item.ext);

		let additionalParams = {
			objBase: item.base,
			objBaseStr: JSON.stringify(item.base),
			objExt: item.ext,
			objExtStr: JSON.stringify(item.ext),
			options: item.options
		};

		let result = upmerge.merge(item.base, item.ext, item.options);

		log('Expect  ', item.expect);
		log('Result  ', result);

		//------------------------------
		// Compare result with expected object

		assert.deepEqual(result, item.expect);

		//------------------------------
		// Additional's defaults

		if (!isObject(item.additional)) {
			item.additional = {};
		}

		if (!isSet(item.additional.baseObjChange)) {
			item.additional.baseObjChange = false;
		}

		//------------------------------
		// Apply Additional logic

		if (isFunction(item.additional.func)) {
			let additionalResult = item.additional.func(additionalParams);
			if (isError(additionalResult)) {
				assert.ok(false, additionalResult.message);
			}
		}

		let resultStr = JSON.stringify(result);
		let objExtAfterStr = JSON.stringify(item.ext);
		let objBaseAfterStr = JSON.stringify(item.base);

		if (item.additional.baseObjChange) {
			assert.equal(objBaseAfterStr, resultStr, 'Merge result obj must match original base obj');
		} else {
			assert.equal(objBaseAfterStr, additionalParams.objBaseStr, 'Base object should not be changed after merge');
		}

		//------------------------------

		assert.equal(additionalParams.objExtStr, objExtAfterStr, 'Extending object should not be changed');

	}); // QUnit.test

}); // cases.forEach


casesAdd.forEach((item, index) => {

	let testNum = index + 1;

	QUnit.test('Test `Add` #' + testNum, (assert) => {

		let result = upmerge.add(item.base, item.ext);

		assert.deepEqual(result, item.expect);

	}); // QUnit.test

}); // cases.forEach