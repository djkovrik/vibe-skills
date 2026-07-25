# Platform entry points and release

- Create the root component/context once per host lifecycle outside Compose.
- Document Android Application/Activity startup and iOS Swift/UIViewController startup ordering.
- Verify Gradle artifact, CocoaPods declarations, lockfile, framework linkage, and Xcode target together.
- Keep signing secrets in approved environment/secret stores; document only variable contracts.
- Validate release variants, shrinking/mapping, native symbols, localized notes, artifacts, and rollback.
- On iOS, build the workspace when CocoaPods owns dependencies.

Primary references:

- https://kotlinlang.org/docs/multiplatform/multiplatform-cocoapods-overview.html
- https://developer.android.com/build
- https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases

Blinkly adaptation: its Firebase-before-root startup, static native dependency graph, and Android release workflows are project evidence that must be revalidated against target SDKs.

