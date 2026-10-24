/*
	- base: - Base object
	- ext: - Extending object
	- options [Optional]: - Merge options, as in merge function
	- expect: - Expected merge result
	- additional.baseObjChange [Optional]: true - expect that baseObject === result, false - expect that baseObject will not be changed
	- additional.func [Optional]: Function - takes object with test data, if returns Error instance - test fails with specified in Error message
 */

//let logEnable = true;

//### Testing `upmerge.merge` method

let casesMerge = [

	//----------------------------------------------------------

	{
		base: {a: 'A', b: 'B'},
		ext: {c: 'C', d: 'D'},
		options: {
			deep: false
		},
		expect: {a: 'A', b: 'B', c: 'C', d: 'D'}
	},

	//----------------------------------------------------------

	{
		base: {
			a: 'A',
			b: 'B',
			e: {
				ee1: 'EE-1',
				ee2: 'EE-2'
			},
			f: 'F-x'
		},
		ext: {
			c: 'C',
			d: 'D',
			e: {
				eex: 'EE-X'
			},
			f: 'F-y'
		},
		options: {
			deep: false
		},
		expect: {
			a: 'A',
			b: 'B',
			c: 'C',
			d: 'D',
			e: {
				eex: 'EE-X'
			},
			f: 'F-y'
		}
	},

	//----------------------------------------------------------

	{
		base: {
			a: 'A',
			b: 'B',
			e: {
				ee1: 'EE-1',
				ee2: 'EE-2'
			}
		},
		ext: {
			a: 'A',
			b: 'B',
			e: {
				ee1: 'EE-1',
				ee2: 'EE-2',
				ee3: 'EE-3'
			}
		},
		options: {
			replaceOnly: true
		},
		expect: null
	},

	//----------------------------------------------------------

	{
		base: {
			a: 'A',
			b: 'B',
			e: {
				ee1: 'EE-1',
				ee2: 'EE-2'
			}
		},
		ext: {
			c: 'C',
			d: 'D',
			e: {
				eex: 'EE-X'
			}
		},
		expect: {
			a: 'A',
			b: 'B',
			c: 'C',
			d: 'D',
			e: {
				ee1: 'EE-1',
				ee2: 'EE-2',
				eex: 'EE-X'
			}
		}
	},

	//----------------------------------------------------------

	{
		base: {
			a: 'A',
			as: [11, 12, 13, 14, 15],
			b: 'B',
			bingo: 7,
			nxr: null,
			six: 'Lbs',
			e: {
				ee1: 'EE-1',
				ee2: 'EE-2'
			},
			dome: {
				ax: 'Alaska',
				opx: {
					dive: {
						mmx: 'Nor',
						amx: [7, 8, 9]
					}
				}
			},
			holder: {
				ref: {
					alpha: 'Ax',
					beta: 'Bx',
					gamma: 'Gx'
				}
			}
		},
		ext: {
			c: 'C',
			ux: [101, 202, 303],
			d: 'D',
			bingo: {
				play: 1
			},
			nxr: {
				radio: 'FM'
			},
			six: 'Px',
			e: {
				eex: 'EE-X',
				helix: {
					op: 'OP',
					dx: 'DX',
					nx: [1, 3, 5]
				}
			},
			dome: {
				opx: {
					caps: 'String X',
					nova: [111, 222, 333],
					dive: {
						glance: 'Fire'
					}
				}
			},
			isNull: null,
			break: {
				d: new Date(1458252729588),
				n: null,
				e: new Error('Test Message')
			},
			holder: {
				ref: {
					beta: 'Updated'
				}
			}
		},

		expect: {
			a: 'A',
			as: [11, 12, 13, 14, 15],
			b: 'B',
			c: 'C',
			ux: [101, 202, 303],
			d: 'D',
			bingo: {
				play: 1
			},
			nxr: {
				radio: 'FM'
			},
			six: 'Px',
			e: {
				ee1: 'EE-1',
				ee2: 'EE-2',
				eex: 'EE-X',
				helix: {
					op: 'OP',
					dx: 'DX',
					nx: [1, 3, 5]
				}
			},
			dome: {
				ax: 'Alaska',
				opx: {
					caps: 'String X',
					nova: [111, 222, 333],
					dive: {
						mmx: 'Nor',
						amx: [7, 8, 9],
						glance: 'Fire'
					}
				}
			},
			isNull: null,
			break: {
				d: new Date(1458252729588),
				n: null,
				e: new Error('Test Message')
			},
			holder: {
				ref: {
					alpha: 'Ax',
					beta: 'Updated',
					gamma: 'Gx'
				}
			}
		},

		additional: {
			func: (params) => {
				//...
			}
		}
	}

	//----------------------------------------------------------
];


//### Testing `upmerge.add` method

let casesAdd = [

	//----------------------------------------------------------

	{
		base: {
			a: 'A',
			b: 'B',
			e: {
				ee1: 'EE-1',
				ee2: 'EE-2',
				x: 'Y'
			}
		},
		ext: {
			b: 'X',
			e: {
				ee2: 'Yet another'
			}
		},
		expect: {
			a: 'A',
			b: 'X',
			e: {
				ee1: 'EE-1',
				ee2: 'Yet another',
				x: 'Y'
			}
		}
	},

	//----------------------------------------------------------

	{
		base: {
			a: 'A',
			b: 'B',
			e: {
				ee1: 'EE-1',
				ee2: 'EE-2',
				x: 'Y'
			}
		},
		ext: {
			b: 'X',
			newKey: 1,
			e: {
				ee2: 'Yet another'
			}
		},
		expect: null
	},

	//----------------------------------------------------------

	{
		base: {
			a: 'A',
			b: 'B',
			e: {
				ee1: 'EE-1',
				ee2: 'EE-2',
				x: 'Y'
			}
		},
		ext: {
			b: 'X',
			e: {
				ee2: 'Yet another',
				newKey: 1
			}
		},
		expect: null
	}

	//----------------------------------------------------------

];