# insertion-devices
Python package for magnetic simulation of insertion devices

## Guidelines for naming branches

Branches may be named like: `<identifier>-<description-with-hyphens>`

Identifiers represent the main goal of the branch, and might be:

- `feat` : New feature or feature expansion.
- `fix` : Bug fix.
- `docs` : Add or expand documentation.
- `style` : Code formating, without altering its content.
- `refactor` : Refactor (ex: change variable names, alter class structure).
- `perf` : Performance improvement.
- `test` : Add, expand or correct test.
- `example` : Add, expand or correct example.
- `wip` : Works in progress, that might not be done soon.
- `exp` : Experiment, probably discarded.

Examples: `feat-roll-off`, `docs-shim-notebook`, `fix-shimming-results-plot-char`

## Semantic versioning

Versioning should follow the guidelines described by the [Semantic Versioning specification](https://semver.org/) ([CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)):

> 4. Major version zero (0.y.z) is for initial development. Anything MAY change at any time. The public API SHOULD NOT be considered stable.
>
> 5. Version 1.0.0 defines the public API. The way in which the version number is incremented after this release is dependent on this public API and how it changes.
>
> 6. Patch version Z (x.y.Z | x > 0) MUST be incremented if only backward compatible bug fixes are introduced. A bug fix is defined as an internal change that fixes incorrect behavior.
>
> 7. Minor version Y (x.Y.z | x > 0) MUST be incremented if new, backward compatible functionality is introduced to the public API. It MUST be incremented if any public API functionality is marked as deprecated. It MAY be incremented if substantial new functionality or improvements are introduced within the private code. It MAY include patch level changes. Patch version MUST be reset to 0 when minor version is incremented.
>
> 8. Major version X (X.y.z | X > 0) MUST be incremented if any backward incompatible changes are introduced to the public API. It MAY also include minor and patch level changes. Patch and minor versions MUST be reset to 0 when major version is incremented.

## imaids GUI

The gui icons are provided by [Yusuke Kamiyamane](https://p.yusukekamiyamane.com/). Licensed under a [Creative Commons Attribution 3.0 License](https://creativecommons.org/licenses/by/3.0/).