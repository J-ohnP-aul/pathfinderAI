# Software Requirements Specification

## PathfinderAI

**Version:** 1.0  
**Date:** 2026-09-09  
**System type:** Django web application and JSON API

## 1. Introduction

### 1.1 Purpose

This document specifies the requirements for PathfinderAI, a location-aware discovery and recommendation system. The system helps a user find nearby places in and around Nairobi by combining location, category, budget, available time, and personal preferences. It can optionally use external place data and a configured large language model to produce a concise recommendation summary.

This SRS describes the behavior currently implemented in the repository and identifies capabilities that remain future work. It is intended for developers, testers, project stakeholders, and maintainers.

### 1.2 Product scope

PathfinderAI shall provide:

- Account registration, login, and logout.
- A discovery form for named locations, coordinates, or current location.
- Filtering of places by budget, visit duration, and category.
- Ranking of places by interests, distance, budget fit, time fit, and availability.
- A map centered on the selected location.
- User preference storage and retrieval.
- Browser-facing and JSON API access to nearby places and personalized recommendations.
- Optional AI-generated summaries with a scored-results fallback when AI is unavailable.

The current product does not include booking, payments, user reviews, itinerary persistence, or a fully implemented conversational assistant.

### 1.3 Definitions and abbreviations

| Term | Definition |
| --- | --- |
| Place | A discoverable location or activity with category, coordinates, cost, duration, rating, address, description, and opening information. |
| Discovery request | A request containing a location and trip constraints such as budget and available time. |
| Recommendation | A place that passed the request constraints and received a calculated score. |
| LLM | Large language model used to generate a natural-language summary. |
| Provider | A component that supplies nearby places from local data or an external service. |

### 1.4 References

- Django 5.2 project configuration and built-in authentication framework.
- OpenStreetMap embedded map and optional Overpass place provider.
- Google Gemini and Ollama integrations configured through environment variables.

## 2. Overall Description

### 2.1 Product perspective

PathfinderAI is a server-rendered Django application. The browser submits HTML forms to Django views and displays returned results. JSON clients can use the nearby-place, recommendation, and preference endpoints. The application uses SQLite by default and supports replaceable place providers.

### 2.2 User classes

| User class | Description |
| --- | --- |
| Visitor | An unauthenticated user who can discover nearby places using request-specific criteria. |
| Registered user | A user who can save preferences and receive personalized recommendations. |
| Administrator | A Django administrative user responsible for operational data and system administration. |
| System operator | A maintainer who configures environment variables, external providers, and the LLM service. |

### 2.3 Operating environment

- Python 3 with Django 5.2 or a compatible supported version.
- SQLite for the default development database.
- A modern web browser with JavaScript enabled for browser geolocation and location fallback behavior.
- Local or hosted network access when using external geocoding, OpenStreetMap, Gemini, or other remote services.
- Ollama running locally, or a configured Gemini API key, for AI summaries.

### 2.4 Design and implementation constraints

- The application is implemented in Python/Django and uses Django forms for validation.
- Coordinates are represented as latitude and longitude decimal values.
- Place costs are represented as integer Kenyan Shillings (KSh).
- The default place catalog is local, centered on Nairobi, and can be replaced or supplemented by provider implementations.
- AI output is optional; core scored recommendations must remain usable when AI is unavailable.
- Secrets and provider configuration shall be supplied through environment variables rather than source code.

### 2.5 Assumptions and dependencies

- A user can provide a valid named location or a valid latitude/longitude pair.
- External services may be unavailable, slow, rate-limited, or return invalid data.
- Place opening information and ratings are informational and may become stale.
- Browser geolocation is available only where the browser permits it, generally on localhost or HTTPS.
- The current system assumes a single primary deployment region and does not implement localization or multi-currency support.

## 3. System Features and Functional Requirements

Requirement statuses: **Implemented** means present in the current repository; **Partial** means a limited implementation exists; **Future** means it is a target requirement rather than current behavior.

