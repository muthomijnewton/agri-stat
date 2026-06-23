plugins {
    id("com.android.application")

    // Flutter Gradle plugin
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "com.example.agric_stat_mobile"

    compileSdk = 36

    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17

        // FIX for flutter_local_notifications
        isCoreLibraryDesugaringEnabled = true
    }

    defaultConfig {
        applicationId = "com.example.agric_stat_mobile"

        minSdk = flutter.minSdkVersion

        targetSdk = 36

        versionCode = flutter.versionCode

        versionName = flutter.versionName
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

flutter {
    source = "../.."
}

subprojects {
    afterEvaluate {
        if (project.hasProperty("android")) {
            project.extensions.configure<com.android.build.gradle.LibraryExtension>(
                "android"
            ) {
                compileSdk = 36
            }
        }
    }
}

dependencies {

    // Required by flutter_local_notifications
    coreLibraryDesugaring(
        "com.android.tools:desugar_jdk_libs:2.1.5"
    )
}