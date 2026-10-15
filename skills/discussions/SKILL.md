---
name: discussions
description: Forum threads on Regent's Phoenix and Ash sites — a question or post and its replies, likes, view counts, a marked answer and reply filters — rendered with the shared Regent.Discussion component and stored in the site's own Ash resources. Use when adding or changing a discussion, question-and-answer or forum page, a like button on posts, a view count, a "Solved" answer, or agent tools that read or like posts.
---

# Discussions

**Load `ash-stack` first, then `ash-data` for the tables.** Patchbay's discussion page is the
reference (Patchbay v146; agent likes on its `discussion-layout` branch). The look is
shared; the records are the site's own.

## The look: `Regent.Discussion`

Render every thread with `Regent.Discussion` from the design system (`regent_ui`), never a
copy of its markup. `thread` holds the title, the Solved mark, the reply, view and like counts
and the Compact replies switch; `post` is the opening post (`opening`) or a reply, with the
author's picture in its `avatar` slot, `solved` and `actions` slots; `solved` quotes the marked
answer under the question; `replies` holds the filters, the list and its empty line; `like` is
the heart; `label` marks Solution or the site's own replies. CONSUMERS.md in the design system
has the attributes. Import `../vendor/regent_ui/discussion.mjs` once from `app.ts` so the
Compact replies choice is remembered. See it at `/showcase/discussion`.

The site supplies the words for times (`RegentFormat.relative_time/2`), the pictures, the
addresses and the like press: `phx-click` with the post's id on a LiveView page, or the
product's own form around `like` with `type="submit"` on a controller page, which also works
without JavaScript.

## The records

1. **Posts and replies are the site's.** A thread has an opening post and ordered replies.
   A reply may be marked as the answer by the person who asked; show it as their word, not a
   check.
2. **Likes: one per person per post.** A like names its thread, and its reply when it is on a
   reply (none for the opening post), and the profile that gave it. Give it an identity on
   `[author_profile_id, thread_id, reply_id]` with `nils_distinct?: false`, so the opening
   post's like, whose reply is nil, still counts once. Liking is an upsert on that identity
   with `upsert_fields([])`, so liking again changes nothing; taking it back is a destroy the
   policy allows only for the like's own author. Liking needs a signed-in actor, because a
   like is given under a name. Likes rank nothing and verify nothing.
3. **Views: one per reader per thread.** Record the reader the server knows, the signed-in
   profile or a session id the server issued, never a value from the request, with an
   identity on `[thread_id, viewer]` and the same no-op upsert. A reload, a like or a reply
   never counts again.
4. **Counts are aggregates** on the thread (`count :view_count, :views`,
   `count :like_count, :likes`) and the post, loaded with the page, not stored columns.
5. **Show who liked it**: load each post's likes oldest first with their authors and pass the
   first three to `like` as `likers`, the rest as `others`.
6. **Filters are links** (`?replies=all|solution|…`), so each view has its own address and
   works without JavaScript.

## Agents

Give agents the same actions the page uses, as tools and HTTP: read a thread with its replies
and each post's `liked_by` (profile id and name, oldest first), `like_post` and `unlike_post`.
The agent acts under its own profile, so the same one-like rule holds.

## Tables

Follow `ash-data`. After `mix ash.codegen`, delete any `prefix: "public"` it wrote into the new
tables' references before committing: the site's tables live in its own schema, and a public
prefix fails the release migration (Patchbay, 2026-09-30). Likes are what people wrote;
consider them for the protected tables list.

## Checks

- Two presses of the heart by the same person leave one like; pressing again takes it back.
- A second visit by the same reader leaves the view count unchanged.
- The page on a phone: pictures shrink, Compact replies hides them, and the heart keeps a
  44px press target.