### 3.1 Account management

| ID | Requirement | Status |
| --- | --- | --- |
| FR-ACC-01 | The system shall allow a visitor to register with username, email, and password confirmation. | Implemented |
| FR-ACC-02 | The system shall validate passwords using Django password validators. | Implemented |
| FR-ACC-03 | The system shall allow a registered user to log in and log out. | Implemented |
| FR-ACC-04 | The system shall protect personalized recommendation and preference operations behind authentication. | Implemented |
| FR-ACC-05 | The system shall provide clear feedback for invalid credentials and form validation errors. | Implemented |
| FR-ACC-06 | The system should support password reset and account recovery. | Future |

### 3.2 Location input and discovery

| ID | Requirement | Status |
| --- | --- | --- |
| FR-DIS-01 | The system shall accept a named location, such as “Nairobi CBD,” and resolve it to coordinates. | Implemented |
| FR-DIS-02 | The system shall accept a latitude and longitude pair as manual input. | Implemented |
| FR-DIS-03 | The system shall offer browser geolocation when supported and permitted. | Implemented |
| FR-DIS-04 | The system shall use an approximate IP-based location fallback when precise browser geolocation is unavailable. | Implemented |
| FR-DIS-05 | The system shall reject a discovery request when it cannot determine a valid location. | Implemented |
| FR-DIS-06 | The system shall accept a non-negative budget in KSh and a positive available-time value in minutes. | Implemented |
| FR-DIS-07 | The system shall allow the user to select all categories or one category from food, nature, history, culture, adventure, nightlife, shopping, and relaxation. | Implemented |
| FR-DIS-08 | The system should validate coordinate ranges and normalize location-provider errors into user-readable messages. | Future |

### 3.3 Place retrieval and recommendation

| ID | Requirement | Status |
| --- | --- | --- |
| FR-REC-01 | The system shall retrieve nearby places within the configured search radius. | Implemented |
| FR-REC-02 | The system shall support a local place provider as the default fallback. | Implemented |
| FR-REC-03 | The system may retrieve mapped places from the OpenStreetMap Overpass API. | Implemented |
| FR-REC-04 | The system may retrieve live place suggestions from Gemini when configured. | Implemented |
| FR-REC-05 | The system shall exclude places whose estimated cost exceeds the requested budget. | Implemented |
| FR-REC-06 | The system shall exclude places whose visit duration exceeds the available time. | Implemented |
| FR-REC-07 | The system shall rank remaining places using interest match, distance, budget, time, and availability factors. | Implemented |
| FR-REC-08 | The system shall return a bounded list of highest-scoring recommendations. | Implemented |
| FR-REC-09 | Each recommendation shall include identifying information, description, category, distance, cost, duration, rating, opening information, score, and an explanation. | Implemented |
| FR-REC-10 | The system should indicate when no places satisfy the constraints and suggest changing the search criteria. | Implemented |
| FR-REC-11 | The system should allow administrators or operators to manage place data without code changes. | Future |

### 3.4 Map and presentation

| ID | Requirement | Status |
| --- | --- | --- |
| FR-MAP-01 | The system shall display an OpenStreetMap embedded map centered on the selected coordinates. | Implemented |
| FR-MAP-02 | The system shall display nearby results with readable names, descriptions, scores, reasons, costs, durations, distances, addresses, and opening information. | Implemented |
| FR-MAP-03 | The system should provide direct map markers or selectable result-to-map interactions for each recommendation. | Future |
| FR-MAP-04 | The system should provide a responsive and accessible experience on desktop and mobile browsers. | Partial |

### 3.5 Preferences

