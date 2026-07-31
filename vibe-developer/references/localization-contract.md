# Localized local text contract

Apply this contract to user-visible text bundled with the app, including labels, local catalogs, seed/reference data, database-backed built-in content, and other text that may have translations. It does not turn user-authored or server-owned dynamic content into app resources.

## Canonical representation

- Keep English as the default/base locale. Put the complete English key set in Compose Multiplatform Resources `composeResources/values/strings.xml`; put Russian in `composeResources/values-ru/strings.xml`. Use one stable resource key in every supported locale from `app.locales`; new locales add another resource set without changing domain or persistence schemas.
- Derive the active locale only from the operating system. Do not add an in-app language picker, persist a language preference, expose locale-selection state, or install an application-specific locale override. When the system locale changes, let the resource system select the matching locale; unsupported locales fall back to English.
- Keep language-neutral IDs and, where data-driven lookup is required, stable localization keys in domain models, settings, database rows, seed data, snapshots, and component/Store state. Never persist or sync a resolved translation, per-locale text columns, or embedded translation maps for app-bundled content.
- Resolve a key to the generated Compose `StringResource`/`Res.string.*` accessor at the presentation boundary. Keep Compose resource types out of the core domain and persistence contracts.
- Do not hardcode user-visible product copy in production Kotlin/Swift/Objective-C/Java code, preview fixtures, local seed files, or database initializers. Formatting templates, plurals, accessibility labels, errors shown to users, and catalog titles/descriptions follow the same rule.

## Native fallback

When a platform `actual` or native API cannot consume Compose Multiplatform Resources, use that platform's localization resources: Android `res/values*/strings.xml`, and iOS string catalogs such as `Localizable.xcstrings` or localized `.strings` tables. Keep English as the native default/base localization, Russian as an additional localization, an explicit stable-key mapping, and no translated literals in platform code.

## AppSpec and verification

- Set `localization.defaultLocale` to `en`, `localization.localeSelection` to `system-only`, and include English in `app.locales`. New app templates start with `app.locales: ["en", "ru"]`: English is always the default/base locale and Russian is the initial additional locale; later locales append without changing that default.
- In `data.md`, inventory each bundled local dataset, its stable item IDs, localization keys, owning resource module, and any native-only resource table.
- Require key-set completeness for every declared locale, valid key-to-resource mappings, system-locale change/fallback coverage, proof that no language preference or picker exists, persistence round trips that preserve IDs/keys, and a production-source scan for hardcoded user-visible strings.
- Render previews and goldens through production resources in at least the default and longest-risk locale; do not make layouts pass with shorter fixture literals.

Primary sources:

- https://kotlinlang.org/docs/multiplatform/compose-multiplatform-resources-usage.html
- https://developer.android.com/guide/topics/resources/localization
- https://developer.apple.com/documentation/Xcode/localizing-and-varying-text-with-a-string-catalog
