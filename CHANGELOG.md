# Changelog

All notable changes to this project will be documented in this file.

## [v1.9.2](https://github.com/somaz94/compress-decompress/compare/v1.9.1...v1.9.2) (2026-03-25)

### Features

- delete linters ([da48031](https://github.com/somaz94/compress-decompress/commit/da480315f43c1b0c0d13fbb4971c7edb23e8af1a))
- add extract_pattern, commit_range inputs and match_count output ([b9ede68](https://github.com/somaz94/compress-decompress/commit/b9ede6808b5d68b22a43d13597372c1797e2cec2))

### Bug Fixes

- add subprocess timeout, compression_level validation, and shell injection protection ([433fbf8](https://github.com/somaz94/compress-decompress/commit/433fbf8ae254f9642005b60df4618f734855333d))
- apache license -> mit license ([119cde6](https://github.com/somaz94/compress-decompress/commit/119cde6cda2780200a13e38f8e999f25e57e0cae))
- skip major version tag deletion on first release ([5a8cccf](https://github.com/somaz94/compress-decompress/commit/5a8cccf65b595da4bff2c7e42aea0142cd770691))
- delete linter.yml ([75ec6d5](https://github.com/somaz94/compress-decompress/commit/75ec6d517d973cfcfe637d258210bd5fcaf32e29))
- use git switch in release workflow to avoid branch/file ambiguity ([1c67b82](https://github.com/somaz94/compress-decompress/commit/1c67b82b376ce7f9fee66d9f6b40b2333f26859f))

### Documentation

- add no-push rule to CLAUDE.md ([dfac703](https://github.com/somaz94/compress-decompress/commit/dfac703808809c73fe896b366a59f38ce9d6c6ec))
- update CLAUDE.md with commit guidelines and language ([49ebb5f](https://github.com/somaz94/compress-decompress/commit/49ebb5f39e0dc99408946716d3f6ef6bf636185f))
- add Makefile quick start and coverage report guide to tests/README.md ([54f9c36](https://github.com/somaz94/compress-decompress/commit/54f9c36c9532cff4e5bf8123c04e9628e9b8deba))
- CLAUDE.md ([b2773a3](https://github.com/somaz94/compress-decompress/commit/b2773a320b11fd8a8add81642695529f9abb4122))

### Builds

- **deps:** bump actions/setup-python from 5 to 6 ([795551f](https://github.com/somaz94/compress-decompress/commit/795551f57e62ae3539acc07a2616f4c0bbacb722))

### Continuous Integration

- skip auto-generated changelog and contributors commits in release notes ([fbac132](https://github.com/somaz94/compress-decompress/commit/fbac1322f7ac3f9e5d45df2ca5e28ed4bfcae9a7))
- revert to body_path RELEASE.md in release workflow ([808fbeb](https://github.com/somaz94/compress-decompress/commit/808fbebf9e3a119c6d2d0fb895830b65f6c8b151))
- use generate_release_notes instead of RELEASE.md ([734f158](https://github.com/somaz94/compress-decompress/commit/734f158e451cd2efd122aa7bb8ddd6ee6a8973e6))
- migrate gitlab-mirror workflow to multi-git-mirror action ([ebca98e](https://github.com/somaz94/compress-decompress/commit/ebca98e2717b79962df1544591107191d09247fb))
- use somaz94/contributors-action@v1 for contributors generation ([6c8d50b](https://github.com/somaz94/compress-decompress/commit/6c8d50b22a4ce2e69060b133a4518f4af8a91493))
- use major-tag-action for version tag updates ([1178eb5](https://github.com/somaz94/compress-decompress/commit/1178eb516b99af2dcd44b07156aafac76124bcb2))
- add dependabot auto-merge workflow ([2700c70](https://github.com/somaz94/compress-decompress/commit/2700c70ff0fdd60efd5c66c764b81b003baeef8c))
- unify changelog-generator with flexible tag pattern ([47d2616](https://github.com/somaz94/compress-decompress/commit/47d261697c88741601cb26e0c55f05cbfd3a6b4b))
- use conventional commit message in changelog-generator workflow ([9173af5](https://github.com/somaz94/compress-decompress/commit/9173af5f6af41bad42e432d8a9734890663a3a60))

### Chores

- change license from MIT to Apache 2.0 ([8dff953](https://github.com/somaz94/compress-decompress/commit/8dff953c1d890cff5ce7bc64e9316065c2c04637))
- add Makefile for development workflow ([e824853](https://github.com/somaz94/compress-decompress/commit/e8248535d07c82f4b2fe92ad0d40a7d6716f6433))
- migrate devcontainer feature from devcontainers-contrib to devcontainers-extra ([e4a199f](https://github.com/somaz94/compress-decompress/commit/e4a199fb46fb208c07763e051952b54fbfbab54d))
- add Auto commit skip rule to cliff.toml ([a9a03ae](https://github.com/somaz94/compress-decompress/commit/a9a03aecaba9558cde5c805214854cbfdb8de052))

### Contributors

- somaz

<br/>

## [v1.9.1](https://github.com/somaz94/compress-decompress/compare/v1.9.0...v1.9.1) (2026-03-09)

### Features

- add txz format support and zip password encryption ([00d6cd7](https://github.com/somaz94/compress-decompress/commit/00d6cd7e1b25feaf83000c8b1345700c9a66b0b0))
- add checksum output, compression_level input, and file_path output ([4a855a3](https://github.com/somaz94/compress-decompress/commit/4a855a372d70635b9f7944808f3466691483f0db))

### Bug Fixes

- .github/workflows/release.yml ([d1b126c](https://github.com/somaz94/compress-decompress/commit/d1b126c872201f9ad4241dad12d3bc335d0d4cdf))

### Contributors

- somaz

<br/>

## [v1.9.0](https://github.com/somaz94/compress-decompress/compare/v1.8.4...v1.9.0) (2026-03-09)

### Code Refactoring

- .github/workflows ([173ca1e](https://github.com/somaz94/compress-decompress/commit/173ca1ec02e20ccdd9db29e4235af72cf2c379b1))
- app & docs: README.md & add: test code ([406ea30](https://github.com/somaz94/compress-decompress/commit/406ea30ecb42af2a6255dc5a6da329c75d24ef50))
- app/compress, main, utils ([8455648](https://github.com/somaz94/compress-decompress/commit/84556487f760b47e760769061372d4bce60c83e6))

### Documentation

- README.md ([2c03e37](https://github.com/somaz94/compress-decompress/commit/2c03e374151454696e262772120f464be3025205))
- README.md, docs/README.md ([63ab52b](https://github.com/somaz94/compress-decompress/commit/63ab52bb42854a6a80f30048d6f21fedec59647b))

### Builds

- **deps:** bump actions/upload-artifact from 6 to 7 ([13be008](https://github.com/somaz94/compress-decompress/commit/13be008ebe535f89b5ff1dc3c8955df656674b24))
- **deps:** bump super-linter/super-linter in the actions-minor group ([84a726c](https://github.com/somaz94/compress-decompress/commit/84a726c03a0288e521ea39cf47899ac6868a06b3))
- **deps:** bump super-linter/super-linter in the actions-minor group ([b949029](https://github.com/somaz94/compress-decompress/commit/b94902949ee04d7b71b2f28fe18d15fc0a9d86ee))
- **deps:** bump super-linter/super-linter in the actions-minor group ([1baeb93](https://github.com/somaz94/compress-decompress/commit/1baeb938ad19b3d998294b660024aa68c4ac0f0e))
- **deps:** bump super-linter/super-linter in the actions-minor group ([3221296](https://github.com/somaz94/compress-decompress/commit/3221296065ecc7925c75e7d8ee7f772891c99200))
- **deps:** bump actions/upload-artifact from 5 to 6 ([8ea0387](https://github.com/somaz94/compress-decompress/commit/8ea0387e2d819cbed50967bfae0e9a39253b006e))
- **deps:** bump super-linter/super-linter in the actions-minor group ([a8af3bd](https://github.com/somaz94/compress-decompress/commit/a8af3bd5f70809d8fdc738fdc272e7fc87938a61))
- **deps:** bump actions/checkout from 5 to 6 ([c664e0d](https://github.com/somaz94/compress-decompress/commit/c664e0df08b35b19cb912448a67f63f76cbeac58))
- **deps:** bump actions/upload-artifact from 4 to 5 ([4702624](https://github.com/somaz94/compress-decompress/commit/4702624cb884eb4f82b10a8438b2d42e8054defc))

### Chores

- contributors.yml ([3cb75b9](https://github.com/somaz94/compress-decompress/commit/3cb75b9dd359d3fc7abe28c3255bd2366a754e70))
- dockerignore ([7fbdc6e](https://github.com/somaz94/compress-decompress/commit/7fbdc6e95ab1ec485e2b6df5a935c094f776451e))
- release.yml ([205e062](https://github.com/somaz94/compress-decompress/commit/205e06281abf77cd7fce7ffacd3e391b4be49dfb))
- workflows ([cff2654](https://github.com/somaz94/compress-decompress/commit/cff26545f4524106c26057a4b684815d55e07974))

### Contributors

- somaz

<br/>

## [v1.8.4](https://github.com/somaz94/compress-decompress/compare/v1.8.3...v1.8.4) (2025-10-22)

### Code Refactoring

- utils.py ([0505086](https://github.com/somaz94/compress-decompress/commit/050508696be170f3917f26dda5575a0a2857602a))

### Chores

- imoji ([2d0bfda](https://github.com/somaz94/compress-decompress/commit/2d0bfda4096a34741a22ffc2672414167aa52e38))

### Contributors

- somaz

<br/>

## [v1.8.3](https://github.com/somaz94/compress-decompress/compare/v1.8.2...v1.8.3) (2025-10-21)

### Code Refactoring

- compress,py, main.py, utils.py ([cb1923c](https://github.com/somaz94/compress-decompress/commit/cb1923cf2c26cb39e7dfa6d69ed6fbf494719744))

### Contributors

- somaz

<br/>

## [v1.8.2](https://github.com/somaz94/compress-decompress/compare/v1.8.1...v1.8.2) (2025-10-21)

### Code Refactoring

- utils.py ([c93b615](https://github.com/somaz94/compress-decompress/commit/c93b615ddc8ac4830ca883d30ccb1d9a4968e2fe))

### Builds

- **deps:** bump actions/github-script from 7 to 8 ([1d3e377](https://github.com/somaz94/compress-decompress/commit/1d3e3771233b15b75cc299b0667728b6226e2269))
- **deps:** bump actions/stale from 9 to 10 ([953678d](https://github.com/somaz94/compress-decompress/commit/953678d289c4fe3bcf34cca01b09ef007d969741))
- **deps:** bump super-linter/super-linter in the actions-minor group ([7acc4b8](https://github.com/somaz94/compress-decompress/commit/7acc4b8fd911e62924f30cd6eda9ea64fbd5239f))

### Contributors

- somaz

<br/>

## [v1.8.1](https://github.com/somaz94/compress-decompress/compare/v1.8.0...v1.8.1) (2025-10-20)

### Documentation

- README.md, docs/GLOB_PATTERNS.md & chore: use-action.yml ([702da61](https://github.com/somaz94/compress-decompress/commit/702da61b328f005135c5b7e46d6ec051bfaeb63c))
- docs/GLOB_PATTERNS.md ([f94c556](https://github.com/somaz94/compress-decompress/commit/f94c556e7d2fb61220599c6013ab983a27fc7ab9))

### Chores

- add symlink-support ([a04fdb6](https://github.com/somaz94/compress-decompress/commit/a04fdb6b680e5b605c650c41e035eec52275c469))
- action.yml icon ([4d473fa](https://github.com/somaz94/compress-decompress/commit/4d473fafdca6311ede2ed5e92ef69491f566074e))
- add issue-greeting.yml & stale-issues.yml ([a6ef771](https://github.com/somaz94/compress-decompress/commit/a6ef771c5554187e3bae89c3d101f2f46251bc06))

### Contributors

- somaz

<br/>

## [v1.8.0](https://github.com/somaz94/compress-decompress/compare/v1.7.0...v1.8.0) (2025-10-20)

### Chores

- use-action.yml, docs: README.md, docs/GLOB_PATTERNS.md ([2adcf01](https://github.com/somaz94/compress-decompress/commit/2adcf018cd03051acdebaffeccc2ad055ebc0712))
- ci.yml ([be21c56](https://github.com/somaz94/compress-decompress/commit/be21c56b0e6fe4dc8e2a09d4171c7f983a044889))
- add stripPrefix ([c1f7964](https://github.com/somaz94/compress-decompress/commit/c1f7964078f3dbe470fe28837151cd27785ef7a6))

### Contributors

- somaz

<br/>

## [v1.7.0](https://github.com/somaz94/compress-decompress/compare/v1.6.0...v1.7.0) (2025-10-20)

### Documentation

- README.md, docs/GLOB_PATTERNS.md ([1aa03ba](https://github.com/somaz94/compress-decompress/commit/1aa03baff744d910f61dcf7e38688bc56b1abc5b))
- README.md, docs ([f189748](https://github.com/somaz94/compress-decompress/commit/f189748e23898dc0e2d460f8498dbf2a13fdb944))
- README.md ([5df2c1a](https://github.com/somaz94/compress-decompress/commit/5df2c1a0580133140a3b758d275fb09518616fb9))

### Chores

- use-action.yml ([aed1bb0](https://github.com/somaz94/compress-decompress/commit/aed1bb0bec5b7baa0260c258ca6d0af0298974bf))
- ci.yml ([59b457a](https://github.com/somaz94/compress-decompress/commit/59b457a98822c14e1985138c5c9e194bbffba6a6))
- ci.yml ([cbe9afb](https://github.com/somaz94/compress-decompress/commit/cbe9afbc6b5532d7f98c42e8eda0a9bd5f51307c))
- add Preserve Structure true/false ([c131183](https://github.com/somaz94/compress-decompress/commit/c131183b5b07e8aeaa51a11a5d745be1596c5cc3))

### Contributors

- somaz

<br/>

## [v1.6.0](https://github.com/somaz94/compress-decompress/compare/v1.5.1...v1.6.0) (2025-10-20)

### Builds

- **deps:** bump python in the docker-minor group ([d79cea7](https://github.com/somaz94/compress-decompress/commit/d79cea7c9e8d3f6ad380a3b3265f51cf3b8ee5e9))
- **deps:** bump super-linter/super-linter in the actions-minor group ([c57fab7](https://github.com/somaz94/compress-decompress/commit/c57fab7d059e0fbd756f5be2ae631dd254da137b))
- **deps:** bump actions/checkout from 4 to 5 ([7fd5453](https://github.com/somaz94/compress-decompress/commit/7fd5453e0763687e70c33dccabea51979ff59235))
- **deps:** bump super-linter/super-linter in the actions-minor group ([2153db8](https://github.com/somaz94/compress-decompress/commit/2153db8f279f3f004a5d08a752f1c487f905015a))
- **deps:** bump super-linter/super-linter from 7.4.0 to 8.0.0 ([8ea30df](https://github.com/somaz94/compress-decompress/commit/8ea30df13ea4de926a52f71cd9cbe2777d30bc6d))
- **deps:** bump super-linter/super-linter in the actions-minor group ([1622250](https://github.com/somaz94/compress-decompress/commit/162225035a6d3c39a68491aee271edbb783d29c0))

### Chores

- use-action.yml , README.md ([ada8e08](https://github.com/somaz94/compress-decompress/commit/ada8e08462269ebccdf27410ae22f0989afa6630))
- ci.yml ([1c323b6](https://github.com/somaz94/compress-decompress/commit/1c323b67cc88e0463dd4ff237ed4f81521a7e07e))
- add glob pattern ([ea4410a](https://github.com/somaz94/compress-decompress/commit/ea4410a4deb92903d3c589e28d4b1cbabad513bd))

### Contributors

- somaz

<br/>

## [v1.5.1](https://github.com/somaz94/compress-decompress/compare/v1.5.0...v1.5.1) (2025-04-15)

### Bug Fixes

- main.py ([7948d78](https://github.com/somaz94/compress-decompress/commit/7948d787f9c56d97f6a17faa1c7707f5fc77298e))
- use-action.yml, utils.py ([cdd7f98](https://github.com/somaz94/compress-decompress/commit/cdd7f983fec6deb5c806bccb16c6220cc7a4816f))
- decompress.py ([f250f0a](https://github.com/somaz94/compress-decompress/commit/f250f0a7e32fc1af77bfe3d8294eee9b8f058940))
- ci.yml ([e4332d4](https://github.com/somaz94/compress-decompress/commit/e4332d42f4bd47e48f13734535548f86000ffce1))
- ci.yml, compress.py ([be612bb](https://github.com/somaz94/compress-decompress/commit/be612bbd4e00d5c370211f0a08d4c7b98d1c07db))
- compress.py ([8864704](https://github.com/somaz94/compress-decompress/commit/8864704e3003bf11e0060a69f0b9d0090391d1fd))
- contributors.yml ([6c2d52a](https://github.com/somaz94/compress-decompress/commit/6c2d52a2e6754583e54e5a448ec2be8885f2082d))
- ci.yml, use-action.yml ([25f67be](https://github.com/somaz94/compress-decompress/commit/25f67be8f827bb90983324b58361191e58d5ea8a))
- changelog-generator.yml ([5fe1edf](https://github.com/somaz94/compress-decompress/commit/5fe1edfaed024191941863dca919e49f17977f0b))
- changelog-generator.yml ([84c2982](https://github.com/somaz94/compress-decompress/commit/84c2982d038d1b55d44385a635257c736a62f7c7))
- changelog-generator.yml ([175787d](https://github.com/somaz94/compress-decompress/commit/175787dd4d96f7e4bd34c0cb81f0ffe60af4bcf6))
- changelog-generator.yml ([e98011e](https://github.com/somaz94/compress-decompress/commit/e98011e1419fd8cdbfae724b622240356e80fd2c))
- changelog-generator.yml ([f63dae7](https://github.com/somaz94/compress-decompress/commit/f63dae72a48d074705b782b27cebcda030cb5c48))
- changelog-generator.yml ([477b867](https://github.com/somaz94/compress-decompress/commit/477b867a1d56f07fcd348ab87e6e637047cc40ea))
- README.md, use-action.yml ([8137599](https://github.com/somaz94/compress-decompress/commit/8137599e3a46e66664e5d887dc95cbcc464fbaec))

### Documentation

- README.md ([6f5191d](https://github.com/somaz94/compress-decompress/commit/6f5191d5f773db17a803debdae752354e4ca6684))

### Contributors

- somaz

<br/>

## [v1.5.0](https://github.com/somaz94/compress-decompress/compare/v1.4.2...v1.5.0) (2025-04-11)

### Bug Fixes

- compress.py ([f5cb80c](https://github.com/somaz94/compress-decompress/commit/f5cb80c41318cbc4fe933f209c42e4e3e3731b6d))
- compress.py ([d563865](https://github.com/somaz94/compress-decompress/commit/d56386599c90351b9033e9cf9ebb94deec9d40d2))
- compress.py ([0677dee](https://github.com/somaz94/compress-decompress/commit/0677dee61fdef7a8c509da66864faa851b48185a))
- ci.yml ([d5fb413](https://github.com/somaz94/compress-decompress/commit/d5fb4132b09b54b06013a93b541c85987ef490f0))

### Contributors

- Fabio Grande
- somaz

<br/>

## [v1.4.2](https://github.com/somaz94/compress-decompress/compare/v1.4.1...v1.4.2) (2025-04-08)

### Bug Fixes

- use-action.yml ([cf12f9f](https://github.com/somaz94/compress-decompress/commit/cf12f9f4213f86b9b1158b7a00d474e4cb82ed8a))
- use-action.yml ([de2f6ff](https://github.com/somaz94/compress-decompress/commit/de2f6ffc949d2f99a63a7c1ae9f6347cddd4e216))
- use-action.yml ([fd7dcab](https://github.com/somaz94/compress-decompress/commit/fd7dcab779de05184d0e73033af485b84aac3c0b))
- changelog-generator.yml ([1236b3c](https://github.com/somaz94/compress-decompress/commit/1236b3c811d68ca2ad34bd4f82633ab049707331))

### Contributors

- somaz

<br/>

## [v1.4.1](https://github.com/somaz94/compress-decompress/compare/v1.4.0...v1.4.1) (2025-04-04)

### Bug Fixes

- app/* ([e529a7d](https://github.com/somaz94/compress-decompress/commit/e529a7d1142cbc00b8bfe3c275fe33b389111c57))
- use-action.yml ([151e153](https://github.com/somaz94/compress-decompress/commit/151e1534ff3ef711ce7a58e2f483a32496bc1fa9))
- compress.py ([a4267f8](https://github.com/somaz94/compress-decompress/commit/a4267f8e4a853177e684523057d1e32828b62e7c))
- compress.py, utils.py ([86d8126](https://github.com/somaz94/compress-decompress/commit/86d8126868f188ad6a53c2c00f5904d6d15eb0ec))
- compress.py, ci.yml ([ba53339](https://github.com/somaz94/compress-decompress/commit/ba533395591237e57972f3d51e9a5c59e4c0c095))
- app/utils.py ([d63599f](https://github.com/somaz94/compress-decompress/commit/d63599f4429709da89ef85848ec7a1dcf59da0bb))
- app/utils.py ([6d8b411](https://github.com/somaz94/compress-decompress/commit/6d8b41104bde7bc8a8f466ee55e6760f87b30cb2))
- ci.yml, use-action.yml ([dddfcb0](https://github.com/somaz94/compress-decompress/commit/dddfcb038647e343d2510ab14a07d755f980fe69))
- ci.yml, app/utils.py ([780d664](https://github.com/somaz94/compress-decompress/commit/780d664c58d9b5d8766947d58e8431fd804abc6f))
- use-action.yml ([3aa600f](https://github.com/somaz94/compress-decompress/commit/3aa600fdec1083533bc30c522c5be0999df88ff7))

### Documentation

- README.md ([8b8ad5b](https://github.com/somaz94/compress-decompress/commit/8b8ad5b50b0db482d7151ab822d084fd1bc42c86))

### Contributors

- somaz

<br/>

## [v1.4.0](https://github.com/somaz94/compress-decompress/compare/v1.3.1...v1.4.0) (2025-04-03)

### Bug Fixes

- contributors.yml ([c61b13f](https://github.com/somaz94/compress-decompress/commit/c61b13f4497a18767a8737afbda8cee5e2d1c249))
- contributors.yml ([7709c70](https://github.com/somaz94/compress-decompress/commit/7709c70ff89adac04903b9d3993e090598d10a8c))
- contributors.yml ([01cdcfc](https://github.com/somaz94/compress-decompress/commit/01cdcfc0c29d3fd8173b489f67455979278576a6))
- contributors.yml ([25ae63a](https://github.com/somaz94/compress-decompress/commit/25ae63a8c6c510215b63c58f3c0b1a5be6689135))
- contributors.yml ([db85a51](https://github.com/somaz94/compress-decompress/commit/db85a513999f0a77f2ebe7e07d122bc5069cf7c6))
- contributors.yml ([4b8772c](https://github.com/somaz94/compress-decompress/commit/4b8772cdaf3da53a1e52c1b7a839c44922ea9796))
- contributors.yml ([d30296f](https://github.com/somaz94/compress-decompress/commit/d30296f764735d4582a9951d83b5b18ff24917ee))
- contributors.yml ([5e5f7fd](https://github.com/somaz94/compress-decompress/commit/5e5f7fd1667cccafeb766678f4d66bc0e52ccf5b))
- contributors.yml ([ead00d8](https://github.com/somaz94/compress-decompress/commit/ead00d83882d854036433de17e48dc0bee85795b))
- contributors.yml ([5ec333a](https://github.com/somaz94/compress-decompress/commit/5ec333a82bb00320cc67f9e03188fffcb92f91cb))
- contributors.yml ([9da0f56](https://github.com/somaz94/compress-decompress/commit/9da0f56d9cb41283ceec446f9792f2eeb529212e))
- contributors.yml ([9d13cfa](https://github.com/somaz94/compress-decompress/commit/9d13cfa257901aea28b5c13cfe6948b680b9572f))
- use-action.yml, README.md ([c543cbb](https://github.com/somaz94/compress-decompress/commit/c543cbbde4d6561ab4df44b4d8e028363eb445dc))
- compress.py ([c2406a7](https://github.com/somaz94/compress-decompress/commit/c2406a7f27cbbf45d53bf7a07f2b900204206143))
- ci.yml, compress.py ([ad2100e](https://github.com/somaz94/compress-decompress/commit/ad2100e9e474fad5bab81f7f753201ac153e435d))
- ci.yml, compress.py ([84eaebf](https://github.com/somaz94/compress-decompress/commit/84eaebf9fc254a486ddcc9a6ecc76e0c7c38c80b))
- compress.py, main.py ([04da2c3](https://github.com/somaz94/compress-decompress/commit/04da2c3422ecd88e840f02882e470b5b8d2439a3))
- ci.yml ([9979e3d](https://github.com/somaz94/compress-decompress/commit/9979e3da085dfec4f5dfee7455f96ecd1c16e605))
- ci.yml, contributors.yml ([f430b36](https://github.com/somaz94/compress-decompress/commit/f430b3642dae4b464bef5fd9ef9e3985c0560f83))
- ci.yml, contributors.yml ([89c9768](https://github.com/somaz94/compress-decompress/commit/89c97683d1fc60fd82308ba158e091148cc29174))
- ci.yml, add: contributors.yml ([070ef59](https://github.com/somaz94/compress-decompress/commit/070ef5961d996cc6c1b37065d0e2399a3fcf9b09))
- ci.yml ([aa56281](https://github.com/somaz94/compress-decompress/commit/aa5628181027a6298d560508e02975678b5b9cd2))

### Add

- contributors.yml ([a3fed2b](https://github.com/somaz94/compress-decompress/commit/a3fed2bef3fc5eb44f479c54c325074b21a27ce4))

### Delete

- contributors.yml ([0d5b890](https://github.com/somaz94/compress-decompress/commit/0d5b890b5d9f35f7b3e1ef6c23d94689e4b822ad))

### Contributors

- Fabio Grande
- somaz

<br/>

## [v1.3.1](https://github.com/somaz94/compress-decompress/compare/v1.3.0...v1.3.1) (2025-03-04)

### Bug Fixes

- compress,decompress,main,utils.py ([2fe77e9](https://github.com/somaz94/compress-decompress/commit/2fe77e95a8fb0648ce99457bd50443d6affe6e22))
- backup/compress,decompress,main,utils.py ([50ffe9f](https://github.com/somaz94/compress-decompress/commit/50ffe9f5c600d4461e7b822df519838c1805f737))
- changelog-generator.yml ([0580451](https://github.com/somaz94/compress-decompress/commit/0580451f99a283b0e50901f94ed5cdaa478154cf))

### Builds

- **deps:** bump super-linter/super-linter in the actions-minor group ([9689ce2](https://github.com/somaz94/compress-decompress/commit/9689ce28d1343dc57a2a16bdf5730524da49a0e8))

### Add

- gitlab-mirror.yml ([f5bcbc1](https://github.com/somaz94/compress-decompress/commit/f5bcbc1fd20866b180054cd045159439360d28ee))

### Contributors

- somaz

<br/>

## [v1.3.0](https://github.com/somaz94/compress-decompress/compare/v1.2.0...v1.3.0) (2025-02-17)

### Bug Fixes

- app/* ([71a7e51](https://github.com/somaz94/compress-decompress/commit/71a7e5119e7ebb176f9f948271adc282f2b88051))
- app/* ([4e23616](https://github.com/somaz94/compress-decompress/commit/4e23616239ed8a54f542688e939844d61b2dbeb7))
- app/* ([0a48bc2](https://github.com/somaz94/compress-decompress/commit/0a48bc27bb72936b18aa4f3e21277e6e88e2474f))
- app/utils.py ([595f050](https://github.com/somaz94/compress-decompress/commit/595f050969518094b6d82284b1c6aa20dbae7788))
- backup ([026a571](https://github.com/somaz94/compress-decompress/commit/026a5712cef0bb58183a4549f37caa91c148af3d))
- changelog-generator.yml ([ebdcf3d](https://github.com/somaz94/compress-decompress/commit/ebdcf3dbacdc5a00451719f893a71144d19fc89e))

### Chores

- Code advancement ([5c1cda7](https://github.com/somaz94/compress-decompress/commit/5c1cda74a4fbf552360f20d46197e276fde770be))

### Contributors

- somaz

<br/>

## [v1.2.0](https://github.com/somaz94/compress-decompress/compare/v1.1.0...v1.2.0) (2025-02-17)

### Bug Fixes

- compress.py, decompress.py, utils.py ([e891154](https://github.com/somaz94/compress-decompress/commit/e8911546eee45ededaa0a9adbc5b18b090bfb3a1))
- ci.yml, use-action.yml ([54c12f4](https://github.com/somaz94/compress-decompress/commit/54c12f440fe247a140678735bec4a3a35dad5cc1))
- compress.py & decompress.py ([a90afd7](https://github.com/somaz94/compress-decompress/commit/a90afd7dbfe42a683b55ca63f2d5309cdbe3574f))

### Add

- input verbose, fail_on_error ([d1a3ff4](https://github.com/somaz94/compress-decompress/commit/d1a3ff47d6afc09441d4357fbf319d6225fb552c))

### Contributors

- somaz

<br/>

## [v1.1.0](https://github.com/somaz94/compress-decompress/compare/v1.0.8...v1.1.0) (2025-02-14)

### Bug Fixes

- app/* ([ae9fa29](https://github.com/somaz94/compress-decompress/commit/ae9fa29dbbba9769a12f9b7a17ba0ffc4fbf0e83))
- compress.py ([c045f91](https://github.com/somaz94/compress-decompress/commit/c045f91407a3db38e996d7d135b1f76b968b796d))
- compress.py ([0394c06](https://github.com/somaz94/compress-decompress/commit/0394c063907849bfb4010915c617a6b482f5baed))
- compress.py ([be2a34e](https://github.com/somaz94/compress-decompress/commit/be2a34e4b451649a8413a80ad7253b7b2e6e57b4))
- compress.py ([36102cf](https://github.com/somaz94/compress-decompress/commit/36102cf135e86af04444b84bc6177d6b2fbc90f4))
- compress.py ([a2006cf](https://github.com/somaz94/compress-decompress/commit/a2006cf4af16d470f72e361a99e6e00152a3a9db))
- compress.py ([cadbcdb](https://github.com/somaz94/compress-decompress/commit/cadbcdb470770b8a657fb63aabf7efc527b7b265))
- ci.yml ([9e1d526](https://github.com/somaz94/compress-decompress/commit/9e1d5269055a12fbab422ccb5148cbd054660763))
- ci.yml ([6b0ccf5](https://github.com/somaz94/compress-decompress/commit/6b0ccf537ae7ad2eb6081106d5106d50e7d98608))
- compress.py, decompress,py, ci.yml ([1f0f498](https://github.com/somaz94/compress-decompress/commit/1f0f498bbc3fef56dd047e31b12be5601d5fffc5))
- workflow ([cb988c9](https://github.com/somaz94/compress-decompress/commit/cb988c9009393cb2eeb05a218216565539128cd2))
- ci.yml ([d852048](https://github.com/somaz94/compress-decompress/commit/d852048c155c58f8901f156e2b9329e7f82c1d84))

### Documentation

- README.md ([72755d7](https://github.com/somaz94/compress-decompress/commit/72755d7e41f66cacedbe950ac98eaec48f117b7f))

### Contributors

- somaz

<br/>

## [v1.0.8](https://github.com/somaz94/compress-decompress/compare/v1.0.7...v1.0.8) (2025-02-13)

### Bug Fixes

- Dockerfile ([a5efc06](https://github.com/somaz94/compress-decompress/commit/a5efc063f3e13101f48230f7eaa0b93870df8419))

### Contributors

- somaz

<br/>

## [v1.0.7](https://github.com/somaz94/compress-decompress/compare/v1.0.6...v1.0.7) (2025-02-12)

### Bug Fixes

- Dockerfile ([027c778](https://github.com/somaz94/compress-decompress/commit/027c778105690c2e2343cd82bcdfeaa76c6472c6))
- Dockerfile ([60d7065](https://github.com/somaz94/compress-decompress/commit/60d70655b4d5508aa250d29247da956bf77c1ef3))
- Dockerfile ([4ed2a38](https://github.com/somaz94/compress-decompress/commit/4ed2a38c55369031d96bb6a246d784c9501150a8))
- Dockerfile ([49bd621](https://github.com/somaz94/compress-decompress/commit/49bd6219797b02affe132afaab7194d570046ef5))
- Dockerfile ([ae75460](https://github.com/somaz94/compress-decompress/commit/ae75460b670c86973ea61edf523ecbad2f84bdb4))
- app/*.py ([4069a88](https://github.com/somaz94/compress-decompress/commit/4069a886f00d21931c8bd689303947e5f2632bed))
- app/main.py ([a75561e](https://github.com/somaz94/compress-decompress/commit/a75561ee0a1d90610838f993d942b1aa437fac09))
- file-structure ([8d23ebc](https://github.com/somaz94/compress-decompress/commit/8d23ebc761cdf2475ec7d9c0a7d57a79c2945360))
- ci, ci-v2.yml ([a7b7e36](https://github.com/somaz94/compress-decompress/commit/a7b7e369c845caeaafcb760596cd3a7f81c24dd0))
- Dockerfile , create backup directory ([3488de7](https://github.com/somaz94/compress-decompress/commit/3488de7c0b1237b71acd2e1ca816d22960311eba))
- action.yml ([d3bd9d9](https://github.com/somaz94/compress-decompress/commit/d3bd9d9c3a2ff3367cf0fd5fc92020a37ef02bf3))

### Contributors

- somaz

<br/>

## [v1.0.6](https://github.com/somaz94/compress-decompress/compare/v1.0.5...v1.0.6) (2025-02-07)

### Bug Fixes

- use-action.yml ([2d75a5b](https://github.com/somaz94/compress-decompress/commit/2d75a5b68e61f3c19033b999210a2e8a2c309f94))
- changelog-generator.yml ([72648a5](https://github.com/somaz94/compress-decompress/commit/72648a5dfb686bcb21771ae1cdcfd6bfa31fe3f8))
- changelog-generator.yml ([7383a16](https://github.com/somaz94/compress-decompress/commit/7383a1682b56802ddf2777d40f831549de2711e1))

### Contributors

- somaz

<br/>

## [v1.0.5](https://github.com/somaz94/compress-decompress/compare/v1.0.4...v1.0.5) (2025-02-07)

### Bug Fixes

- entrypoint.py ([bb63711](https://github.com/somaz94/compress-decompress/commit/bb63711823a440cdfb0d1d2b86d8bc8554f1fcde))
- entrypoint.py ([d3b9d8a](https://github.com/somaz94/compress-decompress/commit/d3b9d8af0848ffb3f91852b58588865e10948e50))

### Contributors

- somaz

<br/>

## [v1.0.4](https://github.com/somaz94/compress-decompress/compare/v1.0.3...v1.0.4) (2025-02-07)

### Bug Fixes

- entrypoint.py ([d039b60](https://github.com/somaz94/compress-decompress/commit/d039b605eb273aa8375cf24bb9380c13b1516c8f))
- release.yml ([b7e2abc](https://github.com/somaz94/compress-decompress/commit/b7e2abc7b769148f4f1642245622b3ffd3fbc5e5))
- release.yml ([87d3b9a](https://github.com/somaz94/compress-decompress/commit/87d3b9ab13da904ee55001d89dd77857ba133480))
- release.yml & changelog-generator.yml ([e3ac3bb](https://github.com/somaz94/compress-decompress/commit/e3ac3bb68cd80a5297d8e66ccb99c5d913c11c4f))
- changelog-generator.yml ([1d9de7c](https://github.com/somaz94/compress-decompress/commit/1d9de7c6b713c68c2720c54a2f641b5bd6d9a36f))

### Documentation

- README.md ([1871cd2](https://github.com/somaz94/compress-decompress/commit/1871cd2f3893a39c821f02f299a3beaea5d5b6f2))
- CODEOWNERS ([10bcbd8](https://github.com/somaz94/compress-decompress/commit/10bcbd8d5d24a6875c7bc2475b1cee680cb769e7))
- README.md ([c2ad716](https://github.com/somaz94/compress-decompress/commit/c2ad716e9b52c80dc5365e5b3d31b959185a0684))
- README.md ([301c681](https://github.com/somaz94/compress-decompress/commit/301c681e2844a986f3d0a9c9f370ae942a4f7466))
- RADEME.md ([d54b6c8](https://github.com/somaz94/compress-decompress/commit/d54b6c8b97e977d5410de5f4a27f0c0f75bbc1f9))

### Builds

- **deps:** bump janheinrichmerker/action-github-changelog-generator ([5a04c76](https://github.com/somaz94/compress-decompress/commit/5a04c76f3c744e0dca17bfd5b9d5b48c461bba24))
- **deps:** bump super-linter/super-linter in the actions-minor group ([eea1ff9](https://github.com/somaz94/compress-decompress/commit/eea1ff9eb80f9390dca5806346d6437324377466))
- **deps:** bump super-linter/super-linter in the actions-minor group ([3f587fa](https://github.com/somaz94/compress-decompress/commit/3f587fa99c2404e5657be4e2c75fbabca0d462c4))

### Chores

- fix changelog-generator.yml ([0f9613d](https://github.com/somaz94/compress-decompress/commit/0f9613d90da3fac31b9edaac4f72e2bcad150545))
- fix changelog workflow ([51dc415](https://github.com/somaz94/compress-decompress/commit/51dc4152ba18e20b8b912f5ab480abc20379bf8a))
- fix changelog workflow ([a722ddd](https://github.com/somaz94/compress-decompress/commit/a722ddd9e8e7b83aa933656bb483075118fad183))
- fix changelog workflow ([402b13f](https://github.com/somaz94/compress-decompress/commit/402b13fb62b764dd670dc5b0237d303b196267aa))
- fix changelog workflow ([9fe771b](https://github.com/somaz94/compress-decompress/commit/9fe771bd283902405e16eb9e1b9958065d869167))
- fix workflow ([dd3fc3a](https://github.com/somaz94/compress-decompress/commit/dd3fc3a4c261ecc99e0f4364b20ffd132fc69df0))
- delete linter workflow ([f835486](https://github.com/somaz94/compress-decompress/commit/f8354864410a35f963d66b62d08c8df5f5f3fc24))
- add changelog generator workflow ([c0447f5](https://github.com/somaz94/compress-decompress/commit/c0447f5b1cfa14ece7dc565f1b38c5ef0cf8d554))
- add changelog generator workflow ([4707cb4](https://github.com/somaz94/compress-decompress/commit/4707cb46a2396d6baa9949af6e4a9c2a7f0fe875))

### Add

- release.yml ([a14a0ac](https://github.com/somaz94/compress-decompress/commit/a14a0ac407db6a63ee9763d225d7fb03446482a0))

### Contributors

- somaz

<br/>

## [v1.0.3](https://github.com/somaz94/compress-decompress/compare/v1.0.2...v1.0.3) (2024-10-28)

### Bug Fixes

- .checkov.yml -> .checkov.yaml ([908720a](https://github.com/somaz94/compress-decompress/commit/908720afff6300ac9f2ad3addc3e672f43c1c28a))
- .github/linters/.checkov.yml ([6204216](https://github.com/somaz94/compress-decompress/commit/62042163c219415728af54783f1c8161a554eb36))
- Dockerfile ([7228150](https://github.com/somaz94/compress-decompress/commit/7228150258c1638feb8818faf26f050f1dfa9055))
- Dockerfile & README.md ([ebd9cb1](https://github.com/somaz94/compress-decompress/commit/ebd9cb1434a0ee9e17d8f0b76315f6facb38f31e))
- .github/* ([2b64575](https://github.com/somaz94/compress-decompress/commit/2b645755f4d60afc5226be7ca9b550631ae4e49f))
- linters/* ([50c7cff](https://github.com/somaz94/compress-decompress/commit/50c7cffec1b72b2eb91918ddc6caf6532cc7872d))
- .checkov.yml ([9623e51](https://github.com/somaz94/compress-decompress/commit/9623e51441f6d915191c286f51065173d1551c54))
- ../workflows/linter.yml ([d5e2c7b](https://github.com/somaz94/compress-decompress/commit/d5e2c7bf65b60c2fddb90842abf7542bd1c8bc01))
- entrypoint.py ([7c0b211](https://github.com/somaz94/compress-decompress/commit/7c0b211a47b9ee31f87394943d00d722a8217997))
- use-action-v2.yml ([c209291](https://github.com/somaz94/compress-decompress/commit/c209291693cfa14f7b28ad4d70cf9b950b66a66e))
- entrypoint.py ([1e65868](https://github.com/somaz94/compress-decompress/commit/1e65868c74985f3225eab42399989232dd8aa06c))
- use-action-v2.yml ([740dbe4](https://github.com/somaz94/compress-decompress/commit/740dbe4fb6440f02eb34c5edc4f88627a5dfe5a9))
- entrypoint.py ([045fdfe](https://github.com/somaz94/compress-decompress/commit/045fdfe89673a38ecf43d151464183c7643adbe6))
- entrypoint.py ([2d5fbc3](https://github.com/somaz94/compress-decompress/commit/2d5fbc35b90b2784d84f9d4ac43f66062281de8d))
- use-action-v2.yml ([d148df3](https://github.com/somaz94/compress-decompress/commit/d148df3f0b0e63e28b2201c5250ffed532c242d6))
- use-action.yml & entrypoint.py ([d9c8cd5](https://github.com/somaz94/compress-decompress/commit/d9c8cd5a094245718c5f64dcf70e7e77fce8089d))
- ci-v2.yml ([5bbe9de](https://github.com/somaz94/compress-decompress/commit/5bbe9deaf776a2a7d3d4855d00c0a834716e33c6))
- entrypoint.py ([b2e462f](https://github.com/somaz94/compress-decompress/commit/b2e462f666c0f3b08cf0d0ebb2c2bc8bfd084f56))
- entrypoint.py ([4f75921](https://github.com/somaz94/compress-decompress/commit/4f759215fbf11f83e76aeae6565a50780949eef5))
- use-action-v2.yml ([8d3536b](https://github.com/somaz94/compress-decompress/commit/8d3536b32fb286d832c5a8f43ba1101a9c4f6d47))
- entrypoint.py ([9730d4b](https://github.com/somaz94/compress-decompress/commit/9730d4bab9ed59007ca83cc7194424ae93cab13e))
- use-action-v2.yml ([f7d43e8](https://github.com/somaz94/compress-decompress/commit/f7d43e8c603cfc839c57f4a1cd5d458c68436969))
- use-action-v2.yml ([060851c](https://github.com/somaz94/compress-decompress/commit/060851cef0ccb1317bec1612a6dc1f6cc1760030))
- use-action-v2.yml ([9393bb6](https://github.com/somaz94/compress-decompress/commit/9393bb6b6e4724c74a9f07de5fa8f0fcfec9f630))
- use-cation-v2.yml ([ff82b6b](https://github.com/somaz94/compress-decompress/commit/ff82b6be53dc12e436ead0591090846469e619eb))
- ci.yml ([f8d0317](https://github.com/somaz94/compress-decompress/commit/f8d03175067018a48f466570459cddaca81e45ad))
- ci.yml ([54b4d03](https://github.com/somaz94/compress-decompress/commit/54b4d030186172f37abd43a97c9f9ddbc6b9114a))
- ci.yml & add use-action-v2.yml ([c91d2a1](https://github.com/somaz94/compress-decompress/commit/c91d2a108bb3a5ff70b9f561205957c5839eb048))
- .github/workflows ([70e8a4d](https://github.com/somaz94/compress-decompress/commit/70e8a4da377137ecf8db399336448a0308761ceb))
- .github/workflows & .env.test & entrypoint.py ([7fe951c](https://github.com/somaz94/compress-decompress/commit/7fe951c5dcb8ac62d0483eb800104f6f7d1451f7))
- entrypoint.py & action.yml & .env.test ([15ca669](https://github.com/somaz94/compress-decompress/commit/15ca66913270252262114aab6e82a9ea04d89d5a))
- entrypoint.py ([826116b](https://github.com/somaz94/compress-decompress/commit/826116bec245b94db4fa00c00336beba4b0d4999))
- entrypoint.py ([b1bc04d](https://github.com/somaz94/compress-decompress/commit/b1bc04d0340c726039d50ba7c78b217fd76ef356))
- entrypoint.py ([bc22adb](https://github.com/somaz94/compress-decompress/commit/bc22adbefcbd80ecaae234911237012ef4447142))
- action.yml & entrypoint.py ([33a067d](https://github.com/somaz94/compress-decompress/commit/33a067dfe46db5f110be6711a585c1b860b7f64b))

### Documentation

- README.md ([2956889](https://github.com/somaz94/compress-decompress/commit/295688979b81d979f243ec505495afef65206a40))
- README.md ([a98096d](https://github.com/somaz94/compress-decompress/commit/a98096dddc1ca3f45df845610937c267a90d71b1))
- README.md ([a99c0e1](https://github.com/somaz94/compress-decompress/commit/a99c0e130937b7d6882b248ccd2ca1a425cfadc5))

### Builds

- **deps:** bump python in the docker-minor group ([8711cce](https://github.com/somaz94/compress-decompress/commit/8711cce704345dad6c815a53290f73eae075adfe))
- **deps:** bump super-linter/super-linter from 6 to 7 ([74d5920](https://github.com/somaz94/compress-decompress/commit/74d5920709f19997fd216529f8dd70b9c2b0790d))

### Add

- ci-v2.yml ([21644b2](https://github.com/somaz94/compress-decompress/commit/21644b27dbaa81ece5afe3f8f3870d8d11a4236d))

### Contributors

- somaz

<br/>

## [v1.0.2](https://github.com/somaz94/compress-decompress/compare/v1.0.1...v1.0.2) (2024-07-01)

### Builds

- **deps:** bump python in the docker-minor group ([ae350fb](https://github.com/somaz94/compress-decompress/commit/ae350fb2de52218534daf5201bcc1fe30ae660ad))

<br/>

## [v1.0.1](https://github.com/somaz94/compress-decompress/compare/v1.0.0...v1.0.1) (2024-06-28)

### Bug Fixes

- use-action.yml ([397d441](https://github.com/somaz94/compress-decompress/commit/397d441bd1aeffa36c31929ebed3c9e551b7e213))
- use-action.yml ([2e7ef30](https://github.com/somaz94/compress-decompress/commit/2e7ef303a17caa85ccc6bfa5a6d0b505e95a214c))
- action.yml ([d45588b](https://github.com/somaz94/compress-decompress/commit/d45588b5ddaba79f5b03f539f1e77a7a24174a86))
- python-lint ([b19f5bd](https://github.com/somaz94/compress-decompress/commit/b19f5bdd3a2f7b3834e880ffba905ef85d052676))
- python-lint ([1378141](https://github.com/somaz94/compress-decompress/commit/1378141499badcd18a8993e8ecb8b623ef290bb1))
- entrypoint.py ([54a625e](https://github.com/somaz94/compress-decompress/commit/54a625e745aa8f4d4ce5e9a29ea753975521c375))
- entrypoint.py ([5f84233](https://github.com/somaz94/compress-decompress/commit/5f84233f3f1b943822917deafeaf2184111ce328))
- ci.yml ([2aec2f9](https://github.com/somaz94/compress-decompress/commit/2aec2f957f7780d5890d8226290e61833d9498e4))
- ci.yml ([7da6ed9](https://github.com/somaz94/compress-decompress/commit/7da6ed995c5693652b0acef9f84f322a04d2227f))
- ci.yml & action.yml ([ade58e3](https://github.com/somaz94/compress-decompress/commit/ade58e3cdfd1d6a51c14bbe6aff37aee3443dc56))
- ci.yml ([7c6585d](https://github.com/somaz94/compress-decompress/commit/7c6585d19145f5da04fc7e0da38cd3aee4bfead6))
- ci.yml ([7572d5a](https://github.com/somaz94/compress-decompress/commit/7572d5ac96876a6ae3249f8ecbb87fafe6a4e126))
- ci.yml ([7b0b302](https://github.com/somaz94/compress-decompress/commit/7b0b302808d7fb620a199f42259ead025640b988))
- ci.yml ([bb9c004](https://github.com/somaz94/compress-decompress/commit/bb9c004adb1a3709a74c74c050f6c3173ad4f852))
- ci.yml ([19b5782](https://github.com/somaz94/compress-decompress/commit/19b5782dc269bb17490898a61d28fdb48904673a))
- ci.yml ([1fae08b](https://github.com/somaz94/compress-decompress/commit/1fae08be3d6adc59cccb6568bc879e206966dfc7))
- ci.yml ([c1ae641](https://github.com/somaz94/compress-decompress/commit/c1ae641924ad0be13e6ec7a759b6f92caee5c569))
- ci.yml ([10136ae](https://github.com/somaz94/compress-decompress/commit/10136ae170904d1cf6d70b131f0c82c1267f9328))
- ci.yml & linter.yml ([a999445](https://github.com/somaz94/compress-decompress/commit/a999445fff3850bffbfc033d9df43f463cddcb9a))
- entrypoint.py ([464267b](https://github.com/somaz94/compress-decompress/commit/464267bd4e59a52267479e170580a0c98acfd122))
- entrypoint.py & ci.yml ([b8696af](https://github.com/somaz94/compress-decompress/commit/b8696af20f68b1c76f7e520befdcfbfc632fca26))
- entrypoint.py ([3b5492e](https://github.com/somaz94/compress-decompress/commit/3b5492ecbfad3d5c85f220210ed955a23b9f7eb9))
- entrypoint.py ([6e7b052](https://github.com/somaz94/compress-decompress/commit/6e7b052636110f234feaac5ca8cf2419af4cf980))
- entrypoint.py ([ed33cb3](https://github.com/somaz94/compress-decompress/commit/ed33cb3782ed4c026dc483d613dfcce13be90837))

### Add

- use-action.yml ([11724f3](https://github.com/somaz94/compress-decompress/commit/11724f3e58d06460da72cbf85cc4e0b13edf1180))

### Contributors

- somaz

<br/>

## [v1.0.0](https://github.com/somaz94/compress-decompress/releases/tag/v1.0.0) (2024-06-24)

### Contributors

- somaz

<br/>

