---
title: Documentation
---
<div class="align-center">
<img src="https://www.bitcaster.io/wp-content/uploads/2024/06/bitcaster-logo-h2.svg">
</div>

# Welcome to Bitcaster Documentation

## TL;TR

Bitcaster is a system-to-user signal-to-message notification system.

In a usual IT environment, Applications must send specific messages to their users. Usually, each application needs to implement multiple protocols to allow users to receive information differently (email, SMS, chat, push notifications).
This can be problematic, expensive, and difficult to manage.

Bitcaster aims to handle these situations by moving the notification system from the application layer to the infrastructure layer.

Bitcaster will receive signals from any of your applications/systems using a simple RESTful API and will convert them in messages to be distributed to you users via a plethora of channels.

Messages content is customised at user/receiver level using a flexible template system.

Administrators are empowered with an easy to use console to choose how to receive the messages configured in Bitcaster.

## What is Bitcaster?

Bitcaster is a powerful, system-to-user notification hub designed to solve the complexity of enterprise messaging. For a large organization, its value lies in centralizing communication logic, ensuring governance, and providing a highly personalized experience for recipients.

  Here are the key capabilities:

  1. Advanced Content & Context-Based Event Routing
  Bitcaster allows enterprises to move beyond "blast" notifications to intelligent, targeted messaging:
   * Payload Filtering (JMESPath): Notifications can be configured with complex rules to evaluate the incoming signal's payload. For example, a "System Alert" event can be routed to a "Critical Response" notification only if the
     severity in the JSON payload is high and the department is infrastructure.
   * Dynamic Recipient Filtering: Instead of static distribution lists, Bitcaster can query and filter recipients in real-time based on their profile attributes (e.g., "notify only users in the 'London' office who are currently
     'On-Call'").
   * Environment Awareness: Built-in support for environment-based routing ensures that notifications from staging or development systems are handled differently than production signals, preventing alert fatigue.

  2. Rich-Text Template Management & Rendering
  The platform provides a sophisticated engine for managing how messages look across different mediums:
   * Multi-Format Capabilities: It supports Plain Text, HTML, and Markdown templates. This ensures that a single event can be rendered as a beautifully formatted email, a concise SMS, or a rich Slack/Teams card with interactive
     elements.
   * Dynamic Context Injection: Using a flexible template engine (Django-based), Bitcaster injects real-time data from the event signal directly into the message. This allows for highly specific notifications (e.g., "Hello \{\{
     user.first_name \}\}, your server \{\{ server_id \}\} in \{\{ region \}\} is at 95% capacity").
   * Protocol-Aware Rendering: The system automatically detects the capabilities of the target channel (e.g., an Email channel supports HTML and Subjects, while an SMS channel only supports Text) and chooses the appropriate
     template version to ensure the best possible delivery.

  3. Enterprise Governance & Multi-Tenancy
   * Logical Isolation: Bitcaster uses a hierarchical structure (Organizations > Projects > Applications) that fits perfectly into complex corporate structures. Different departments can manage their own notification logic in
     isolation while sharing the same underlying infrastructure.
   * Granular Security: Access is controlled via scoped API Keys and Single Sign-On (SSO) integrations with enterprise providers like Azure AD, GitHub Enterprise, and Google Workspace.
   * Auditability & Compliance: The system tracks every "Occurrence" (event trigger) and its subsequent notifications. Enterprises can set data retention policies to automatically purge history in compliance with GDPR or
     internal data privacy standards.

  4. Omnichannel Delivery & User Empowerment
   * Unified API: Internal developers only need to integrate with one RESTful API to gain access to Email, SMS, Slack, Microsoft Teams, and WebPush.
   * Preference Management Console: A critical enterprise feature is the user-facing console. It empowers employees to choose how and where they receive specific types of alerts, significantly reducing the "noise" of corporate
     communications and increasing the likelihood that critical messages are seen.

  5. Operational Scalability
   * Scheduled Monitoring: Beyond reactive API triggers, Bitcaster includes Agents that can actively monitor external systems and databases, triggering notifications automatically when specific business conditions are met.
   * High Performance: Designed as a cloud-native Python/Django application, it is built to handle the high volume of signals generated by large-scale enterprise microservices and legacy systems alike.

# More Information

See the [Glossary](./glossary/index.md) for a list of common Bitcaster terminology

!!! hint

    To help you to novigate this documentation use the `Set Address` link on the header.
    All the links to in the pages will reflect your server address for a better user experience.

    **No data are sent outside your Browser**
