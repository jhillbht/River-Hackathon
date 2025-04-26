# Required Permissions for Traffic Alert App

## iOS Info.plist Entries

The following entries must be added to the app's Info.plist file:

### Privacy Permissions

1. **Location Always and When In Use Permission**
   - Key: `NSLocationAlwaysAndWhenInUseUsageDescription`
   - Value: "This app needs your location to provide traffic alerts relevant to your route while driving."
   - Purpose: Allows continuous location tracking, even in the background.

2. **Location When In Use Permission**
   - Key: `NSLocationWhenInUseUsageDescription`
   - Value: "This app needs your location to provide traffic alerts relevant to your route."
   - Purpose: Required as a fallback when "Always" permission is not granted.

3. **Motion Usage Permission**
   - Key: `NSMotionUsageDescription`
   - Value: "Motion detection is used to determine when you're driving so traffic alerts can be provided."
   - Purpose: Enables detection of driving activity.

### Background Modes

Add the following to the UIBackgroundModes array:

```xml
<key>UIBackgroundModes</key>
<array>
    <string>location</string>
    <string>fetch</string>
    <string>processing</string>
</array>
```

- **location**: Allows the app to receive location updates in the background
- **fetch**: Enables periodic background updates to check for new traffic incidents
- **processing**: Allows the app to continue processing data in the background

## Special Entitlements

### Critical Alerts Entitlement

The Critical Alerts entitlement (`com.apple.developer.usernotifications.critical-alerts`) requires special permission from Apple. You must apply for this entitlement with a valid justification.

This allows notifications to bypass Do Not Disturb mode and silent switch settings, which is crucial for emergency traffic alerts for first responders.

## Implementation Best Practices

1. Request permissions at appropriate times with clear explanations
2. Implement graceful fallbacks if permissions are denied
3. Provide in-app guidance for enabling permissions via Settings
4. Conserve battery by only activating features when necessary
5. Regularly check permission status in case it changes