| ID | Requirement | Status |
| --- | --- | --- |
| FR-PREF-01 | An authenticated user shall be able to save interests from the supported category list. | Implemented |
| FR-PREF-02 | An authenticated user shall be able to save budget preference, preferred transport, available time, travel companions, dietary preferences, and mobility preferences. | Implemented |
| FR-PREF-03 | The system shall create a default preference record when an authenticated user first accesses preferences. | Implemented |
| FR-PREF-04 | Personalized recommendations shall use the saved interests in ranking. | Implemented |
| FR-PREF-05 | The system should use transport, companion, dietary, and mobility preferences in recommendation ranking. | Future |

### 3.6 AI assistance

| ID | Requirement | Status |
| --- | --- | --- |
| FR-AI-01 | The system shall generate a concise summary from the discovery context and ranked recommendations when an LLM is configured. | Implemented |
| FR-AI-02 | The system shall support Ollama as the default summary provider. | Implemented |
| FR-AI-03 | The system shall support Gemini as an alternative summary provider. | Implemented |
| FR-AI-04 | The system shall show scored recommendations when the LLM is unavailable, misconfigured, rate-limited, or returns invalid output. | Implemented |
| FR-AI-05 | The system shall avoid presenting the AI summary as a substitute for the underlying recommendation data. | Implemented |
| FR-AI-06 | The conversational assistant endpoint should return a working answer instead of the current “not configured” response. | Future |

### 3.7 API requirements

| ID | Endpoint | Requirement | Status |
| --- | --- | --- | --- |
| FR-API-01 | `POST /api/places/nearby` | Accept a JSON discovery request, validate it, and return nearby places. | Implemented |
| FR-API-02 | `POST /api/recommendations` | Require authentication and return ranked recommendations, AI summary, and AI status. | Implemented |
| FR-API-03 | `GET /api/profile/preferences` | Require authentication and return the current user's preferences. | Implemented |
| FR-API-04 | `PUT /api/profile/preferences` | Require authentication, validate the JSON body, save preferences, and return the updated values. | Implemented |
| FR-API-05 | All JSON endpoints | Return appropriate JSON validation errors for malformed JSON or invalid form data. | Implemented |
| FR-API-06 | `GET /answer/` | Provide a usable assistant response. | Future; currently returns HTTP 503 |

## 4. External Interface Requirements

### 4.1 User interface

The web interface shall provide:

- A discovery page with location, budget, time, and category controls.
- A “Use my location” action with status feedback and fallback behavior.
- A map section after a successful search.
- A results section with recommendation details and AI status.
- Registration, login, logout, and preferences pages.
- CSRF protection on server-rendered state-changing forms.

### 4.2 Software interfaces

The system may communicate with:

- OpenStreetMap export/embed for map display.
- `ipapi.co` for approximate browser-side IP geolocation fallback.
- A geocoding service used by `resolve_location` for named locations.
- OpenStreetMap Overpass API for mapped place retrieval.
- Ollama HTTP API for local summaries.
- Google Gemini API for place suggestions or summaries.

External failures shall degrade gracefully to local place data or scored recommendations where possible.

### 4.3 Data interface

The primary persisted entities are:

- Django `User`: username, email, password hash, and authentication metadata.
- `UserPreference`: one-to-one user preferences, interests, budget, transport, time, companions, dietary preferences, mobility preferences, and update timestamp.
- `Place`: an in-memory/provider-level record containing ID, name, category, coordinates, address, description, estimated cost, visit duration, rating, and opening information.

## 5. Non-Functional Requirements

| ID | Requirement | Verification approach |
| --- | --- | --- |
| NFR-01 | The system shall validate all user and API input server-side. | Automated form and API tests |
| NFR-02 | The system shall not expose passwords, API keys, or provider credentials in responses or logs. | Configuration review and security test |
| NFR-03 | The system shall continue to return useful scored results when optional external services fail. | Provider failure tests |
| NFR-04 | A normal local discovery request should complete within 2 seconds excluding external provider or LLM latency. | Performance test |
| NFR-05 | External calls shall use bounded timeouts and handle malformed responses. | Integration tests and code review |
| NFR-06 | Authenticated endpoints shall enforce authentication and Django CSRF/session protections appropriate to the client. | Security tests |
| NFR-07 | The user interface shall be usable with keyboard navigation and readable on mobile and desktop viewports. | Accessibility and responsive UI tests |
| NFR-08 | Recommendation scoring shall be deterministic for the same inputs and provider results. | Unit tests |
| NFR-09 | The system shall be maintainable through replaceable provider and ranking components. | Architecture review and unit tests |
| NFR-10 | Production deployments shall disable debug mode, use a secure secret key, configure allowed hosts, and use a production database and static-file strategy. | Deployment checklist |

