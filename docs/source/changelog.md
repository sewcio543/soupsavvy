# Changelog

## v1.0.0<!-- Release notes generated using configuration in .github/release.yml at v1.0.0 -->### Breaking Changes 💥\* Implementations rework by @sewcio543 in https://github.com/sewcio543/soupsavvy/pull/207\* About tutorial for new design by @sewcio543 in https://github.com/sewcio543/soupsavvy/pull/208**Full Changelog**: https://github.com/sewcio543/soupsavvy/compare/v0.3.1...v1.0.0

## v0.3.1<!-- Release notes generated using configuration in .github/release.yml at v0.3.1 -->

### New Features 🎉

- `XPathSelector`
- `ExpressionSelector`

### Improvements 🚀

- `Operation` allows extra parameters
- Support for python 3.13

### Documentation 📚

- `Other` section with changelog and contribution guidelines
- `Features` tutorial

**Full Changelog**: https://github.com/sewcio543/soupsavvy/compare/v0.3.0...v0.3.1

## v0.3.0<!-- Release notes generated using configuration in .github/release.yml at v0.3.0 -->

### Breaking Changes 💥

- `SkipNone` and `Suppress` moved to `operations`
- Base `operation` and `selectors` classes moved to new `base` module

### New Features 🎉

- Conditional Operations (`IfElse`, `Break`, `Continue`)
- Model post-processors (`post`)
- Model field customization (`Field`)

### Documentation 📚

- Documentation and demos update

### Improvements 🚀

- Extended model migration
- Frozen model

### Other

- `api` module deprecated and renamed to `operators`
- `base` module with base classes

**Full Changelog**: https://github.com/sewcio543/soupsavvy/compare/v0.2.3...v0.3.0

## v0.2.3<!-- Release notes generated using configuration in .github/release.yml at v0.2.3 -->

### New Features 🎉

- Model Migrations
- `SelfSelector` selector
- `Parent` selector/operation

### Improvements 🚀

- Improved deprecation in package
- Allowing Operations as model fields
- `Suppress` optionally accepts exception category

### Other Changes

- Replacing some attributes with read-only properties

**Full Changelog**: https://github.com/sewcio543/soupsavvy/compare/v0.2.2...v0.2.3

## v0.2.2<!-- Release notes generated using configuration in .github/release.yml at v0.2.2 -->

### New Features 🎉

- `Operations` subpackage
- `Models` subpackage

### Documentation 📚

- Docstrings in package init file
- `Model` tutorial

**Full Changelog**: https://github.com/sewcio543/soupsavvy/compare/v0.2.1...v0.2.2

## v0.2.1<!-- Release notes generated using configuration in .github/release.yml at v0.2.1 -->

### New Features 🎉

- `AncestorCombinator` and `ParentCombinator`
- `RelativeParent` and `RelativeAncestor` in `selectors.relative`

### Fixes 🐛

- Equality in `CompisiteSoupSelector`

### Improvements 🚀

- Docs - improvements
- `check_selector` function decoupled from `SoupSelector` in `selectors.base`

**Full Changelog**: https://github.com/sewcio543/soupsavvy/compare/v0.2.0...v0.2.1

## v0.2.0<!-- Release notes generated using configuration in .github/release.yml at v0.2.0 -->

### Breaking Changes 💥

- Renaming `tags` subpackage to `selectors`
- Moving `nth` package from `selectors.css` to `selectors`
- Renaming `TagSelector` to `TypeSelector` and removing `attributes` parameter
- Renaming `AnyTagSelector` to `UniversalSelector`
- Moving `HasSelector` to `relative.py` module
- Moving all logical selctors to `soupsavvy.selectors.logical.py` module
- Removing `tag` parameter from `soupsavvy.selectors.css` module selectors.

### New Features 🎉

- `XORSelector`

### Improvements 🚀

- Alias for `SelectorList` -> `OrSelector`
- `IdSelector` and `ClassSelector` to package init
- Moving documentation to [ReadTheDocs](https://soupsavvy.readthedocs.io/en/latest/)
- New tutorials in documentation

This minor release introduces breaking changes as with this version development of `soupsavvy` is planned to be more stable with gradual changes from release to release. All this changes makes package more consistent and components more coherent.

**Full Changelog**: https://github.com/sewcio543/soupsavvy/compare/v0.1.9...v0.2.0
