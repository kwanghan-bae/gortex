# Future Work Plan: Gap Analysis & Roadmap

This document outlines the discrepancies between the initial planning documents (`Clover_Lotto_README.md`, `Clover_Lotto_Design_Guide.md`, `Clover_Lotto_Project_Proposal.md`) and the current codebase implementation. It serves as a roadmap for future development.

## 1. Critical Gaps (High Priority)

### Frontend
-   **OCR Lotto Ticket Scan**:
    -   **Status**: Unimplemented.
    -   **Gap**: `flutter_native_ocr` dependency exists, but no scanning screen or logic is implemented. The "Scan" button in `HistoryScreen` is likely missing or non-functional.
    -   **Action**: Implement `ScanScreen` using `camera` and `flutter_native_ocr` packages. Parse scanned text to extract numbers and round info.
-   **Community Interaction**:
    -   **Status**: Partial.
    -   **Gap**: "Like" button exists in UI but backend API for liking posts (`POST /posts/{id}/like`) is missing. "Share" button is a placeholder.
    -   **Action**: Implement backend "Like" API and connect frontend button. Implement native share functionality using `share_plus`.
-   **Push Notification Handling**:
    -   **Status**: Basic Implementation.
    -   **Gap**: `FcmService` is initialized, but specific handlers for different notification types (Winning, Comment, Notice) are not fully implemented in the UI (e.g., navigating to specific screens).
    -   **Action**: Implement deep linking or specific routing based on notification data payload.

### Backend
-   **Badge Logic Flaw**:
    -   **Status**: Buggy.
    -   **Gap**: `BadgeService` only checks for badges when a *winning* check occurs. Badges like "Frequent Player" (based on purchase count) will never be awarded if the user doesn't win or check winnings.
    -   **Action**: Trigger badge updates on *game save* (purchase) as well, not just winning checks.
-   **Notification Scheduling**:
    -   **Status**: Missing.
    -   **Gap**: "Notification before draw" (Saturday 8:00 PM) is planned but not implemented.
    -   **Action**: Implement a scheduled task (`@Scheduled`) in Spring Boot to send broadcast push notifications at specific times.

## 2. Feature Enhancements (Medium Priority)

### Frontend
-   **Map & Location**:
    -   **Status**: Basic.
    -   **Gap**: Map markers are currently mock data or limited. "Search by Region" filter is missing.
    -   **Action**: Connect `LottoSpotViewModel` to a real backend endpoint that supports geo-spatial queries (radius search).
-   **Travel Plan Recommendation**:
    -   **Status**: Missing.
    -   **Gap**: Entire "Travel Plan" feature (combining Lotto Spots with local tourism) is missing.
    -   **Action**: Create `TravelScreen` and backend service to curate/recommend trips.

### Backend
-   **Auth & Security**:
    -   **Status**: TODOs exist.
    -   **Gap**: Refresh Token logic and Logout (Blacklist) are marked as TODO in `AuthService`.
    -   **Action**: Implement full JWT lifecycle management.

## 3. UI/UX Polish (Low Priority)

-   **Empty States**: Better empty states for "My Lotto", "Community", and "Notifications".
-   **Animations**: Add micro-animations for button presses and loading states as per Design Guide.
-   **Accessibility**: Ensure proper semantic labels for screen readers.

## 4. Summary of Missing Files/Components

| Component | Status | Description |
| :--- | :--- | :--- |
| `ScanScreen.dart` | ❌ Missing | Camera & OCR UI |
| `TravelScreen.dart` | ❌ Missing | Travel recommendation UI |
| `LikeController.kt` | ❌ Missing | Backend API for post likes |
| `NotificationScheduler.kt` | ❌ Missing | Scheduled push notifications |
| `RefreshTokenRepository` | ❌ Missing | For secure token management |

---

**Generated on**: 2025-12-04
**Based on**: Codebase Audit vs. Planning Docs