## 6. Main Use Cases

### UC-01: Discover nearby places

**Actor:** Visitor or registered user  
**Preconditions:** The application is available.  
**Main flow:**

1. The user opens the discovery page.
2. The user enters a named location, coordinates, or chooses current location.
3. The user enters budget, available time, and an optional category.
4. The system validates and resolves the location.
5. The system retrieves nearby places.
6. The system filters and ranks places.
7. The system displays the map and recommendations.

**Alternative flows:**

- If location permission is unavailable, the system tries approximate IP location.
- If automatic location fails, the system asks for a named location or coordinates.
- If no places match, the system displays an empty-result message.
- If an external provider fails, the system uses its fallback provider.

### UC-02: Get personalized recommendations

**Actor:** Registered user  
**Preconditions:** The user is authenticated and may have saved preferences.  
**Main flow:**

1. The user submits discovery criteria.
2. The system loads the user's stored interests.
3. The system ranks places using the interests and request constraints.
4. The system returns scored recommendations and an optional AI summary.

### UC-03: Manage preferences

**Actor:** Registered user  
**Main flow:**

1. The user opens the preferences page.
2. The system loads existing preferences or creates defaults.
3. The user edits preference fields.
4. The system validates and saves the changes.
5. The system confirms the updated preferences.

### UC-04: Use the recommendation API

**Actor:** API client  
**Main flow:**

1. The client sends JSON to a supported endpoint.
2. The system parses and validates the payload.
3. The system returns JSON data or structured validation errors.
4. An unauthenticated request to a protected endpoint is rejected or redirected according to Django authentication configuration.

## 7. Data Validation and Business Rules

- Budget must be an integer greater than or equal to zero.
- Available time must be an integer greater than zero.
- A discovery request must resolve to both latitude and longitude.
- A named location is resolved only when both coordinates are not supplied.
- A place is eligible only if its estimated cost is within budget and its visit duration is within available time.
- Category filters must use the supported category choices.
- Recommendation results are ordered by descending calculated score and limited to the configured result count.
- User interests are stored as a list of supported category values.
- AI failures must not prevent scored recommendations from being shown.

## 8. Acceptance Criteria

The release satisfies the core SRS when:

1. A visitor can submit a valid named location and receive nearby results and a map.
2. A visitor can submit coordinates and receive equivalent discovery behavior.
3. Budget, time, and category constraints are reflected in the returned results.
4. A registered user can save preferences and receive interest-aware ranking.
5. Protected API endpoints reject unauthenticated access.
6. Malformed JSON and invalid form data return clear validation errors.
7. The system returns useful scored recommendations when the configured LLM is unavailable.
8. Automated tests cover location validation, filtering, ranking, authentication, and API behavior.

## 9. Future Enhancements

- Replace the placeholder assistant endpoint with a controlled conversational planning flow.
- Add saved trips, favorites, itinerary sequencing, and sharing.
- Add user ratings, reviews, and feedback-based ranking.
- Persist and administer the place catalog in the database.
- Use transport, accessibility, dietary, and companion preferences in scoring.
- Add provider caching, rate limiting, observability, and background refresh jobs.
- Add password recovery, email verification, account deletion, and privacy controls.
- Add production deployment configuration, stronger secrets management, and a production database.
- Add automated accessibility, performance, and external-provider integration tests.
