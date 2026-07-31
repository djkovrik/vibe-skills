# Data

## Local tables and settings

Store only the stable `PreferenceValue` ID through a typed settings contract with a documented default. Do not persist a translated label.

Do not store a language or locale preference. The active language follows the operating-system locale only; there is no application-specific locale override.

## Localized text storage

Compose Multiplatform Resources owns every user-visible label for this local option catalog. English is always the default/base locale: put its complete resource set in `composeResources/values/strings.xml`. Put the additional Russian translations in `composeResources/values-ru/strings.xml`, and add future locales through matching `values-<locale>/strings.xml` files with the same keys.

| Stable value ID | Shared string resource key |
| --- | --- |
| `standard` | `preference_option_standard` |
| `compact` | `preference_option_compact` |

Settings, seed data, and Kotlin code contain only the stable value IDs/resource keys, never resolved EN/RU text. Resolve keys to generated `Res.string.*` accessors at the presentation boundary. If a native `actual` cannot use Compose resources, keep the same semantic key in Android `res/values*/strings.xml` or an iOS string catalog/localized `.strings` resource file; do not hardcode the fallback text in platform code.

## Remote APIs and authentication

No remote API or authentication.

## Offline, cache, and sync

Settings are available offline. No sync or conflict policy is required.

## Privacy and retention

Retain the preference until reset or uninstall.
