## 2025-05-15 - [Interactive Suggestions and Dynamic ARIA Labels]
**Learning:** Converting static text suggestions into clickable buttons drastically reduces user friction and clarifies how to interact with a chatbot. Additionally, dynamic `aria-label` values for buttons (e.g., "Sending..." vs "Send") provide immediate, non-visual feedback during async operations.
**Action:** Always look for static "hint" text that can be made interactive and ensure all async action buttons have state-aware ARIA labels.

## 2025-05-15 - [Consistent Theming with CSS Variables]
**Learning:** Implementing a brand-specific color palette using CSS variables (`:root`) ensures visual consistency and makes future theme updates trivial. It also allows for easier contrast checking across the entire UI.
**Action:** Use CSS variables for all theme-related colors to maintain a single source of truth for the app's visual identity.
